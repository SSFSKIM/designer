/** W47 G0(f): the narrow tap reuses the measured chain+residual plan, not a new pass shape. */
import { heavyTapPlan, planPyramid } from "../../../../renderer-webgpu/src/pyramid-plan";
for (const scale of [1, 2]) {
  const plan = planPyramid(320 * scale, 200 * scale, {scale: 1, maxDimension: 4096});
  for (const sigmaCss of [2, 3, 4, 6]) {
    console.log(JSON.stringify({scale, sigmaCss, ...heavyTapPlan(sigmaCss * scale, plan)}));
  }
}
