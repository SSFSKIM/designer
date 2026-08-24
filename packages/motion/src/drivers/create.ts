import type { DriverConfig, MotionDriver } from "../driver";

import { EaseDriver } from "./ease";
import { ExponentialDriver } from "./exponential";
import { LowPassHysteresisDriver } from "./low-pass";
import { SpringDriver } from "./spring";
import { StepDriver } from "./step";
import { ThresholdCrossfadeDriver } from "./threshold-crossfade";

/**
 * Build the driver a config names.
 *
 * Eight table rows map onto six classes: `interruptible-spring` and
 * `critically-damped` are one spring at different ζ, and `step` and
 * `hysteresis-cooldown` are one discrete channel at different band and dwell.
 * The distinction stays in the table because it is the table that states which
 * channels are allowed to overshoot.
 */
export function createDriver(config: DriverConfig, initialValue: number): MotionDriver {
  switch (config.kind) {
    case "interruptible-spring":
    case "critically-damped":
      return new SpringDriver(config, initialValue);
    case "attack-decay":
      return new ExponentialDriver(config, initialValue);
    case "low-pass-hysteresis":
      return new LowPassHysteresisDriver(config, initialValue);
    case "threshold-crossfade":
      return new ThresholdCrossfadeDriver(config, initialValue);
    case "monotonic-ease":
      return new EaseDriver(config, initialValue);
    case "step":
    case "hysteresis-cooldown":
      return new StepDriver(config, initialValue);
  }
}
