import { run } from "./diag.mjs";
const R = "/Users/new/Developer/GitHub/designer/packages/calibration/profiles/";
const cases = [["dark-solid","rrect-md"],["checkerboard","rrect-md"],["photo","rrect-md"],["photo","rrect-lg"],
  ["dark-solid","capsule-button"],["checkerboard","capsule-button"],["photo","capsule-button"],
  ["mid-dark-solid","capsule-button"],["impulse","capsule-button"]];
const f = (x,n=4) => (x===undefined?"-":x.toFixed(n));
for (const [prof, scale] of [["apple-macos-26.5-1x-dark-standard","1x"],["apple-macos-26.5-1x-dark-standard","2x"],
                             ["apple-macos-26.5-1x-light-standard","1x"]]) {
  console.log(`\n== ${prof}`);
  console.log("scene".padEnd(32),"bgLin  bgEnc  k      target nominal alpha  tint   clamp X      gpuBody form     span     cssA_now tintN cssBody_now | cssA_fix tintF cssBody_fix");
  for (const r of run(R+prof+".json", scale, cases)) {
    console.log(r.scene.padEnd(32), f(r.bgLin,4), f(r.bgEnc,4), f(r.k,3), f(r.target,4), f(r.nominal,4),
      f(r.alpha,4), f(r.tint,4), (r.clamped?"YES ":"no  "), f(r.X,4), f(r.gpuBody,4), r.form.padEnd(8),
      f(r.spanNow,5), (r.degenerate?"DEGEN":"     "), f(r.cssAlphaNow,4), String(r.cssTintNow).padStart(4),
      f(r.cssNow,4), " |", f(r.cssAlphaFixed,4), String(r.cssTintFixed).padStart(4), f(r.cssFixed,4));
  }
}
