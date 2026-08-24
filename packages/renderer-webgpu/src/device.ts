/**
 * Device ownership, loss teardown, and rebuild (§GPU device ownership).
 *
 * `platform-web` owns the *browser* half of the story — is there an adapter, get
 * a device, notice when it goes away. This module owns the *resource* half: what
 * has to be thrown away when a device dies, when it is safe to build again, and
 * what core's capability inputs should read while that is in flight.
 *
 * ## The two ownership modes, and why they are not symmetric
 *
 * - **vitrea-owned** — this module can re-request a device by itself, so loss is
 *   a transient it recovers from: tear down, re-request, re-attach, rebuild.
 *   Every backdrop source is re-imported on the next frame because loss marks
 *   them all dirty, which routes recovery through the same
 *   one-rebuild-per-dirty-source-per-frame path a content change takes rather
 *   than through a special case.
 * - **app-owned** — the app owns the resources that would have to be
 *   re-registered, so this module reports the loss, raises
 *   `replacementPending`, and **waits**. Groups stay demoted until
 *   `replaceDevice` arrives and the re-registration handshake completes. Inventing
 *   a device the app did not give us would break the one guarantee app-ownership
 *   exists for: that every texture the renderer samples came from the app's own
 *   device, because WebGPU has no cross-device sharing.
 *
 * `info.reason === "destroyed"` is our own teardown and is not recovered from —
 * re-requesting there would resurrect a renderer the host just destroyed.
 *
 * ## Generations
 *
 * Every attach bumps a generation counter, and every GPU object this package
 * holds is tagged with the generation it was made under. A resource from a lost
 * device is unusable forever, and the failure mode is silent — bindings simply
 * produce nothing — so "is this from the current device" has to be a cheap
 * integer comparison somewhere. It is here.
 */

import { rendererError } from "./errors";

/**
 * Structurally identical to `@vitrea/core`'s `WebGPUAvailability` (X2's K1
 * amendment, Decision Log #21c). Declared here rather than imported because this
 * package sits *below* core in the dependency graph — core reaches the renderer
 * through a dynamic import, so an import back would close a cycle. A test pins
 * the two unions to the same members.
 */
export type WebGPUAvailability = "not-requested" | "unavailable" | "available";

export type DeviceOwnership = "vitrea" | "app";

export interface RendererDeviceStatus {
  /** Feeds core's `PlatformProbe.webgpu` unchanged. */
  readonly webgpu: WebGPUAvailability;
  readonly deviceHealth: "ok" | "lost";
  readonly ownership: DeviceOwnership;
  readonly device: GPUDevice | undefined;
  /** Bumped on every attach. Tags every resource built under it. */
  readonly generation: number;
  /** True while an app-owned device is lost and no replacement has arrived. */
  readonly replacementPending: boolean;
  /** Why there is no device, when there is a reason worth reporting. */
  readonly unavailableReason?: "no-adapter" | "device-request-failed" | "lost";
}

/** The capability facts a host folds into core's `PlatformProbe`. */
export interface DeviceCapabilityInput {
  readonly webgpu: WebGPUAvailability;
  readonly deviceHealth: "ok" | "lost";
}

/** Run on loss and on teardown. Must be idempotent and must not touch the device. */
export type TeardownHook = () => void;

export interface DeviceHostOptions {
  readonly onStatusChange?: (status: RendererDeviceStatus) => void;
  /** Raised when an app-owned device is lost and only the app can replace it. */
  readonly onReplacementNeeded?: () => void;
  /**
   * Re-request a vitrea-owned device. Absent means "no automatic recovery",
   * which is the honest configuration when the host owns the adapter handshake.
   */
  readonly reacquire?: () => Promise<GPUDevice | undefined>;
}

