/**
 * Device ownership, loss, and recovery — for both ownership modes, which C6's
 * acceptance asks for by name.
 *
 * The two modes are not symmetric and the tests are written to hold that line: a
 * vitrea-owned device re-requests itself, while an app-owned one reports the loss
 * and **waits**, because the app owns the resources that would have to be
 * re-registered and WebGPU has no cross-device sharing.
 *
 * The fake device is two members wide — `lost` and `destroy` — which is the whole
 * surface this module touches. A loss test that needed a real adapter would only
 * run where an adapter exists, and the machines where device loss actually happens
 * are not the machines running the suite.
 */

import { describe, expect, it, vi } from "vitest";

import { createDeviceHost } from "../src/device";
import { RendererError } from "../src/errors";

interface FakeDevice {
  readonly device: GPUDevice;
  lose(reason: GPUDeviceLostReason): void;
  readonly destroyed: () => boolean;
}

function fakeDevice(): FakeDevice {
  let resolve: (info: GPUDeviceLostInfo) => void = () => undefined;
  const lost = new Promise<GPUDeviceLostInfo>((r) => {
    resolve = r;
  });
  let destroyed = false;
  const device = {
    lost,
    destroy: () => {
      destroyed = true;
    },
  } as unknown as GPUDevice;
  return {
    device,
    lose: (reason) => resolve({ reason, message: "test" } as GPUDeviceLostInfo),
    destroyed: () => destroyed,
  };
}

const flush = async (): Promise<void> => {
  await Promise.resolve();
  await Promise.resolve();
  await Promise.resolve();
};

describe("before anything is attached", () => {
  it('reports "not-requested" rather than a fault', () => {
    // X2's K1 amendment (Decision Log #21c): a root that never asked for WebGPU
    // is not broken. Reporting "unavailable" here would make every CSS-by-choice
    // root read as demoted.
    const host = createDeviceHost();
    expect(host.status.webgpu).toBe("not-requested");
    expect(host.capabilityInput).toEqual({ webgpu: "not-requested", deviceHealth: "ok" });
  });

  it("throws a typed error rather than handing out an undefined device", () => {
    const host = createDeviceHost();
    expect(() => host.requireDevice()).toThrowError(RendererError);
    try {
      host.requireDevice();
    } catch (error) {
      expect((error as RendererError).code).toBe("device-unavailable");
    }
  });

  it('moves to "unavailable" only once an attempt actually failed', () => {
    const host = createDeviceHost();
    host.markUnavailable("no-adapter");
    expect(host.capabilityInput.webgpu).toBe("unavailable");
    expect(host.status.unavailableReason).toBe("no-adapter");
  });
});

describe("a vitrea-owned device", () => {
  it("publishes available and bumps the generation on attach", () => {
    const statuses: string[] = [];
    const host = createDeviceHost({ onStatusChange: (s) => statuses.push(s.webgpu) });
    const fake = fakeDevice();

    host.attach(fake.device, "vitrea");

    expect(host.status.webgpu).toBe("available");
    expect(host.status.generation).toBe(1);
    expect(host.requireDevice()).toBe(fake.device);
    expect(statuses).toEqual(["available"]);
  });

  it("tears down, re-requests, and comes back on a new generation", async () => {
    const first = fakeDevice();
    const second = fakeDevice();
    const teardown = vi.fn();

    const host = createDeviceHost({ reacquire: async () => second.device });
    host.addTeardownHook(teardown);
    host.attach(first.device, "vitrea");

    first.lose("unknown");
    await flush();
    await host.settled();

    expect(teardown).toHaveBeenCalledTimes(1);
    expect(host.status.deviceHealth).toBe("ok");
    expect(host.status.device).toBe(second.device);
    expect(host.status.generation).toBe(2);
    expect(host.status.replacementPending).toBe(false);
  });

  it("keeps webgpu available across the loss, so the fault stays recoverable", async () => {
    // core only raises `device-lost` when `webgpu` is available — "a device can
    // only be lost if there was one to lose". Clearing it would collapse a
    // recoverable fault into `no-webgpu`, whose honest recovery is "none".
    const fake = fakeDevice();
    const host = createDeviceHost();
    host.attach(fake.device, "vitrea");

    fake.lose("unknown");
    await flush();

    expect(host.capabilityInput).toEqual({ webgpu: "available", deviceHealth: "lost" });
  });

  it("does not re-request after our own destroy", async () => {
    const reacquire = vi.fn(async () => fakeDevice().device);
    const fake = fakeDevice();
    const host = createDeviceHost({ reacquire });
    host.attach(fake.device, "vitrea");

    fake.lose("destroyed");
    await flush();
    await host.settled();

    expect(reacquire).not.toHaveBeenCalled();
  });

  it("destroys the device it requested", () => {
    const fake = fakeDevice();
    const host = createDeviceHost();
    host.attach(fake.device, "vitrea");
    host.destroy();
    expect(fake.destroyed()).toBe(true);
  });

  it("destroys a replacement that arrives after the host was torn down", async () => {
    // A `destroy()` landing while the re-request is in flight still has to
    // account for what the re-request produced. Abandoning it leaks a whole
    // GPUDevice on the one path where this module IS the owner, and the host has
    // no handle to it — it never learned the reacquire had finished.
    const first = fakeDevice();
    const replacement = fakeDevice();
    let handOver: (() => void) | undefined;
    const arrival = new Promise<void>((resolve) => {
      handOver = resolve;
    });

    const host = createDeviceHost({
      reacquire: async () => {
        await arrival;
        return replacement.device;
      },
    });
    host.attach(first.device, "vitrea");

    first.lose("unknown");
    await flush();

    host.destroy();
    handOver?.();
    await host.settled();

    expect(replacement.destroyed()).toBe(true);
    expect(host.status.device).toBeUndefined();
  });
});

