/**
 * The WebGPU lifecycle: capability probe, device request, loss detection.
 *
 * This module deliberately stops at the device. C6 owns the resource graph, the
 * passes and the `BackdropFrame` protocol (X3); what lives here is the part of
 * the story that is about the *browser* — whether there is an adapter at all,
 * getting a device, and noticing when it goes away. The device travels to C6 as
 * data, and the capability facts travel to core as data.
 *
 * Two contract points from §GPU device ownership and Decision Log #19:
 *
 * - **Loss demotes, then recovery runs.** A vitrea-owned device re-requests
 *   automatically; the affected groups carry `demotionReason: "device-lost"`
 *   until it completes. An app-owned device needs a replacement-device callback
 *   plus C6's resource re-registration handshake, so this module reports the loss
 *   and waits rather than inventing a device the app did not give it.
 * - **`no-webgpu` recovery is `"none"`.** Honestly unrecoverable within a
 *   session: a user enabling support means a new session. So an absent adapter is
 *   probed once and not retried on a timer.
 */

/** Ownership, per §GPU device ownership. Default is vitrea-owned. */
export type DeviceOwnership = "vitrea" | "app";

export interface WebGPUStatus {
  /** An adapter *and* a device were obtained. This is core's `PlatformProbe.webgpu`. */
  readonly available: boolean;
  readonly deviceHealth: "ok" | "lost";
  readonly ownership: DeviceOwnership;
  readonly device: GPUDevice | undefined;
  /** Why there is no device, in a form a dev-mode message can use. */
  readonly unavailableReason?: "no-navigator-gpu" | "no-adapter" | "device-request-failed";
}

export interface WebGPULifecycleOptions {
  /**
   * An app-owned device. Given one, this module never requests its own — and on
   * loss it waits for `onReplacementNeeded` rather than re-requesting, because
   * the app owns the resources that would have to be re-registered.
   */
  readonly device?: GPUDevice;
  readonly powerPreference?: GPUPowerPreference;
  readonly onStatusChange: (status: WebGPUStatus) => void;
  /** Called when an app-owned device is lost and only the app can replace it. */
  readonly onReplacementNeeded?: () => void;
  readonly navigatorGpu?: GPU | undefined;
}

export interface WebGPULifecycle {
  readonly status: WebGPUStatus;
  /** Probe and acquire. Safe to call once; later calls resolve to the current status. */
  start(): Promise<WebGPUStatus>;
  /** Hand in a replacement for a lost app-owned device. */
  replaceDevice(device: GPUDevice): void;
  destroy(): void;
}

/** Cheap and synchronous: is there a GPU object at all? Necessary, not sufficient. */
export function hasWebGPU(gpu: GPU | undefined = navigator.gpu): boolean {
  return gpu !== undefined;
}

export function createWebGPULifecycle(options: WebGPULifecycleOptions): WebGPULifecycle {
  const gpu = options.navigatorGpu ?? navigator.gpu;
  const ownership: DeviceOwnership = options.device === undefined ? "vitrea" : "app";

  let status: WebGPUStatus = {
    available: false,
    deviceHealth: "ok",
    ownership,
    device: undefined,
  };
  let destroyed = false;
  let started: Promise<WebGPUStatus> | undefined;

  const publish = (next: WebGPUStatus): WebGPUStatus => {
    status = next;
    if (!destroyed) options.onStatusChange(status);
    return status;
  };

  const watchLoss = (device: GPUDevice): void => {
    void device.lost.then((info) => {
      if (destroyed) return;
      publish({ ...status, available: false, deviceHealth: "lost", device: undefined });

      if (ownership === "app") {
        options.onReplacementNeeded?.();
        return;
      }
      // A vitrea-owned device re-requests itself. `info.reason === "destroyed"`
      // is our own teardown, which is not a fault to recover from.
      if (info.reason !== "destroyed") void acquire();
    });
  };

  const acquire = async (): Promise<WebGPUStatus> => {
    if (gpu === undefined) {
      return publish({ ...status, available: false, unavailableReason: "no-navigator-gpu" });
    }

    const adapter = await gpu.requestAdapter(
      options.powerPreference === undefined ? {} : { powerPreference: options.powerPreference },
    );
    if (adapter === null) {
      return publish({ ...status, available: false, unavailableReason: "no-adapter" });
    }

    try {
      const device = await adapter.requestDevice();
      if (destroyed) {
        device.destroy();
        return status;
      }
      watchLoss(device);
      return publish({ available: true, deviceHealth: "ok", ownership, device });
    } catch {
      return publish({ ...status, available: false, unavailableReason: "device-request-failed" });
    }
  };

  return {
    get status() {
      return status;
    },

    start() {
      started ??= (async () => {
        if (options.device !== undefined) {
          watchLoss(options.device);
          return publish({
            available: true,
            deviceHealth: "ok",
            ownership: "app",
            device: options.device,
          });
        }
        return acquire();
      })();
      return started;
    },

    replaceDevice(device) {
      watchLoss(device);
      publish({ available: true, deviceHealth: "ok", ownership, device });
    },

    destroy() {
      destroyed = true;
      // Only a device this module requested is ours to destroy.
      if (ownership === "vitrea") status.device?.destroy();
    },
  };
}