export interface DeviceHost {
  readonly status: RendererDeviceStatus;
  readonly capabilityInput: DeviceCapabilityInput;
  /** The current device, or a thrown `device-unavailable` if there is none. */
  requireDevice(): GPUDevice;
  attach(device: GPUDevice, ownership: DeviceOwnership): void;
  /** Hand in a replacement for a lost device. Also clears `replacementPending`. */
  replaceDevice(device: GPUDevice): void;
  /**
   * Record that WebGPU *was* asked for and could not be had. Moves `webgpu` off
   * `"not-requested"`, which is the difference K1 exists to preserve.
   */
  markUnavailable(reason: "no-adapter" | "device-request-failed"): void;
  addTeardownHook(hook: TeardownHook): () => void;
  /** Awaits the in-flight recovery, if any. Test and shutdown seam. */
  settled(): Promise<void>;
  destroy(): void;
}

export function createDeviceHost(options: DeviceHostOptions = {}): DeviceHost {
  let status: RendererDeviceStatus = {
    webgpu: "not-requested",
    deviceHealth: "ok",
    ownership: "vitrea",
    device: undefined,
    generation: 0,
    replacementPending: false,
  };
  const hooks = new Set<TeardownHook>();
  let destroyed = false;
  let recovery: Promise<void> | undefined;

  const publish = (next: RendererDeviceStatus): void => {
    status = next;
    if (!destroyed) options.onStatusChange?.(status);
  };

  const runTeardown = (): void => {
    // A hook that throws must not stop the others: half-torn-down state after a
    // device loss is the one condition from which nothing can recover.
    for (const hook of [...hooks]) {
      try {
        hook();
      } catch {
        // Deliberately swallowed — see above.
      }
    }
  };

  const watchLoss = (device: GPUDevice, generation: number): void => {
    void device.lost.then((info) => {
      // A loss from a superseded device is not this device's loss.
      if (destroyed || status.generation !== generation) return;

      runTeardown();
      const ownership = status.ownership;
      publish({
        webgpu: "available",
        deviceHealth: "lost",
        ownership,
        device: undefined,
        generation,
        replacementPending: ownership === "app",
        unavailableReason: "lost",
      });

      if (info.reason === "destroyed") return;

      if (ownership === "app") {
        options.onReplacementNeeded?.();
        return;
      }

      const reacquire = options.reacquire;
      if (reacquire === undefined) return;
      recovery = (async () => {
        const replacement = await reacquire();
        if (destroyed || replacement === undefined) return;
        attach(replacement, "vitrea");
      })();
    });
  };

  function attach(device: GPUDevice, ownership: DeviceOwnership): void {
    const generation = status.generation + 1;
    publish({
      webgpu: "available",
      deviceHealth: "ok",
      ownership,
      device,
      generation,
      replacementPending: false,
    });
    watchLoss(device, generation);
  }

  return {
    get status() {
      return status;
    },

    get capabilityInput() {
      return { webgpu: status.webgpu, deviceHealth: status.deviceHealth };
    },

    requireDevice() {
      const { device } = status;
      if (device === undefined) {
        throw rendererError(
          "device-unavailable",
          status.replacementPending
            ? "The app-owned GPUDevice was lost and no replacement has been handed in yet. Call replaceDevice() and re-register the app's texture views before drawing again."
            : "No GPUDevice is attached. Attach one (platform-web's WebGPU lifecycle produces it) before building resources or drawing.",
        );
      }
      return device;
    },

    attach,

    replaceDevice(device) {
      attach(device, status.ownership);
    },

    markUnavailable(reason) {
      publish({
        ...status,
        webgpu: "unavailable",
        device: undefined,
        unavailableReason: reason,
      });
    },

    addTeardownHook(hook) {
      hooks.add(hook);
      return () => hooks.delete(hook);
    },

    async settled() {
      await recovery;
    },

    destroy() {
      destroyed = true;
      runTeardown();
      // Only a device this renderer owns is ours to destroy.
      if (status.ownership === "vitrea") status.device?.destroy();
      hooks.clear();
      status = { ...status, device: undefined };
    },
  };
}