describe("an app-owned device", () => {
  it("reports the loss and waits for the app's replacement", async () => {
    const fake = fakeDevice();
    const onReplacementNeeded = vi.fn();
    const teardown = vi.fn();
    const reacquire = vi.fn(async () => fakeDevice().device);

    const host = createDeviceHost({ onReplacementNeeded, reacquire });
    host.addTeardownHook(teardown);
    host.attach(fake.device, "app");

    fake.lose("unknown");
    await flush();

    expect(teardown).toHaveBeenCalledTimes(1);
    expect(onReplacementNeeded).toHaveBeenCalledTimes(1);
    // Never re-requests: the app owns the resources that would need re-registering.
    expect(reacquire).not.toHaveBeenCalled();
    expect(host.status.replacementPending).toBe(true);
    expect(host.status.device).toBeUndefined();
  });

  it("names the handshake in the error raised while it waits", async () => {
    const fake = fakeDevice();
    const host = createDeviceHost();
    host.attach(fake.device, "app");
    fake.lose("unknown");
    await flush();

    expect(() => host.requireDevice()).toThrowError(/replaceDevice/);
  });

  it("recovers on replaceDevice and keeps app ownership", async () => {
    const fake = fakeDevice();
    const replacement = fakeDevice();
    const host = createDeviceHost();
    host.attach(fake.device, "app");
    fake.lose("unknown");
    await flush();

    host.replaceDevice(replacement.device);

    expect(host.status.ownership).toBe("app");
    expect(host.status.deviceHealth).toBe("ok");
    expect(host.status.replacementPending).toBe(false);
    expect(host.status.generation).toBe(2);
  });

  it("never destroys a device it was only lent", () => {
    const fake = fakeDevice();
    const host = createDeviceHost();
    host.attach(fake.device, "app");
    host.destroy();
    expect(fake.destroyed()).toBe(false);
  });
});

describe("teardown discipline", () => {
  it("runs every hook even when one throws", async () => {
    // Half-torn-down state after a device loss is the one condition from which
    // nothing can recover.
    const order: string[] = [];
    const fake = fakeDevice();
    const host = createDeviceHost();

    host.addTeardownHook(() => {
      order.push("first");
      throw new Error("boom");
    });
    host.addTeardownHook(() => order.push("second"));

    fake.lose("unknown");
    host.attach(fake.device, "vitrea");
    fake.lose("unknown");
    await flush();

    expect(order).toEqual(["first", "second"]);
  });

  it("lets a hook unsubscribe", async () => {
    const hook = vi.fn();
    const fake = fakeDevice();
    const host = createDeviceHost();
    const off = host.addTeardownHook(hook);
    off();
    host.attach(fake.device, "vitrea");

    fake.lose("unknown");
    await flush();

    expect(hook).not.toHaveBeenCalled();
  });

  it("ignores a loss from a superseded generation", async () => {
    const first = fakeDevice();
    const second = fakeDevice();
    const teardown = vi.fn();

    const host = createDeviceHost();
    host.addTeardownHook(teardown);
    host.attach(first.device, "vitrea");
    host.attach(second.device, "vitrea");

    first.lose("unknown");
    await flush();

    expect(teardown).not.toHaveBeenCalled();
    expect(host.status.device).toBe(second.device);
    expect(host.status.deviceHealth).toBe("ok");
  });
});
