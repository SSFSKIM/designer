# W31 G0 — the chromatic cut (claims §5.161 §3)

Ratio (i) is `sqrt(sd(a)² + sd(b)²) / interiorStdDev` of one image's masked
interior, per side. Ratio (ii) is that side's mean per-pixel OKLab chroma over the
RAW backdrop's under the same mask. `web/native` on ratio (i) is the wave's
statistic: 1.000 would be vitrea reading the reference's chroma-to-structure, and it
is never read against 1.

Ratio (iii) is the side's mean per-pixel chroma against a backdrop blurred to that
side's OWN measured structure — a body that only blurred reads 1. It comes from a
second pass over the same captures (`blurred-reference.sh`) and is absent where the
reference radius is outside the 64 device px searched, which is itself a reading:
the side is flatter than any blur in that range leaves.

`cond` is `adopted-thresholds.test.ts`'s conditioning predicate evaluated on the
row's own shape axis. A refused cell is TABLED, not dropped — `mask-adequacy.txt`
is the evidence that the refusal is the shape axis's and does not reach this one.

## `checkerboard`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | dark | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.020 | 0.000 | 0.000 | **0.000** | 49825.658 | 1.110 | — | — | 0.1926 / 0.1715 / 0.5003 |
| 26.5 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.447 | 0.315 | 0.000 | **0.704** | 9178697.167 | 9392220.337 | — | — | 0.4385 / 0.4274 / 0.5000 |
| 26.5 | dark | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.020 | 0.000 | 0.000 | **0.000** | 49825.658 | 1.096 | — | — | 0.1926 / 0.1711 / 0.5003 |
| 26.5 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.447 | 0.281 | 0.000 | **0.629** | 9178697.167 | 9366158.509 | — | — | 0.4385 / 0.4282 / 0.5000 |
| 26.5 | dark | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.019 | 0.000 | 0.000 | **0.000** | 46046.899 | 1.110 | — | — | 0.1938 / 0.1715 / 0.5003 |
| 26.5 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.420 | 0.371 | 0.000 | **0.883** | 9185554.498 | 9394433.153 | — | — | 0.4399 / 0.4277 / 0.5001 |
| 26.5 | dark | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.019 | 0.000 | 0.000 | **0.000** | 46046.899 | 1.096 | — | — | 0.1938 / 0.1709 / 0.5003 |
| 26.5 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.420 | 0.324 | 0.000 | **0.770** | 9185554.498 | 9377122.612 | — | — | 0.4399 / 0.4285 / 0.5001 |
| 26.5 | light | increased-contrast | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.001 | 0.000 | 0.000 | **0.000** | 1146.429 | 1.843 | — | — | 0.7300 / 0.7834 / 0.5002 |
| 26.5 | light | increased-contrast | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.267 | 0.308 | 0.000 | **1.152** | 9354639.204 | 8925903.593 | — | — | 0.3981 / 0.4520 / 0.5000 |
| 26.5 | light | increased-contrast | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.001 | 0.000 | 0.000 | **0.000** | 1146.429 | 1.756 | — | — | 0.7300 / 0.7432 / 0.5002 |
| 26.5 | light | increased-contrast | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.267 | 0.310 | 0.000 | **1.159** | 9354639.204 | 8931552.172 | — | — | 0.3981 / 0.4503 / 0.5000 |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-blue | yes | validation | ok | 0.010 | 0.000 | 0.000 | **0.000** | 35495.941 | 1.559 | — | — | 0.4513 / 0.4735 / 0.5000 |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.010 | 0.000 | 0.000 | **0.000** | 35495.941 | 1.559 | — | — | 0.4513 / 0.4735 / 0.5000 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-blue | yes | validation | ok | 0.398 | 0.483 | 0.000 | **1.212** | 10350326.088 | 10405570.767 | — | — | 0.2064 / 0.2065 / 0.5000 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.302 | 0.367 | 0.000 | **1.214** | 8812316.061 | 8910616.252 | — | — | 0.3603 / 0.3674 / 0.5000 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-blue | yes | validation | ok | 0.010 | 0.000 | 0.000 | **0.000** | 35495.941 | 1.553 | — | — | 0.4513 / 0.4734 / 0.5000 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.010 | 0.000 | 0.000 | **0.000** | 35495.941 | 1.553 | — | — | 0.4513 / 0.4734 / 0.5000 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-blue | yes | validation | ok | 0.398 | 0.307 | 0.000 | **0.771** | 10350326.088 | 10392337.870 | — | — | 0.2064 / 0.2117 / 0.5000 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.302 | 0.195 | 0.000 | **0.644** | 8812316.061 | 8921901.364 | — | — | 0.3603 / 0.3727 / 0.5000 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-blue | yes | validation | ok | 0.008 | 0.000 | 0.000 | **0.000** | 22339.204 | 1.558 | — | — | 0.4532 / 0.4735 / 0.5002 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.008 | 0.000 | 0.000 | **0.000** | 22339.204 | 1.558 | — | — | 0.4532 / 0.4735 / 0.5002 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-blue | yes | validation | ok | 0.371 | 0.456 | 0.000 | **1.229** | 10354448.135 | 10407717.613 | — | — | 0.2072 / 0.2065 / 0.5002 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.289 | 0.329 | 0.000 | **1.141** | 8817485.065 | 8911437.073 | — | — | 0.3609 / 0.3675 / 0.5002 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-blue | yes | validation | ok | 0.008 | 0.000 | 0.000 | **0.000** | 22339.204 | 1.551 | — | — | 0.4532 / 0.4738 / 0.5002 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.008 | 0.000 | 0.000 | **0.000** | 22339.204 | 1.551 | — | — | 0.4532 / 0.4738 / 0.5002 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-blue | yes | validation | ok | 0.371 | 0.319 | 0.000 | **0.859** | 10354448.135 | 10419132.210 | — | — | 0.2072 / 0.2119 / 0.5002 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.289 | 0.210 | 0.000 | **0.729** | 8817485.065 | 8941483.667 | — | — | 0.3609 / 0.3738 / 0.5002 |
| 27 | dark | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.019 | 0.000 | 0.000 | **0.000** | 43832.054 | 1.365 | — | — | 0.2841 / 0.3182 / 0.5002 |
| 27 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.378 | 0.403 | 0.000 | **1.064** | 9050816.656 | 9393006.004 | — | — | 0.4413 / 0.4275 / 0.5000 |
| 27 | dark | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.019 | 0.000 | 0.000 | **0.000** | 43832.054 | 1.357 | — | — | 0.2841 / 0.3174 / 0.5002 |
| 27 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.378 | 0.285 | 0.000 | **0.754** | 9050816.656 | 9363855.032 | — | — | 0.4413 / 0.4290 / 0.5000 |
| 27 | dark | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.022 | 0.000 | 0.000 | **0.000** | 43357.401 | 1.365 | — | — | 0.2921 / 0.3184 / 0.5002 |
| 27 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.379 | 0.490 | 0.000 | **1.294** | 9063445.394 | 9395000.672 | — | — | 0.4420 / 0.4277 / 0.5001 |
| 27 | dark | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.022 | 0.000 | 0.000 | **0.000** | 43357.401 | 1.357 | — | — | 0.2921 / 0.3175 / 0.5002 |
| 27 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.379 | 0.304 | 0.000 | **0.801** | 9063445.394 | 9377612.397 | — | — | 0.4420 / 0.4281 / 0.5001 |
| 27 | light | increased-contrast | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.002 | 0.000 | 0.000 | **0.000** | 523.307 | 1.843 | — | — | 0.6934 / 0.7832 / 0.5000 |
| 27 | light | increased-contrast | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.310 | 0.308 | 0.000 | **0.994** | 9256572.330 | 8925897.037 | — | — | 0.4131 / 0.4520 / 0.5000 |
| 27 | light | increased-contrast | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.002 | 0.000 | 0.000 | **0.000** | 523.307 | 1.756 | — | — | 0.6934 / 0.7429 / 0.5000 |
| 27 | light | increased-contrast | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.310 | 0.310 | 0.000 | **1.000** | 9256572.330 | 8928444.141 | — | — | 0.4131 / 0.4502 / 0.5000 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-blue | yes | validation | ok | 0.017 | 0.000 | 0.000 | **0.000** | 24291.955 | 1.488 | — | — | 0.3849 / 0.4126 / 0.5003 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.017 | 0.000 | 0.000 | **0.000** | 24291.955 | 1.488 | — | — | 0.3849 / 0.4126 / 0.5003 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-blue | yes | validation | ok | 0.249 | 0.626 | 0.000 | **2.508** | 10507943.589 | 10361240.139 | — | — | 0.2011 / 0.1946 / 0.5000 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.164 | 0.418 | 0.000 | **2.557** | 8877321.433 | 8809107.052 | — | — | 0.3583 / 0.3511 / 0.5000 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-blue | yes | validation | ok | 0.017 | 0.000 | 0.000 | **0.000** | 24291.955 | 1.483 | — | — | 0.3849 / 0.4133 / 0.5003 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.017 | 0.000 | 0.000 | **0.000** | 24291.955 | 1.483 | — | — | 0.3849 / 0.4133 / 0.5003 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-blue | yes | validation | ok | 0.249 | 0.341 | 0.000 | **1.365** | 10507943.589 | 10358980.205 | — | — | 0.2011 / 0.1999 / 0.5000 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.164 | 0.181 | 0.000 | **1.110** | 8877321.433 | 8806748.135 | — | — | 0.3583 / 0.3541 / 0.5000 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-blue | yes | validation | ok | 0.023 | 0.000 | 0.000 | **0.000** | 30126.902 | 1.488 | — | — | 0.3799 / 0.4126 / 0.5004 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.023 | 0.000 | 0.000 | **0.000** | 30126.902 | 1.488 | — | — | 0.3799 / 0.4126 / 0.5004 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-blue | yes | validation | ok | 0.270 | 0.584 | 0.000 | **2.162** | 10512771.310 | 10366606.546 | — | — | 0.2024 / 0.1945 / 0.5000 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.177 | 0.415 | 0.000 | **2.350** | 8888504.298 | 8812443.319 | — | — | 0.3602 / 0.3511 / 0.5000 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-blue | yes | validation | ok | 0.023 | 0.000 | 0.000 | **0.000** | 30126.902 | 1.479 | — | — | 0.3799 / 0.4133 / 0.5004 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.023 | 0.000 | 0.000 | **0.000** | 30126.902 | 1.479 | — | — | 0.3799 / 0.4133 / 0.5004 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-blue | yes | validation | ok | 0.270 | 0.336 | 0.000 | **1.246** | 10512771.310 | 10383898.141 | — | — | 0.2024 / 0.1998 / 0.5000 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.177 | 0.188 | 0.000 | **1.063** | 8888504.298 | 8825213.776 | — | — | 0.3602 / 0.3553 / 0.5000 |

## `checkerboard-32`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.477 | 0.235 | 0.000 | **0.493** | 9179580.040 | 9391806.003 | — | — | 0.4384 / 0.4272 / 0.5000 |
| 26.5 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.477 | 0.291 | 0.000 | **0.610** | 9179580.040 | 9366858.639 | — | — | 0.4384 / 0.4283 / 0.5000 |
| 26.5 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.441 | 0.243 | 0.000 | **0.549** | 9187526.950 | 9394145.475 | — | — | 0.4403 / 0.4276 / 0.5001 |
| 26.5 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.441 | 0.338 | 0.000 | **0.765** | 9187526.950 | 9377726.887 | — | — | 0.4403 / 0.4285 / 0.5001 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.280 | 0.373 | 0.000 | **1.333** | 8810963.611 | 8910453.441 | — | — | 0.3609 / 0.3671 / 0.5000 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.280 | 0.183 | 0.000 | **0.655** | 8810963.611 | 8918480.763 | — | — | 0.3609 / 0.3725 / 0.5000 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.270 | 0.334 | 0.000 | **1.238** | 8819988.944 | 8911305.358 | — | — | 0.3615 / 0.3673 / 0.5002 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.270 | 0.192 | 0.000 | **0.712** | 8819988.944 | 8930514.660 | — | — | 0.3615 / 0.3732 / 0.5002 |
| 27 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.386 | 0.298 | 0.000 | **0.770** | 9056366.298 | 9392828.017 | — | — | 0.4418 / 0.4273 / 0.5000 |
| 27 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.386 | 0.291 | 0.000 | **0.753** | 9056366.298 | 9364272.581 | — | — | 0.4418 / 0.4290 / 0.5000 |
| 27 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.386 | 0.302 | 0.000 | **0.783** | 9065633.830 | 9394848.201 | — | — | 0.4427 / 0.4276 / 0.5001 |
| 27 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.386 | 0.311 | 0.000 | **0.805** | 9065633.830 | 9377977.935 | — | — | 0.4427 / 0.4281 / 0.5001 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.160 | 0.398 | 0.000 | **2.486** | 8872553.025 | 8808972.474 | — | — | 0.3580 / 0.3508 / 0.5000 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.160 | 0.176 | 0.000 | **1.102** | 8872553.025 | 8797551.678 | — | — | 0.3580 / 0.3546 / 0.5000 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.170 | 0.399 | 0.000 | **2.351** | 8877857.926 | 8812321.434 | — | — | 0.3592 / 0.3510 / 0.5000 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.170 | 0.176 | 0.000 | **1.038** | 8877857.926 | 8817509.962 | — | — | 0.3592 / 0.3547 / 0.5000 |

## `checkerboard-4`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.446 | 0.363 | 0.000 | **0.814** | 9181197.761 | 9392383.464 | — | — | 0.4383 / 0.4274 / 0.5000 |
| 26.5 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.446 | 0.280 | 0.000 | **0.628** | 9181197.761 | 9365945.289 | — | — | 0.4383 / 0.4283 / 0.5000 |
| 26.5 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.419 | 0.346 | 0.000 | **0.828** | 9188914.466 | 9394379.890 | — | — | 0.4399 / 0.4277 / 0.5001 |
| 26.5 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.419 | 0.330 | 0.000 | **0.788** | 9188914.466 | 9377118.907 | — | — | 0.4399 / 0.4286 / 0.5001 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.355 | 0.420 | 0.000 | **1.184** | 8813470.390 | 8910734.607 | — | — | 0.3598 / 0.3675 / 0.5000 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.355 | 0.224 | 0.000 | **0.631** | 8813470.390 | 8930461.510 | — | — | 0.3598 / 0.3728 / 0.5000 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.324 | 0.357 | 0.000 | **1.100** | 8816840.611 | 8911194.122 | — | — | 0.3603 / 0.3675 / 0.5002 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.324 | 0.245 | 0.000 | **0.754** | 8816840.611 | 8977633.214 | — | — | 0.3603 / 0.3775 / 0.5002 |
| 27 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.373 | 0.465 | 0.000 | **1.247** | 9027217.119 | 9393076.973 | — | — | 0.4426 / 0.4275 / 0.5000 |
| 27 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.373 | 0.285 | 0.000 | **0.763** | 9027217.119 | 9363724.831 | — | — | 0.4426 / 0.4290 / 0.5000 |
| 27 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.375 | 0.437 | 0.000 | **1.165** | 9050536.408 | 9394918.901 | — | — | 0.4427 / 0.4277 / 0.5001 |
| 27 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.375 | 0.307 | 0.000 | **0.818** | 9050536.408 | 9377637.599 | — | — | 0.4427 / 0.4282 / 0.5001 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.164 | 0.565 | 0.000 | **3.445** | 8841510.705 | 8809228.394 | — | — | 0.3532 / 0.3512 / 0.5000 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.164 | 0.220 | 0.000 | **1.344** | 8841510.705 | 8808109.075 | — | — | 0.3532 / 0.3544 / 0.5000 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.176 | 0.585 | 0.000 | **3.323** | 8868759.865 | 8812489.688 | — | — | 0.3574 / 0.3511 / 0.5000 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.176 | 0.206 | 0.000 | **1.170** | 8868759.865 | 8856865.871 | — | — | 0.3574 / 0.3590 / 0.5000 |

## `checkerboard-64`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.373 | 0.223 | 0.000 | **0.598** | 7935383.557 | 8124599.310 | — | — | 0.4375 / 0.4271 / 0.5780 |
| 26.5 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.373 | 0.238 | 0.000 | **0.638** | 7935383.557 | 8098047.287 | — | — | 0.4375 / 0.4259 / 0.5780 |
| 26.5 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.382 | 0.231 | 0.000 | **0.604** | 7917209.320 | 8115103.268 | — | — | 0.4408 / 0.4275 / 0.5789 |
| 26.5 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.382 | 0.292 | 0.000 | **0.763** | 7917209.320 | 8099022.070 | — | — | 0.4408 / 0.4274 / 0.5789 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.284 | 0.375 | 0.000 | **1.324** | 7612589.363 | 7690381.030 | — | — | 0.3585 / 0.3625 / 0.5780 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.284 | 0.171 | 0.000 | **0.604** | 7612589.363 | 7764809.791 | — | — | 0.3585 / 0.3786 / 0.5780 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.268 | 0.336 | 0.000 | **1.254** | 7646457.973 | 7680925.260 | — | — | 0.3651 / 0.3627 / 0.5789 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.268 | 0.182 | 0.000 | **0.678** | 7646457.973 | 7765024.504 | — | — | 0.3651 / 0.3799 / 0.5789 |
| 27 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.320 | 0.284 | 0.000 | **0.888** | 7805143.079 | 8125252.571 | — | — | 0.4416 / 0.4273 / 0.5780 |
| 27 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.320 | 0.233 | 0.000 | **0.728** | 7805143.079 | 8098634.418 | — | — | 0.4416 / 0.4266 / 0.5780 |
| 27 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.348 | 0.292 | 0.000 | **0.841** | 7802406.651 | 8115383.748 | — | — | 0.4430 / 0.4276 / 0.5789 |
| 27 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.348 | 0.254 | 0.000 | **0.730** | 7802406.651 | 8100278.194 | — | — | 0.4430 / 0.4270 / 0.5789 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.159 | 0.402 | 0.000 | **2.537** | 7682716.214 | 7567279.207 | — | — | 0.3615 / 0.3446 / 0.5780 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.159 | 0.171 | 0.000 | **1.077** | 7682716.214 | 7659492.715 | — | — | 0.3615 / 0.3601 / 0.5780 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.162 | 0.390 | 0.000 | **2.410** | 7679827.800 | 7562429.161 | — | — | 0.3626 / 0.3448 / 0.5786 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.162 | 0.166 | 0.000 | **1.023** | 7679827.800 | 7668869.154 | — | — | 0.3626 / 0.3615 / 0.5786 |

## `checkerboard-8`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.436 | 0.636 | 0.000 | **1.457** | 9180573.892 | 9392635.966 | — | — | 0.4388 / 0.4276 / 0.5000 |
| 26.5 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.436 | 0.279 | 0.000 | **0.638** | 9180573.892 | 9365624.795 | — | — | 0.4388 / 0.4283 / 0.5000 |
| 26.5 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.418 | 0.496 | 0.000 | **1.185** | 9195791.521 | 9394506.299 | — | — | 0.4400 / 0.4277 / 0.5001 |
| 26.5 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.418 | 0.323 | 0.000 | **0.773** | 9195791.521 | 9376792.285 | — | — | 0.4400 / 0.4286 / 0.5001 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.315 | 0.375 | 0.000 | **1.191** | 8809724.715 | 8910843.668 | — | — | 0.3599 / 0.3677 / 0.5000 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.315 | 0.210 | 0.000 | **0.667** | 8809724.715 | 8926945.697 | — | — | 0.3599 / 0.3726 / 0.5000 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.324 | 0.335 | 0.000 | **1.036** | 8815383.146 | 8911259.520 | — | — | 0.3602 / 0.3675 / 0.5002 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.324 | 0.236 | 0.000 | **0.729** | 8815383.146 | 8954762.149 | — | — | 0.3602 / 0.3752 / 0.5002 |
| 27 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.377 | 0.984 | 0.000 | **2.610** | 9040701.313 | 9393243.248 | — | — | 0.4419 / 0.4277 / 0.5000 |
| 27 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.377 | 0.284 | 0.000 | **0.752** | 9040701.313 | 9363392.080 | — | — | 0.4419 / 0.4290 / 0.5000 |
| 27 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.378 | 0.620 | 0.000 | **1.640** | 9058659.091 | 9394984.884 | — | — | 0.4423 / 0.4277 / 0.5001 |
| 27 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.378 | 0.303 | 0.000 | **0.801** | 9058659.091 | 9377429.985 | — | — | 0.4423 / 0.4281 / 0.5001 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.164 | 0.499 | 0.000 | **3.048** | 8863242.652 | 8809293.719 | — | — | 0.3561 / 0.3513 / 0.5000 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.164 | 0.193 | 0.000 | **1.176** | 8863242.652 | 8807919.079 | — | — | 0.3561 / 0.3544 / 0.5000 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.175 | 0.453 | 0.000 | **2.583** | 8880188.037 | 8812519.332 | — | — | 0.3590 / 0.3512 / 0.5000 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.175 | 0.194 | 0.000 | **1.105** | 8880188.037 | 8836878.882 | — | — | 0.3590 / 0.3567 / 0.5000 |

## `dark-solid`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | dark | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.255 | 0.000 | — | **0.000** | 0.454 | 0.000 | — | — | 0.0370 / 0.0369 / 0.0117 |
| 26.5 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.355 | 0.282 | — | **0.795** | 45.703 | 45.768 | — | — | 0.4257 / 0.4276 / 0.0117 |
| 26.5 | dark | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.255 | 0.313 | — | **1.229** | 0.454 | 0.000 | — | — | 0.0370 / 0.0369 / 0.0117 |
| 26.5 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.355 | 0.387 | — | **1.091** | 45.703 | 45.711 | — | — | 0.4257 / 0.4317 / 0.0117 |
| 26.5 | dark | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.223 | — | — | **—** | 0.453 | 0.000 | — | — | 0.0370 / 0.0369 / 0.0117 |
| 26.5 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.370 | 0.327 | — | **0.884** | 45.754 | 45.790 | — | — | 0.4276 / 0.4281 / 0.0117 |
| 26.5 | dark | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.223 | — | — | **—** | 0.453 | 0.000 | — | — | 0.0370 / 0.0369 / 0.0117 |
| 26.5 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.370 | 0.397 | — | **1.073** | 45.754 | 45.757 | — | — | 0.4276 / 0.4326 / 0.0117 |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.255 | 0.000 | — | **0.000** | 0.454 | 0.000 | — | — | 0.0370 / 0.0369 / 0.0117 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-blue | yes | holdout | ok | 0.520 | 0.524 | — | **1.007** | 53.341 | 53.474 | — | — | 0.2404 / 0.2404 / 0.0117 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.355 | 0.282 | — | **0.794** | 45.703 | 45.768 | — | — | 0.4257 / 0.4276 / 0.0117 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.255 | 0.313 | — | **1.229** | 0.454 | 0.000 | — | — | 0.0370 / 0.0369 / 0.0117 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-blue | yes | holdout | ok | 0.520 | 0.451 | — | **0.866** | 53.341 | 53.141 | — | — | 0.2404 / 0.2451 / 0.0117 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.355 | 0.387 | — | **1.091** | 45.703 | 45.711 | — | — | 0.4257 / 0.4317 / 0.0117 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.223 | — | — | **—** | 0.453 | 0.000 | — | — | 0.0370 / 0.0369 / 0.0117 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-blue | yes | holdout | ok | 0.471 | 0.492 | — | **1.043** | 53.361 | 53.503 | — | — | 0.2422 / 0.2407 / 0.0117 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.370 | 0.327 | — | **0.883** | 45.754 | 45.790 | — | — | 0.4276 / 0.4280 / 0.0117 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.223 | — | — | **—** | 0.453 | 0.000 | — | — | 0.0370 / 0.0369 / 0.0117 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-blue | yes | holdout | ok | 0.471 | 0.428 | — | **0.908** | 53.361 | 53.185 | — | — | 0.2422 / 0.2456 / 0.0117 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.370 | 0.397 | — | **1.073** | 45.754 | 45.757 | — | — | 0.4276 / 0.4326 / 0.0117 |
| 27 | dark | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.074 | 0.058 | — | **0.787** | 0.856 | 0.000 | — | — | 0.0684 / 0.0466 / 0.0117 |
| 27 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.303 | 0.236 | — | **0.780** | 45.165 | 45.787 | — | — | 0.4302 / 0.4270 / 0.0117 |
| 27 | dark | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.074 | 0.117 | — | **1.595** | 0.856 | 0.001 | — | — | 0.0684 / 0.0466 / 0.0117 |
| 27 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.303 | 0.223 | — | **0.736** | 45.165 | 45.654 | — | — | 0.4302 / 0.4256 / 0.0117 |
| 27 | dark | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.057 | 0.085 | — | **1.499** | 0.860 | 0.000 | — | — | 0.0685 / 0.0466 / 0.0117 |
| 27 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.328 | 0.237 | — | **0.722** | 45.215 | 45.808 | — | — | 0.4317 / 0.4274 / 0.0117 |
| 27 | dark | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.057 | 0.138 | — | **2.439** | 0.860 | 0.001 | — | — | 0.0685 / 0.0466 / 0.0117 |
| 27 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.328 | 0.227 | — | **0.694** | 45.215 | 45.731 | — | — | 0.4317 / 0.4263 / 0.0117 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-blue | yes | holdout | ok | 0.010 | 0.016 | — | **1.613** | 0.397 | 0.001 | — | — | 0.1860 / 0.2343 / 0.0117 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.010 | 0.016 | — | **1.613** | 0.397 | 0.001 | — | — | 0.1860 / 0.2343 / 0.0117 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-blue | yes | holdout | ok | 0.142 | 1.229 | — | **8.659** | 48.824 | 46.918 | — | — | 0.1572 / 0.1582 / 0.0117 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.159 | 0.506 | — | **3.190** | 40.375 | 39.936 | — | — | 0.2813 / 0.2856 / 0.0117 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-blue | yes | holdout | ok | 0.010 | 0.013 | — | **1.307** | 0.397 | 0.002 | — | — | 0.1860 / 0.2338 / 0.0117 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.010 | 0.013 | — | **1.307** | 0.397 | 0.002 | — | — | 0.1860 / 0.2338 / 0.0117 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-blue | yes | holdout | ok | 0.142 | 0.393 | — | **2.769** | 48.824 | 47.652 | — | — | 0.1572 / 0.1661 / 0.0117 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.159 | 0.224 | — | **1.411** | 40.375 | 40.245 | — | — | 0.2813 / 0.2922 / 0.0117 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-blue | yes | holdout | ok | 0.010 | 0.023 | — | **2.334** | 0.396 | 0.001 | — | — | 0.1870 / 0.2344 / 0.0117 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.010 | 0.023 | — | **2.334** | 0.396 | 0.001 | — | — | 0.1870 / 0.2344 / 0.0117 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-blue | yes | holdout | ok | 0.167 | 0.932 | — | **5.566** | 48.800 | 46.939 | — | — | 0.1578 / 0.1582 / 0.0117 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.158 | 0.483 | — | **3.061** | 40.382 | 39.951 | — | — | 0.2820 / 0.2858 / 0.0117 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-blue | yes | holdout | ok | 0.010 | 0.013 | — | **1.283** | 0.396 | 0.001 | — | — | 0.1870 / 0.2342 / 0.0117 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.010 | 0.013 | — | **1.283** | 0.396 | 0.001 | — | — | 0.1870 / 0.2342 / 0.0117 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-blue | yes | holdout | ok | 0.167 | 0.361 | — | **2.157** | 48.800 | 47.656 | — | — | 0.1578 / 0.1657 / 0.0117 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.158 | 0.205 | — | **1.299** | 40.382 | 40.271 | — | — | 0.2820 / 0.2924 / 0.0117 |

## `hc-text`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | holdout | ok | 0.311 | 0.419 | 0.000 | **1.348** | 7373392.933 | 7610518.492 | — | — | 0.3709 / 0.3980 / 0.6026 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | holdout | ok | 0.311 | 0.220 | 0.000 | **0.707** | 7373392.933 | 7500375.467 | — | — | 0.3709 / 0.3883 / 0.6026 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | holdout | ok | 0.309 | 0.396 | 0.000 | **1.281** | 7370749.815 | 7609202.165 | — | — | 0.3703 / 0.3979 / 0.6029 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | holdout | ok | 0.309 | 0.242 | 0.000 | **0.781** | 7370749.815 | 7513074.716 | — | — | 0.3703 / 0.3885 / 0.6029 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | holdout | ok | 0.019 | 0.000 | 0.000 | **0.000** | 15005.765 | 1.283 | — | — | 0.4256 / 0.4626 / 0.6026 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | holdout | ok | 0.197 | 0.444 | 0.000 | **2.254** | 7448221.903 | 7527823.798 | — | — | 0.3735 / 0.3890 / 0.6026 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | holdout | ok | 0.019 | 0.000 | 0.000 | **0.000** | 15005.765 | 1.273 | — | — | 0.4256 / 0.4552 / 0.6026 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | holdout | ok | 0.197 | 0.195 | 0.000 | **0.989** | 7448221.903 | 7433167.623 | — | — | 0.3735 / 0.3743 / 0.6026 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | holdout | ok | 0.019 | 0.000 | 0.000 | **0.000** | 12523.608 | 1.282 | — | — | 0.4263 / 0.4623 / 0.6029 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | holdout | ok | 0.208 | 0.428 | 0.000 | **2.061** | 7455308.038 | 7526551.942 | — | — | 0.3755 / 0.3889 / 0.6029 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | holdout | ok | 0.019 | 0.000 | 0.000 | **0.000** | 12523.608 | 1.267 | — | — | 0.4263 / 0.4521 / 0.6029 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | holdout | ok | 0.208 | 0.200 | 0.000 | **0.965** | 7455308.038 | 7448513.424 | — | — | 0.3755 / 0.3747 / 0.6029 |

## `impulse`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.467 | — | 0.000 | **—** | 11589767.139 | 93.635 | — | — | 0.0259 / 0.0307 / 0.0033 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.330 | 0.255 | 0.000 | **0.772** | 1427375444.710 | 1429461672.376 | — | — | 0.4254 / 0.4275 / 0.0033 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.467 | 0.000 | 0.000 | **0.000** | 11589767.139 | 93.708 | — | — | 0.0259 / 0.0308 / 0.0033 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.330 | 0.365 | 0.000 | **1.103** | 1427375444.710 | 1427585054.567 | — | — | 0.4254 / 0.4313 / 0.0033 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.443 | — | 0.000 | **—** | 13249968.589 | 94.086 | — | — | 0.0258 / 0.0307 / 0.0033 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.353 | 0.300 | 0.000 | **0.851** | 1426661190.121 | 1427836136.860 | — | — | 0.4274 / 0.4280 / 0.0033 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.443 | 0.000 | 0.000 | **0.000** | 13249968.589 | 94.356 | — | — | 0.0258 / 0.0310 / 0.0033 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.353 | 0.388 | 0.000 | **1.099** | 1426661190.121 | 1426768605.914 | — | — | 0.4274 / 0.4324 / 0.0033 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.056 | 0.000 | 0.000 | **0.000** | 11743853.473 | 180.382 | — | — | 0.1467 / 0.2120 / 0.0033 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.161 | 0.420 | 0.000 | **2.612** | 1235673070.279 | 1231630101.773 | — | — | 0.2647 / 0.2723 / 0.0033 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.056 | 0.000 | 0.000 | **0.000** | 11743853.473 | 180.507 | — | — | 0.1467 / 0.2127 / 0.0033 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.161 | 0.206 | 0.000 | **1.280** | 1235673070.279 | 1242524994.794 | — | — | 0.2647 / 0.2803 / 0.0033 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.068 | 0.000 | 0.000 | **0.000** | 11855435.957 | 180.587 | — | — | 0.1473 / 0.2121 / 0.0033 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.157 | 0.409 | 0.000 | **2.611** | 1234700661.614 | 1230848846.753 | — | — | 0.2654 / 0.2725 / 0.0033 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.068 | 0.000 | 0.000 | **0.000** | 11855435.957 | 180.888 | — | — | 0.1473 / 0.2134 / 0.0033 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.157 | 0.195 | 0.000 | **1.242** | 1234700661.614 | 1242112020.978 | — | — | 0.2654 / 0.2805 / 0.0033 |

## `light-solid`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.024 | 0.049 | — | **2.053** | 0.409 | 0.005 | — | — | 0.7326 / 0.7091 / 0.8910 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.367 | 0.413 | — | **1.125** | 26.169 | 26.335 | — | — | 0.4319 / 0.4282 / 0.8910 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.024 | 0.038 | — | **1.589** | 0.409 | 0.004 | — | — | 0.7326 / 0.7091 / 0.8910 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.367 | 0.358 | — | **0.977** | 26.169 | 26.258 | — | — | 0.4319 / 0.4310 / 0.8910 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.025 | 0.052 | — | **2.100** | 0.409 | 0.002 | — | — | 0.7323 / 0.7087 / 0.8910 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.378 | 0.415 | — | **1.099** | 26.184 | 26.344 | — | — | 0.4317 / 0.4280 / 0.8910 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.025 | 0.038 | — | **1.519** | 0.409 | 0.002 | — | — | 0.7323 / 0.7087 / 0.8910 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.378 | 0.380 | — | **1.008** | 26.184 | 26.290 | — | — | 0.4317 / 0.4302 / 0.8910 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.021 | 0.040 | — | **1.858** | 0.417 | 0.005 | — | — | 0.6437 / 0.6383 / 0.8910 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.374 | 0.397 | — | **1.059** | 26.064 | 26.171 | — | — | 0.4184 / 0.4210 / 0.8910 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.021 | 0.033 | — | **1.559** | 0.417 | 0.004 | — | — | 0.6437 / 0.6384 / 0.8910 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.374 | 0.443 | — | **1.184** | 26.064 | 26.174 | — | — | 0.4184 / 0.4223 / 0.8910 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.020 | 0.039 | — | **1.955** | 0.414 | 0.002 | — | — | 0.6443 / 0.6380 / 0.8910 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.378 | 0.398 | — | **1.051** | 26.063 | 26.180 | — | — | 0.4190 / 0.4208 / 0.8910 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.020 | 0.030 | — | **1.473** | 0.414 | 0.002 | — | — | 0.6443 / 0.6380 / 0.8910 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.378 | 0.440 | — | **1.163** | 26.063 | 26.211 | — | — | 0.4190 / 0.4217 / 0.8910 |

## `mid-chroma-solid`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | dark | standard | 1x | dom | 44 | inactive | — | probe | ok | 0.762 | 1.248 | — | **1.638** | 0.755 | 0.555 | — | — | 0.0984 / 0.0422 / 0.2141 |
| 26.5 | dark | standard | 1x | dom | 44 | inactive-tint-orange | yes | probe | ok | 1.678 | 13.021 | — | **7.759** | 0.627 | 0.004 | — | — | 0.1082 / 0.0741 / 0.2141 |
| 26.5 | dark | standard | 1x | dom | 96 | inactive | — | probe | ok | 0.776 | 1.408 | — | **1.814** | 0.743 | 0.548 | — | — | 0.0939 / 0.0390 / 0.2141 |
| 26.5 | dark | standard | 1x | dom | 160 | inactive | — | probe | ok | 0.753 | 1.402 | — | **1.863** | 0.743 | 0.547 | — | — | 0.0939 / 0.0388 / 0.2141 |
| 26.5 | dark | standard | 1x | texture | 44 | inactive | — | probe | ok | 0.762 | 2.025 | — | **2.659** | 0.755 | 0.396 | — | — | 0.0984 / 0.0374 / 0.2141 |
| 26.5 | dark | standard | 1x | texture | 44 | inactive-tint-orange | yes | probe | ok | 1.678 | 10.620 | — | **6.328** | 0.627 | 0.006 | — | — | 0.1082 / 0.0743 / 0.2141 |
| 26.5 | dark | standard | 1x | texture | 96 | inactive | — | probe | ok | 0.776 | 1.741 | — | **2.244** | 0.743 | 0.407 | — | — | 0.0939 / 0.0321 / 0.2141 |
| 26.5 | dark | standard | 1x | texture | 160 | inactive | — | probe | ok | 0.753 | 1.548 | — | **2.057** | 0.743 | 0.406 | — | — | 0.0939 / 0.0320 / 0.2141 |
| 26.5 | dark | standard | 2x | dom | 44 | inactive | — | probe | ok | 0.751 | 1.257 | — | **1.674** | 0.754 | 0.554 | — | — | 0.0981 / 0.0417 / 0.2141 |
| 26.5 | dark | standard | 2x | dom | 44 | inactive-tint-orange | yes | probe | ok | 1.617 | 12.566 | — | **7.770** | 0.626 | 0.002 | — | — | 0.1080 / 0.0742 / 0.2141 |
| 26.5 | dark | standard | 2x | dom | 96 | inactive | — | probe | ok | 0.754 | 1.335 | — | **1.771** | 0.743 | 0.546 | — | — | 0.0938 / 0.0386 / 0.2141 |
| 26.5 | dark | standard | 2x | dom | 160 | inactive | — | probe | ok | 0.748 | 1.327 | — | **1.775** | 0.743 | 0.546 | — | — | 0.0938 / 0.0385 / 0.2141 |
| 26.5 | dark | standard | 2x | texture | 44 | inactive | — | probe | ok | 0.751 | 2.015 | — | **2.683** | 0.754 | 0.394 | — | — | 0.0981 / 0.0372 / 0.2141 |
| 26.5 | dark | standard | 2x | texture | 44 | inactive-tint-orange | yes | probe | ok | 1.617 | 10.323 | — | **6.383** | 0.626 | 0.003 | — | — | 0.1080 / 0.0743 / 0.2141 |
| 26.5 | dark | standard | 2x | texture | 96 | inactive | — | probe | ok | 0.754 | 1.532 | — | **2.033** | 0.743 | 0.406 | — | — | 0.0938 / 0.0320 / 0.2141 |
| 26.5 | dark | standard | 2x | texture | 160 | inactive | — | probe | ok | 0.748 | 1.646 | — | **2.201** | 0.743 | 0.406 | — | — | 0.0938 / 0.0319 / 0.2141 |
| 26.5 | light | standard | 1x | dom | 44 | inactive | — | probe | ok | 0.522 | 0.568 | — | **1.089** | 0.539 | 0.659 | — | — | 0.4729 / 0.3868 / 0.2141 |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | probe | ok | 0.893 | 2.047 | — | **2.293** | 0.396 | 0.004 | — | — | 0.3265 / 0.3461 / 0.2141 |
| 26.5 | light | standard | 1x | dom | 96 | inactive | — | probe | ok | 0.454 | 0.447 | — | **0.986** | 0.583 | 0.551 | — | — | 0.5016 / 0.4807 / 0.2141 |
| 26.5 | light | standard | 1x | dom | 160 | inactive | — | probe | ok | 0.458 | 0.397 | — | **0.868** | 0.582 | 0.550 | — | — | 0.5020 / 0.4812 / 0.2141 |
| 26.5 | light | standard | 1x | texture | 44 | inactive | — | probe | ok | 0.522 | 0.684 | — | **1.311** | 0.539 | 0.438 | — | — | 0.4729 / 0.4310 / 0.2141 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | probe | ok | 0.893 | 1.311 | — | **1.469** | 0.396 | 0.005 | — | — | 0.3265 / 0.3455 / 0.2141 |
| 26.5 | light | standard | 1x | texture | 96 | inactive | — | probe | ok | 0.454 | 0.557 | — | **1.228** | 0.583 | 0.377 | — | — | 0.5016 / 0.5205 / 0.2141 |
| 26.5 | light | standard | 1x | texture | 160 | inactive | — | probe | ok | 0.458 | 0.566 | — | **1.236** | 0.582 | 0.376 | — | — | 0.5020 / 0.5210 / 0.2141 |
| 26.5 | light | standard | 2x | dom | 44 | inactive | — | probe | ok | 0.523 | 0.536 | — | **1.025** | 0.536 | 0.656 | — | — | 0.4744 / 0.3900 / 0.2141 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | probe | ok | 0.963 | 1.987 | — | **2.064** | 0.394 | 0.002 | — | — | 0.3274 / 0.3464 / 0.2141 |
| 26.5 | light | standard | 2x | dom | 96 | inactive | — | probe | ok | 0.457 | 0.375 | — | **0.821** | 0.582 | 0.550 | — | — | 0.5022 / 0.4816 / 0.2141 |
| 26.5 | light | standard | 2x | dom | 160 | inactive | — | probe | ok | 0.460 | 0.374 | — | **0.813** | 0.582 | 0.550 | — | — | 0.5024 / 0.4818 / 0.2141 |
| 26.5 | light | standard | 2x | texture | 44 | inactive | — | probe | ok | 0.523 | 0.680 | — | **1.302** | 0.536 | 0.436 | — | — | 0.4744 / 0.4319 / 0.2141 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | probe | ok | 0.963 | 1.313 | — | **1.364** | 0.394 | 0.002 | — | — | 0.3274 / 0.3462 / 0.2141 |
| 26.5 | light | standard | 2x | texture | 96 | inactive | — | probe | ok | 0.457 | 0.561 | — | **1.228** | 0.582 | 0.376 | — | — | 0.5022 / 0.5211 / 0.2141 |
| 26.5 | light | standard | 2x | texture | 160 | inactive | — | probe | ok | 0.460 | 0.557 | — | **1.211** | 0.582 | 0.376 | — | — | 0.5024 / 0.5213 / 0.2141 |
| 27 | dark | standard | 1x | dom | 44 | inactive | — | probe | ok | 0.685 | 2.628 | — | **3.834** | 1.040 | 0.473 | — | — | 0.2856 / 0.0718 / 0.2141 |
| 27 | dark | standard | 1x | dom | 44 | inactive-tint-orange | yes | probe | ok | 0.898 | 3.832 | — | **4.267** | 0.877 | 0.002 | — | — | 0.2439 / 0.1300 / 0.2141 |
| 27 | dark | standard | 1x | dom | 96 | inactive | — | probe | ok | 0.708 | 2.008 | — | **2.837** | 1.033 | 0.443 | — | — | 0.2727 / 0.0749 / 0.2141 |
| 27 | dark | standard | 1x | dom | 160 | inactive | — | probe | ok | 0.619 | 2.693 | — | **4.350** | 1.031 | 0.444 | — | — | 0.2691 / 0.0747 / 0.2141 |
| 27 | dark | standard | 1x | texture | 44 | inactive | — | probe | ok | 0.685 | 4.932 | — | **7.194** | 1.040 | 0.278 | — | — | 0.2856 / 0.0761 / 0.2141 |
| 27 | dark | standard | 1x | texture | 44 | inactive-tint-orange | yes | probe | ok | 0.898 | 9.992 | — | **11.127** | 0.877 | 0.003 | — | — | 0.2439 / 0.1300 / 0.2141 |
| 27 | dark | standard | 1x | texture | 96 | inactive | — | probe | ok | 0.708 | 4.072 | — | **5.752** | 1.033 | 0.266 | — | — | 0.2727 / 0.0770 / 0.2141 |
| 27 | dark | standard | 1x | texture | 160 | inactive | — | probe | ok | 0.619 | 3.070 | — | **4.960** | 1.031 | 0.266 | — | — | 0.2691 / 0.0770 / 0.2141 |
| 27 | dark | standard | 2x | dom | 44 | inactive | — | probe | ok | 0.637 | 2.626 | — | **4.122** | 1.040 | 0.474 | — | — | 0.2857 / 0.0717 / 0.2141 |
| 27 | dark | standard | 2x | dom | 44 | inactive-tint-orange | yes | probe | ok | 0.845 | 3.714 | — | **4.396** | 0.877 | 0.001 | — | — | 0.2440 / 0.1301 / 0.2141 |
| 27 | dark | standard | 2x | dom | 96 | inactive | — | probe | ok | 0.623 | 2.200 | — | **3.531** | 1.033 | 0.443 | — | — | 0.2727 / 0.0747 / 0.2141 |
| 27 | dark | standard | 2x | dom | 160 | inactive | — | probe | ok | 0.596 | 2.247 | — | **3.773** | 1.031 | 0.442 | — | — | 0.2690 / 0.0746 / 0.2141 |
| 27 | dark | standard | 2x | texture | 44 | inactive | — | probe | ok | 0.637 | 5.216 | — | **8.187** | 1.040 | 0.277 | — | — | 0.2857 / 0.0761 / 0.2141 |
| 27 | dark | standard | 2x | texture | 44 | inactive-tint-orange | yes | probe | ok | 0.845 | 8.951 | — | **10.594** | 0.877 | 0.001 | — | — | 0.2440 / 0.1301 / 0.2141 |
| 27 | dark | standard | 2x | texture | 96 | inactive | — | probe | ok | 0.623 | 2.561 | — | **4.110** | 1.033 | 0.266 | — | — | 0.2727 / 0.0770 / 0.2141 |
| 27 | dark | standard | 2x | texture | 160 | inactive | — | probe | ok | 0.596 | 2.575 | — | **4.323** | 1.031 | 0.266 | — | — | 0.2690 / 0.0770 / 0.2141 |
| 27 | light | standard | 1x | dom | 44 | inactive | — | probe | ok | 0.499 | 0.733 | — | **1.470** | 0.820 | 0.724 | — | — | 0.3762 / 0.3289 / 0.2141 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | probe | ok | 0.463 | 2.354 | — | **5.087** | 0.611 | 0.005 | — | — | 0.2270 / 0.3044 / 0.2141 |
| 27 | light | standard | 1x | dom | 44 | rest | — | probe | ok | 0.589 | 0.421 | — | **0.715** | 0.802 | 0.484 | — | — | 0.3851 / 0.5621 / 0.2141 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.153 | 2.254 | — | **14.735** | 0.500 | 0.532 | — | — | 0.2838 / 0.3510 / 0.2141 |
| 27 | light | standard | 1x | dom | 96 | inactive | — | probe | ok | 0.492 | 0.693 | — | **1.408** | 0.818 | 0.689 | — | — | 0.3772 / 0.3366 / 0.2141 |
| 27 | light | standard | 1x | dom | 96 | rest | — | probe | ok | 0.577 | 0.411 | — | **0.712** | 0.793 | 0.464 | — | — | 0.3890 / 0.5781 / 0.2141 |
| 27 | light | standard | 1x | dom | 160 | inactive | — | probe | ok | 0.436 | 0.558 | — | **1.280** | 0.818 | 0.689 | — | — | 0.3774 / 0.3370 / 0.2141 |
| 27 | light | standard | 1x | dom | 160 | rest | — | probe | ok | 0.474 | 0.364 | — | **0.767** | 0.779 | 0.469 | — | — | 0.3957 / 0.5743 / 0.2141 |
| 27 | light | standard | 1x | texture | 44 | inactive | — | probe | ok | 0.499 | 0.788 | — | **1.580** | 0.820 | 0.471 | — | — | 0.3762 / 0.3754 / 0.2141 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | probe | ok | 0.463 | 1.584 | — | **3.422** | 0.611 | 0.005 | — | — | 0.2270 / 0.3039 / 0.2141 |
| 27 | light | standard | 1x | texture | 44 | rest | — | probe | ok | 0.589 | 0.439 | — | **0.744** | 0.802 | 0.352 | — | — | 0.3851 / 0.5964 / 0.2141 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.153 | 0.907 | — | **5.930** | 0.500 | 0.534 | — | — | 0.2838 / 0.3537 / 0.2141 |
| 27 | light | standard | 1x | texture | 96 | inactive | — | probe | ok | 0.492 | 0.801 | — | **1.627** | 0.818 | 0.452 | — | — | 0.3772 / 0.3757 / 0.2141 |
| 27 | light | standard | 1x | texture | 96 | rest | — | probe | ok | 0.577 | 0.439 | — | **0.760** | 0.793 | 0.332 | — | — | 0.3890 / 0.6128 / 0.2141 |
| 27 | light | standard | 1x | texture | 160 | inactive | — | probe | ok | 0.436 | 0.746 | — | **1.710** | 0.818 | 0.451 | — | — | 0.3774 / 0.3759 / 0.2141 |
| 27 | light | standard | 1x | texture | 160 | rest | — | probe | ok | 0.474 | 0.423 | — | **0.891** | 0.779 | 0.332 | — | — | 0.3957 / 0.6134 / 0.2141 |
| 27 | light | standard | 2x | dom | 44 | inactive | — | probe | ok | 0.436 | 0.646 | — | **1.483** | 0.819 | 0.722 | — | — | 0.3768 / 0.3294 / 0.2141 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | probe | ok | 0.433 | 2.277 | — | **5.264** | 0.610 | 0.002 | — | — | 0.2276 / 0.3047 / 0.2141 |
| 27 | light | standard | 2x | dom | 44 | rest | — | probe | ok | 0.564 | 0.344 | — | **0.609** | 0.800 | 0.488 | — | — | 0.3859 / 0.5595 / 0.2141 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | probe | ok | 0.161 | 2.184 | — | **13.565** | 0.500 | 0.532 | — | — | 0.2844 / 0.3511 / 0.2141 |
| 27 | light | standard | 2x | dom | 96 | inactive | — | probe | ok | 0.416 | 0.478 | — | **1.149** | 0.818 | 0.689 | — | — | 0.3774 / 0.3373 / 0.2141 |
| 27 | light | standard | 2x | dom | 96 | rest | — | probe | ok | 0.510 | 0.320 | — | **0.627** | 0.793 | 0.464 | — | — | 0.3893 / 0.5776 / 0.2141 |
| 27 | light | standard | 2x | dom | 160 | inactive | — | probe | ok | 0.363 | 0.456 | — | **1.255** | 0.818 | 0.689 | — | — | 0.3775 / 0.3375 / 0.2141 |
| 27 | light | standard | 2x | dom | 160 | rest | — | probe | ok | 0.401 | 0.316 | — | **0.788** | 0.779 | 0.469 | — | — | 0.3958 / 0.5741 / 0.2141 |
| 27 | light | standard | 2x | texture | 44 | inactive | — | probe | ok | 0.436 | 0.795 | — | **1.825** | 0.819 | 0.470 | — | — | 0.3768 / 0.3759 / 0.2141 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | probe | ok | 0.433 | 1.583 | — | **3.658** | 0.610 | 0.003 | — | — | 0.2276 / 0.3044 / 0.2141 |
| 27 | light | standard | 2x | texture | 44 | rest | — | probe | ok | 0.564 | 0.430 | — | **0.762** | 0.800 | 0.350 | — | — | 0.3859 / 0.5976 / 0.2141 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | probe | ok | 0.161 | 0.788 | — | **4.895** | 0.500 | 0.533 | — | — | 0.2844 / 0.3538 / 0.2141 |
| 27 | light | standard | 2x | texture | 96 | inactive | — | probe | ok | 0.416 | 0.837 | — | **2.012** | 0.818 | 0.451 | — | — | 0.3774 / 0.3760 / 0.2141 |
| 27 | light | standard | 2x | texture | 96 | rest | — | probe | ok | 0.510 | 0.442 | — | **0.865** | 0.793 | 0.331 | — | — | 0.3893 / 0.6134 / 0.2141 |
| 27 | light | standard | 2x | texture | 160 | inactive | — | probe | ok | 0.363 | 0.781 | — | **2.150** | 0.818 | 0.451 | — | — | 0.3775 / 0.3760 / 0.2141 |
| 27 | light | standard | 2x | texture | 160 | rest | — | probe | ok | 0.401 | 0.431 | — | **1.076** | 0.779 | 0.331 | — | — | 0.3958 / 0.6136 / 0.2141 |

## `photo`

| os | scheme | a11y | scale | tier | span | pose | tint | set | cond | (i) native | (i) web | (i) backdrop | **web/native** | (ii) native | (ii) web | (iii) native | (iii) web | interior mean N/W/B |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26.5 | dark | standard | 1x | dom | 44 | inactive | — | calibration | ok | 3.966 | 4.014 | 1.386 | **1.012** | 0.550 | 0.364 | — | — | 0.1132 / 0.0917 / 0.2119 |
| 26.5 | dark | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | REFUSED | 2.525 | 2.729 | 1.391 | **1.081** | 0.375 | 0.004 | — | — | 0.1835 / 0.1529 / 0.2145 |
| 26.5 | dark | standard | 1x | dom | 44 | rest | — | calibration | ok | 2.191 | 5.015 | 1.386 | **2.288** | 0.580 | 0.411 | 0.909 | — | 0.1020 / 0.0568 / 0.2119 |
| 26.5 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.561 | 0.526 | 1.386 | **0.937** | 1.512 | 1.544 | — | — | 0.4384 / 0.4273 / 0.2119 |
| 26.5 | dark | standard | 1x | dom | 96 | inactive | — | calibration | ok | 6.573 | 6.626 | 1.389 | **1.008** | 0.635 | 0.463 | — | — | 0.0600 / 0.0497 / 0.2147 |
| 26.5 | dark | standard | 1x | dom | 96 | rest | — | calibration | ok | 4.898 | 7.302 | 1.389 | **1.491** | 0.587 | 0.483 | — | — | 0.0490 / 0.0402 / 0.2147 |
| 26.5 | dark | standard | 1x | dom | 128 | inactive | — | probe | ok | 5.567 | 6.088 | 1.381 | **1.094** | 0.652 | 0.471 | — | — | 0.0622 / 0.0501 / 0.2211 |
| 26.5 | dark | standard | 1x | dom | 160 | rest | — | holdout | ok | 5.648 | 7.289 | 1.400 | **1.290** | 0.532 | 0.484 | — | — | 0.0464 / 0.0402 / 0.2258 |
| 26.5 | dark | standard | 1x | texture | 44 | inactive | — | calibration | ok | 3.966 | 2.241 | 1.386 | **0.565** | 0.550 | 0.184 | — | — | 0.1132 / 0.0926 / 0.2119 |
| 26.5 | dark | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | REFUSED | 2.525 | 0.586 | 1.391 | **0.232** | 0.375 | 0.006 | — | — | 0.1835 / 0.1535 / 0.2145 |
| 26.5 | dark | standard | 1x | texture | 44 | rest | — | calibration | ok | 2.191 | 1.409 | 1.386 | **0.643** | 0.580 | 0.227 | 0.909 | 0.475 | 0.1020 / 0.0563 / 0.2119 |
| 26.5 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.561 | 0.874 | 1.386 | **1.556** | 1.512 | 1.541 | — | — | 0.4384 / 0.4277 / 0.2119 |
| 26.5 | dark | standard | 1x | texture | 96 | inactive | — | calibration | ok | 6.573 | 3.867 | 1.389 | **0.588** | 0.635 | 0.247 | — | — | 0.0600 / 0.0507 / 0.2147 |
| 26.5 | dark | standard | 1x | texture | 96 | rest | — | calibration | ok | 4.898 | 2.867 | 1.389 | **0.585** | 0.587 | 0.268 | — | — | 0.0490 / 0.0409 / 0.2147 |
| 26.5 | dark | standard | 1x | texture | 128 | inactive | — | probe | ok | 5.567 | 3.719 | 1.381 | **0.668** | 0.652 | 0.263 | — | — | 0.0622 / 0.0503 / 0.2211 |
| 26.5 | dark | standard | 1x | texture | 160 | rest | — | holdout | ok | 5.648 | 3.645 | 1.400 | **0.645** | 0.532 | 0.283 | — | — | 0.0464 / 0.0410 / 0.2258 |
| 26.5 | dark | standard | 2x | dom | 44 | inactive | — | calibration | ok | 3.942 | 4.360 | 1.378 | **1.106** | 0.571 | 0.366 | — | — | 0.1121 / 0.0913 / 0.2128 |
| 26.5 | dark | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | REFUSED | 2.413 | 2.739 | 1.385 | **1.135** | 0.390 | 0.002 | — | — | 0.1818 / 0.1529 / 0.2157 |
| 26.5 | dark | standard | 2x | dom | 44 | rest | — | calibration | ok | 2.198 | 5.142 | 1.378 | **2.339** | 0.589 | 0.434 | — | — | 0.1023 / 0.0559 / 0.2128 |
| 26.5 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.497 | 0.530 | 1.379 | **1.068** | 1.510 | 1.541 | — | — | 0.4395 / 0.4276 / 0.2128 |
| 26.5 | dark | standard | 2x | dom | 96 | inactive | — | calibration | ok | 6.639 | 6.257 | 1.388 | **0.942** | 0.631 | 0.496 | — | — | 0.0597 / 0.0490 / 0.2153 |
| 26.5 | dark | standard | 2x | dom | 96 | rest | — | calibration | ok | 4.758 | 6.991 | 1.388 | **1.469** | 0.593 | 0.502 | — | — | 0.0493 / 0.0400 / 0.2153 |
| 26.5 | dark | standard | 2x | dom | 128 | inactive | — | probe | ok | 5.656 | 5.805 | 1.381 | **1.026** | 0.650 | 0.496 | — | — | 0.0619 / 0.0497 / 0.2214 |
| 26.5 | dark | standard | 2x | dom | 160 | rest | — | holdout | ok | 5.581 | 7.055 | 1.401 | **1.264** | 0.534 | 0.499 | — | — | 0.0465 / 0.0402 / 0.2260 |
| 26.5 | dark | standard | 2x | texture | 44 | inactive | — | calibration | ok | 3.942 | 2.442 | 1.378 | **0.620** | 0.571 | 0.182 | — | — | 0.1121 / 0.0925 / 0.2128 |
| 26.5 | dark | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | REFUSED | 2.413 | 0.414 | 1.385 | **0.171** | 0.390 | 0.003 | — | — | 0.1818 / 0.1537 / 0.2157 |
| 26.5 | dark | standard | 2x | texture | 44 | rest | — | calibration | ok | 2.198 | 1.492 | 1.378 | **0.679** | 0.589 | 0.232 | — | — | 0.1023 / 0.0558 / 0.2128 |
| 26.5 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.497 | 0.723 | 1.379 | **1.457** | 1.510 | 1.539 | — | — | 0.4395 / 0.4280 / 0.2128 |
| 26.5 | dark | standard | 2x | texture | 96 | inactive | — | calibration | ok | 6.639 | 3.736 | 1.388 | **0.563** | 0.631 | 0.256 | — | — | 0.0597 / 0.0509 / 0.2153 |
| 26.5 | dark | standard | 2x | texture | 96 | rest | — | calibration | ok | 4.758 | 2.857 | 1.388 | **0.601** | 0.593 | 0.278 | — | — | 0.0493 / 0.0410 / 0.2153 |
| 26.5 | dark | standard | 2x | texture | 128 | inactive | — | probe | ok | 5.656 | 3.708 | 1.381 | **0.656** | 0.650 | 0.271 | — | — | 0.0619 / 0.0503 / 0.2214 |
| 26.5 | dark | standard | 2x | texture | 160 | rest | — | holdout | ok | 5.581 | 3.588 | 1.401 | **0.643** | 0.534 | 0.291 | — | — | 0.0465 / 0.0410 / 0.2260 |
| 26.5 | light | increased-contrast | 1x | dom | 44 | inactive | — | calibration | ok | 0.063 | 0.222 | 1.386 | **3.520** | 0.018 | 0.036 | — | — | 0.9316 / 0.9610 / 0.2119 |
| 26.5 | light | increased-contrast | 1x | dom | 44 | inactive | — | validation | ok | 0.068 | 0.244 | 1.070 | **3.563** | 0.031 | 0.047 | — | — | 0.9000 / 0.9033 / 0.2536 |
| 26.5 | light | increased-contrast | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.070 | 0.420 | 1.386 | **5.962** | 0.014 | 0.002 | — | — | 0.7297 / 0.7832 / 0.2119 |
| 26.5 | light | increased-contrast | 1x | dom | 44 | rest | — | calibration | ok | 0.051 | 0.329 | 1.386 | **6.460** | 0.043 | 0.053 | — | — | 0.9183 / 0.9162 / 0.2119 |
| 26.5 | light | increased-contrast | 1x | dom | 44 | rest | — | validation | ok | 0.055 | 0.336 | 1.070 | **6.073** | 0.059 | 0.067 | — | — | 0.8792 / 0.9080 / 0.2536 |
| 26.5 | light | increased-contrast | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.274 | 0.309 | 1.386 | **1.128** | 1.538 | 1.470 | — | — | 0.3986 / 0.4490 / 0.2119 |
| 26.5 | light | increased-contrast | 1x | dom | 96 | inactive | — | calibration | ok | 0.054 | 0.161 | 1.389 | **2.984** | 0.005 | 0.011 | — | — | 0.9624 / 0.9810 / 0.2148 |
| 26.5 | light | increased-contrast | 1x | dom | 96 | rest | — | calibration | ok | 0.046 | 0.390 | 1.389 | **8.555** | 0.014 | 0.048 | — | — | 0.9564 / 0.9102 / 0.2147 |
| 26.5 | light | increased-contrast | 1x | dom | 160 | rest | — | holdout | ok | 0.049 | 0.428 | 1.401 | **8.721** | 0.018 | 0.045 | — | — | 0.9689 / 0.9047 / 0.2258 |
| 26.5 | light | increased-contrast | 1x | texture | 44 | inactive | — | calibration | ok | 0.063 | 0.040 | 1.386 | **0.628** | 0.018 | 0.008 | — | — | 0.9316 / 0.9440 / 0.2119 |
| 26.5 | light | increased-contrast | 1x | texture | 44 | inactive | — | validation | ok | 0.068 | 0.051 | 1.070 | **0.750** | 0.031 | 0.017 | — | — | 0.9000 / 0.9281 / 0.2536 |
| 26.5 | light | increased-contrast | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.070 | 0.046 | 1.386 | **0.661** | 0.014 | 0.008 | — | — | 0.7297 / 0.7427 / 0.2119 |
| 26.5 | light | increased-contrast | 1x | texture | 44 | rest | — | calibration | ok | 0.051 | 0.254 | 1.386 | **4.994** | 0.043 | 0.050 | — | — | 0.9183 / 0.9009 / 0.2119 |
| 26.5 | light | increased-contrast | 1x | texture | 44 | rest | — | validation | ok | 0.055 | 0.291 | 1.070 | **5.253** | 0.059 | 0.059 | — | — | 0.8792 / 0.9084 / 0.2536 |
| 26.5 | light | increased-contrast | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.274 | 0.323 | 1.386 | **1.179** | 1.538 | 1.468 | — | — | 0.3986 / 0.4475 / 0.2119 |
| 26.5 | light | increased-contrast | 1x | texture | 96 | inactive | — | calibration | ok | 0.054 | 0.036 | 1.389 | **0.661** | 0.005 | 0.005 | — | — | 0.9624 / 0.9646 / 0.2148 |
| 26.5 | light | increased-contrast | 1x | texture | 96 | rest | — | calibration | ok | 0.046 | 0.348 | 1.389 | **7.618** | 0.014 | 0.052 | — | — | 0.9564 / 0.8992 / 0.2147 |
| 26.5 | light | increased-contrast | 1x | texture | 160 | rest | — | holdout | ok | 0.049 | 0.376 | 1.401 | **7.664** | 0.018 | 0.053 | — | — | 0.9689 / 0.8992 / 0.2258 |
| 26.5 | light | reduced-transparency | 1x | dom | 44 | inactive | — | calibration | ok | 0.277 | 0.332 | 1.386 | **1.199** | 0.084 | 0.056 | — | — | 0.9484 / 0.9210 / 0.2119 |
| 26.5 | light | reduced-transparency | 1x | dom | 44 | inactive | — | validation | ok | 0.243 | 0.384 | 1.070 | **1.580** | 0.092 | 0.087 | — | — | 0.9400 / 0.8680 / 0.2536 |
| 26.5 | light | reduced-transparency | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.301 | 0.549 | 1.386 | **1.828** | 0.059 | 0.002 | — | — | 0.7440 / 0.7229 / 0.2119 |
| 26.5 | light | reduced-transparency | 1x | dom | 44 | rest | — | calibration | ok | 0.366 | 0.690 | 1.386 | **1.887** | 0.082 | 0.090 | — | — | 0.8927 / 0.8922 / 0.2119 |
| 26.5 | light | reduced-transparency | 1x | dom | 44 | rest | — | validation | ok | 0.357 | 0.443 | 1.070 | **1.239** | 0.088 | 0.108 | — | — | 0.8899 / 0.9064 / 0.2536 |
| 26.5 | light | reduced-transparency | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.481 | 0.890 | 1.386 | **1.851** | 1.515 | 1.524 | — | — | 0.4166 / 0.4143 / 0.2119 |
| 26.5 | light | reduced-transparency | 1x | dom | 96 | inactive | — | calibration | ok | 0.329 | 0.396 | 1.389 | **1.204** | 0.067 | 0.042 | — | — | 0.9508 / 0.9379 / 0.2147 |
| 26.5 | light | reduced-transparency | 1x | dom | 96 | rest | — | calibration | ok | 0.453 | 0.908 | 1.389 | **2.003** | 0.071 | 0.086 | — | — | 0.8930 / 0.8953 / 0.2147 |
| 26.5 | light | reduced-transparency | 1x | dom | 160 | rest | — | holdout | ok | 0.486 | 0.939 | 1.401 | **1.931** | 0.059 | 0.086 | — | — | 0.8920 / 0.8948 / 0.2258 |
| 26.5 | light | reduced-transparency | 1x | texture | 44 | inactive | — | calibration | ok | 0.277 | 0.236 | 1.386 | **0.850** | 0.084 | 0.029 | — | — | 0.9484 / 0.9453 / 0.2119 |
| 26.5 | light | reduced-transparency | 1x | texture | 44 | inactive | — | validation | ok | 0.243 | 0.179 | 1.070 | **0.737** | 0.092 | 0.038 | — | — | 0.9400 / 0.9389 / 0.2536 |
| 26.5 | light | reduced-transparency | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.301 | 0.315 | 1.386 | **1.047** | 0.059 | 0.006 | — | — | 0.7440 / 0.7215 / 0.2119 |
| 26.5 | light | reduced-transparency | 1x | texture | 44 | rest | — | calibration | ok | 0.366 | 0.289 | 1.386 | **0.790** | 0.082 | 0.055 | — | — | 0.8927 / 0.8943 / 0.2119 |
| 26.5 | light | reduced-transparency | 1x | texture | 44 | rest | — | validation | ok | 0.357 | 0.269 | 1.070 | **0.753** | 0.088 | 0.068 | — | — | 0.8899 / 0.8925 / 0.2536 |
| 26.5 | light | reduced-transparency | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.481 | 0.553 | 1.386 | **1.149** | 1.515 | 1.525 | — | — | 0.4166 / 0.4152 / 0.2119 |
| 26.5 | light | reduced-transparency | 1x | texture | 96 | inactive | — | calibration | ok | 0.329 | 0.229 | 1.389 | **0.696** | 0.067 | 0.027 | — | — | 0.9508 / 0.9469 / 0.2147 |
| 26.5 | light | reduced-transparency | 1x | texture | 96 | rest | — | calibration | ok | 0.453 | 0.329 | 1.389 | **0.725** | 0.071 | 0.054 | — | — | 0.8930 / 0.8958 / 0.2147 |
| 26.5 | light | reduced-transparency | 1x | texture | 160 | rest | — | holdout | ok | 0.486 | 0.368 | 1.401 | **0.757** | 0.059 | 0.054 | — | — | 0.8920 / 0.8973 / 0.2258 |
| 26.5 | light | standard | 1x | dom | 32 | inactive | — | validation | ok | 1.139 | 1.598 | 1.826 | **1.403** | 0.393 | 0.409 | 0.500 | 0.633 | 0.5396 / 0.5487 / 0.1682 |
| 26.5 | light | standard | 1x | dom | 32 | rest | — | validation | ok | 0.586 | 1.073 | 1.826 | **1.829** | 0.389 | 0.364 | — | 0.427 | 0.5559 / 0.6097 / 0.1682 |
| 26.5 | light | standard | 1x | dom | 44 | inactive | — | calibration | ok | 1.246 | 1.601 | 1.386 | **1.285** | 0.431 | 0.464 | 0.574 | 0.663 | 0.5871 / 0.5724 / 0.2119 |
| 26.5 | light | standard | 1x | dom | 44 | inactive | — | validation | ok | 1.091 | 1.294 | 1.070 | **1.186** | 0.497 | 0.557 | 0.637 | 0.722 | 0.6040 / 0.5719 / 0.2536 |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-blue | yes | calibration | ok | 1.201 | 1.305 | 1.386 | **1.087** | 0.312 | 0.005 | — | — | 0.4328 / 0.4562 / 0.2119 |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 1.201 | 1.305 | 1.386 | **1.087** | 0.312 | 0.005 | — | — | 0.4328 / 0.4562 / 0.2119 |
| 26.5 | light | standard | 1x | dom | 44 | inactive-tint-orange-half | yes | calibration | ok | 1.242 | 1.772 | 1.386 | **1.427** | 0.372 | 0.239 | — | — | 0.5050 / 0.5131 / 0.2119 |
| 26.5 | light | standard | 1x | dom | 44 | rest | — | calibration | ok | 1.085 | 1.400 | 1.386 | **1.290** | 0.414 | 0.418 | 0.522 | 0.584 | 0.5832 / 0.6223 / 0.2119 |
| 26.5 | light | standard | 1x | dom | 44 | rest | — | validation | ok | 1.172 | 1.222 | 1.070 | **1.042** | 0.474 | 0.477 | 0.638 | 0.646 | 0.6012 / 0.6336 / 0.2536 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-blue | yes | calibration | ok | 0.436 | 0.452 | 1.386 | **1.036** | 1.695 | 1.699 | — | — | 0.2019 / 0.2000 / 0.2119 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.421 | 0.526 | 1.386 | **1.249** | 1.440 | 1.451 | — | — | 0.3524 / 0.3566 / 0.2119 |
| 26.5 | light | standard | 1x | dom | 44 | rest-tint-orange-half | yes | calibration | ok | 0.710 | 1.790 | 1.386 | **2.520** | 0.922 | 0.943 | — | — | 0.4385 / 0.4575 / 0.2119 |
| 26.5 | light | standard | 1x | dom | 96 | inactive | — | calibration | ok | 1.541 | 1.442 | 1.389 | **0.936** | 0.560 | 0.395 | 0.752 | 0.632 | 0.6288 / 0.6199 / 0.2147 |
| 26.5 | light | standard | 1x | dom | 96 | inactive-tint-orange | yes | validation | ok | 1.422 | 0.737 | 1.389 | **0.518** | 0.406 | 0.001 | — | — | 0.4650 / 0.4909 / 0.2147 |
| 26.5 | light | standard | 1x | dom | 96 | rest | — | calibration | ok | 1.324 | 1.356 | 1.389 | **1.024** | 0.499 | 0.361 | 0.657 | 0.586 | 0.6649 / 0.6562 / 0.2147 |
| 26.5 | light | standard | 1x | dom | 96 | rest-tint-orange | yes | validation | ok | 0.385 | 0.382 | 1.389 | **0.993** | 1.186 | 1.183 | — | — | 0.3656 / 0.3624 / 0.2147 |
| 26.5 | light | standard | 1x | dom | 128 | inactive | — | probe | ok | 1.530 | 1.509 | 1.381 | **0.986** | 0.602 | 0.411 | 0.805 | 0.694 | 0.6282 / 0.6182 / 0.2211 |
| 26.5 | light | standard | 1x | dom | 128 | rest | — | calibration | ok | 1.330 | 1.403 | 1.381 | **1.055** | 0.501 | 0.365 | 0.690 | 0.636 | 0.6734 / 0.6573 / 0.2211 |
| 26.5 | light | standard | 1x | dom | 130 | rest | — | holdout | ok | 0.629 | 0.474 | 1.392 | **0.753** | 0.447 | 0.320 | — | — | 0.7064 / 0.6918 / 0.2190 |
| 26.5 | light | standard | 1x | dom | 160 | rest | — | holdout | ok | 1.357 | 1.417 | 1.401 | **1.045** | 0.482 | 0.368 | 0.687 | 0.648 | 0.6855 / 0.6562 / 0.2258 |
| 26.5 | light | standard | 1x | dom | 160 | rest-tint-orange | yes | holdout | ok | 0.407 | 0.421 | 1.401 | **1.034** | 1.073 | 1.067 | — | — | 0.3678 / 0.3621 / 0.2258 |
| 26.5 | light | standard | 1x | texture | 32 | inactive | — | validation | ok | 1.139 | 0.776 | 1.826 | **0.681** | 0.393 | 0.236 | 0.500 | 0.328 | 0.5396 / 0.5521 / 0.1682 |
| 26.5 | light | standard | 1x | texture | 32 | rest | — | validation | ok | 0.586 | 0.292 | 1.826 | **0.499** | 0.389 | 0.212 | — | — | 0.5559 / 0.6019 / 0.1682 |
| 26.5 | light | standard | 1x | texture | 44 | inactive | — | calibration | ok | 1.246 | 0.796 | 1.386 | **0.639** | 0.431 | 0.250 | 0.574 | 0.347 | 0.5871 / 0.5797 / 0.2119 |
| 26.5 | light | standard | 1x | texture | 44 | inactive | — | validation | ok | 1.091 | 0.613 | 1.070 | **0.561** | 0.497 | 0.297 | 0.637 | 0.370 | 0.6040 / 0.5998 / 0.2536 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-blue | yes | calibration | ok | 1.201 | 0.257 | 1.386 | **0.214** | 0.312 | 0.006 | — | — | 0.4328 / 0.4529 / 0.2119 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 1.201 | 0.257 | 1.386 | **0.214** | 0.312 | 0.006 | — | — | 0.4328 / 0.4529 / 0.2119 |
| 26.5 | light | standard | 1x | texture | 44 | inactive-tint-orange-half | yes | calibration | ok | 1.242 | 0.514 | 1.386 | **0.414** | 0.372 | 0.129 | — | — | 0.5050 / 0.5137 / 0.2119 |
| 26.5 | light | standard | 1x | texture | 44 | rest | — | calibration | ok | 1.085 | 0.530 | 1.386 | **0.489** | 0.414 | 0.226 | 0.522 | 0.271 | 0.5832 / 0.6192 / 0.2119 |
| 26.5 | light | standard | 1x | texture | 44 | rest | — | validation | ok | 1.172 | 0.562 | 1.070 | **0.480** | 0.474 | 0.266 | 0.638 | 0.334 | 0.6012 / 0.6400 / 0.2536 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-blue | yes | calibration | ok | 0.436 | 0.310 | 1.386 | **0.712** | 1.695 | 1.690 | — | — | 0.2019 / 0.2052 / 0.2119 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.421 | 0.284 | 1.386 | **0.674** | 1.440 | 1.452 | — | — | 0.3524 / 0.3605 / 0.2119 |
| 26.5 | light | standard | 1x | texture | 44 | rest-tint-orange-half | yes | calibration | ok | 0.710 | 0.368 | 1.386 | **0.518** | 0.922 | 0.920 | — | — | 0.4385 / 0.4610 / 0.2119 |
| 26.5 | light | standard | 1x | texture | 96 | inactive | — | calibration | ok | 1.541 | 0.751 | 1.389 | **0.488** | 0.560 | 0.221 | 0.752 | 0.336 | 0.6288 / 0.6303 / 0.2147 |
| 26.5 | light | standard | 1x | texture | 96 | inactive-tint-orange | yes | validation | ok | 1.422 | 0.164 | 1.389 | **0.116** | 0.406 | 0.003 | — | — | 0.4650 / 0.4898 / 0.2147 |
| 26.5 | light | standard | 1x | texture | 96 | rest | — | calibration | ok | 1.324 | 0.620 | 1.389 | **0.468** | 0.499 | 0.202 | 0.657 | 0.286 | 0.6649 / 0.6603 / 0.2147 |
| 26.5 | light | standard | 1x | texture | 96 | rest-tint-orange | yes | validation | ok | 0.385 | 0.289 | 1.389 | **0.751** | 1.186 | 1.184 | — | — | 0.3656 / 0.3660 / 0.2147 |
| 26.5 | light | standard | 1x | texture | 128 | inactive | — | probe | ok | 1.530 | 0.756 | 1.381 | **0.494** | 0.602 | 0.236 | 0.805 | 0.362 | 0.6282 / 0.6277 / 0.2211 |
| 26.5 | light | standard | 1x | texture | 128 | rest | — | calibration | ok | 1.330 | 0.654 | 1.381 | **0.491** | 0.501 | 0.211 | 0.690 | 0.316 | 0.6734 / 0.6613 / 0.2211 |
| 26.5 | light | standard | 1x | texture | 130 | rest | — | holdout | ok | 0.629 | 0.280 | 1.392 | **0.445** | 0.447 | 0.190 | — | — | 0.7064 / 0.6865 / 0.2190 |
| 26.5 | light | standard | 1x | texture | 160 | rest | — | holdout | ok | 1.357 | 0.706 | 1.401 | **0.520** | 0.482 | 0.212 | 0.687 | 0.335 | 0.6855 / 0.6626 / 0.2258 |
| 26.5 | light | standard | 1x | texture | 160 | rest-tint-orange | yes | holdout | ok | 0.407 | 0.301 | 1.401 | **0.739** | 1.073 | 1.069 | — | — | 0.3678 / 0.3656 / 0.2258 |
| 26.5 | light | standard | 2x | dom | 32 | inactive | — | validation | ok | 1.368 | 1.625 | 1.814 | **1.188** | 0.406 | 0.452 | — | 0.631 | 0.5407 / 0.5504 / 0.1685 |
| 26.5 | light | standard | 2x | dom | 32 | rest | — | validation | ok | 0.592 | 1.120 | 1.814 | **1.892** | 0.397 | 0.384 | — | 0.442 | 0.5549 / 0.6091 / 0.1685 |
| 26.5 | light | standard | 2x | dom | 44 | inactive | — | calibration | ok | 1.298 | 1.519 | 1.378 | **1.170** | 0.427 | 0.504 | — | 0.661 | 0.5753 / 0.5764 / 0.2128 |
| 26.5 | light | standard | 2x | dom | 44 | inactive | — | validation | ok | 1.155 | 1.303 | 1.069 | **1.128** | 0.500 | 0.574 | 0.654 | 0.734 | 0.6094 / 0.5881 / 0.2545 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-blue | yes | calibration | ok | 1.224 | 1.340 | 1.378 | **1.095** | 0.308 | 0.002 | — | — | 0.4227 / 0.4563 / 0.2128 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 1.224 | 1.340 | 1.378 | **1.095** | 0.308 | 0.002 | — | — | 0.4227 / 0.4563 / 0.2128 |
| 26.5 | light | standard | 2x | dom | 44 | inactive-tint-orange-half | yes | calibration | ok | 1.277 | 1.747 | 1.379 | **1.368** | 0.368 | 0.258 | — | — | 0.4941 / 0.5147 / 0.2128 |
| 26.5 | light | standard | 2x | dom | 44 | rest | — | calibration | ok | 1.023 | 1.356 | 1.379 | **1.326** | 0.419 | 0.436 | 0.515 | — | 0.5837 / 0.6233 / 0.2128 |
| 26.5 | light | standard | 2x | dom | 44 | rest | — | validation | ok | 1.110 | 1.196 | 1.069 | **1.077** | 0.488 | 0.487 | 0.633 | 0.646 | 0.6204 / 0.6392 / 0.2545 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-blue | yes | calibration | ok | 0.411 | 0.443 | 1.379 | **1.079** | 1.693 | 1.696 | — | — | 0.2025 / 0.2000 / 0.2128 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.387 | 0.405 | 1.379 | **1.048** | 1.439 | 1.449 | — | — | 0.3527 / 0.3566 / 0.2128 |
| 26.5 | light | standard | 2x | dom | 44 | rest-tint-orange-half | yes | calibration | ok | 0.637 | 1.734 | 1.379 | **2.722** | 0.925 | 0.945 | — | — | 0.4391 / 0.4579 / 0.2128 |
| 26.5 | light | standard | 2x | dom | 96 | inactive | — | calibration | ok | 1.589 | 1.362 | 1.388 | **0.857** | 0.557 | 0.424 | — | — | 0.6291 / 0.6213 / 0.2153 |
| 26.5 | light | standard | 2x | dom | 96 | inactive-tint-orange | yes | validation | ok | 1.464 | 0.695 | 1.388 | **0.475** | 0.404 | 0.000 | — | — | 0.4652 / 0.4910 / 0.2153 |
| 26.5 | light | standard | 2x | dom | 96 | rest | — | calibration | ok | 1.303 | 1.309 | 1.388 | **1.005** | 0.504 | 0.378 | 0.653 | — | 0.6654 / 0.6573 / 0.2153 |
| 26.5 | light | standard | 2x | dom | 96 | rest-tint-orange | yes | validation | ok | 0.379 | 0.312 | 1.388 | **0.823** | 1.186 | 1.183 | — | — | 0.3656 / 0.3624 / 0.2153 |
| 26.5 | light | standard | 2x | dom | 128 | inactive | — | probe | ok | 1.550 | 1.445 | 1.381 | **0.932** | 0.600 | 0.433 | — | — | 0.6286 / 0.6191 / 0.2214 |
| 26.5 | light | standard | 2x | dom | 128 | rest | — | calibration | ok | 1.313 | 1.362 | 1.381 | **1.038** | 0.506 | 0.380 | — | — | 0.6732 / 0.6578 / 0.2214 |
| 26.5 | light | standard | 2x | dom | 130 | rest | — | holdout | ok | 0.635 | 0.487 | 1.391 | **0.767** | 0.452 | 0.332 | — | — | 0.7054 / 0.6915 / 0.2193 |
| 26.5 | light | standard | 2x | dom | 160 | rest | — | holdout | ok | 1.336 | 1.368 | 1.401 | **1.024** | 0.484 | 0.380 | — | — | 0.6853 / 0.6569 / 0.2260 |
| 26.5 | light | standard | 2x | dom | 160 | rest-tint-orange | yes | holdout | ok | 0.390 | 0.348 | 1.401 | **0.892** | 1.073 | 1.067 | — | — | 0.3678 / 0.3622 / 0.2260 |
| 26.5 | light | standard | 2x | texture | 32 | inactive | — | validation | ok | 1.368 | 0.921 | 1.814 | **0.674** | 0.406 | 0.242 | — | — | 0.5407 / 0.5524 / 0.1685 |
| 26.5 | light | standard | 2x | texture | 32 | rest | — | validation | ok | 0.592 | 0.261 | 1.814 | **0.441** | 0.397 | 0.213 | — | — | 0.5549 / 0.6016 / 0.1685 |
| 26.5 | light | standard | 2x | texture | 44 | inactive | — | calibration | ok | 1.298 | 0.803 | 1.378 | **0.619** | 0.427 | 0.252 | — | — | 0.5753 / 0.5811 / 0.2128 |
| 26.5 | light | standard | 2x | texture | 44 | inactive | — | validation | ok | 1.155 | 0.625 | 1.069 | **0.541** | 0.500 | 0.296 | 0.654 | 0.372 | 0.6094 / 0.6044 / 0.2545 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-blue | yes | calibration | ok | 1.224 | 0.173 | 1.378 | **0.141** | 0.308 | 0.003 | — | — | 0.4227 / 0.4538 / 0.2128 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 1.224 | 0.173 | 1.378 | **0.141** | 0.308 | 0.003 | — | — | 0.4227 / 0.4538 / 0.2128 |
| 26.5 | light | standard | 2x | texture | 44 | inactive-tint-orange-half | yes | calibration | ok | 1.277 | 0.496 | 1.379 | **0.388** | 0.368 | 0.129 | — | — | 0.4941 / 0.5147 / 0.2128 |
| 26.5 | light | standard | 2x | texture | 44 | rest | — | calibration | ok | 1.023 | 0.484 | 1.379 | **0.473** | 0.419 | 0.227 | 0.515 | 0.266 | 0.5837 / 0.6196 / 0.2128 |
| 26.5 | light | standard | 2x | texture | 44 | rest | — | validation | ok | 1.110 | 0.526 | 1.069 | **0.474** | 0.488 | 0.265 | 0.633 | 0.326 | 0.6204 / 0.6438 / 0.2545 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-blue | yes | calibration | ok | 0.411 | 0.314 | 1.379 | **0.765** | 1.693 | 1.688 | — | — | 0.2025 / 0.2048 / 0.2128 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.387 | 0.265 | 1.379 | **0.686** | 1.439 | 1.450 | — | — | 0.3527 / 0.3604 / 0.2128 |
| 26.5 | light | standard | 2x | texture | 44 | rest-tint-orange-half | yes | calibration | ok | 0.637 | 0.337 | 1.379 | **0.529** | 0.925 | 0.919 | — | — | 0.4391 / 0.4606 / 0.2128 |
| 26.5 | light | standard | 2x | texture | 96 | inactive | — | calibration | ok | 1.589 | 0.758 | 1.388 | **0.477** | 0.557 | 0.221 | — | — | 0.6291 / 0.6313 / 0.2153 |
| 26.5 | light | standard | 2x | texture | 96 | inactive-tint-orange | yes | validation | ok | 1.464 | 0.128 | 1.388 | **0.088** | 0.404 | 0.001 | — | — | 0.4652 / 0.4905 / 0.2153 |
| 26.5 | light | standard | 2x | texture | 96 | rest | — | calibration | ok | 1.303 | 0.590 | 1.388 | **0.453** | 0.504 | 0.205 | 0.653 | — | 0.6654 / 0.6610 / 0.2153 |
| 26.5 | light | standard | 2x | texture | 96 | rest-tint-orange | yes | validation | ok | 0.379 | 0.306 | 1.388 | **0.807** | 1.186 | 1.184 | — | — | 0.3656 / 0.3661 / 0.2153 |
| 26.5 | light | standard | 2x | texture | 128 | inactive | — | probe | ok | 1.550 | 0.756 | 1.381 | **0.488** | 0.600 | 0.237 | — | — | 0.6286 / 0.6283 / 0.2214 |
| 26.5 | light | standard | 2x | texture | 128 | rest | — | calibration | ok | 1.313 | 0.633 | 1.381 | **0.483** | 0.506 | 0.214 | — | — | 0.6732 / 0.6614 / 0.2214 |
| 26.5 | light | standard | 2x | texture | 130 | rest | — | holdout | ok | 0.635 | 0.283 | 1.391 | **0.445** | 0.452 | 0.193 | — | — | 0.7054 / 0.6865 / 0.2193 |
| 26.5 | light | standard | 2x | texture | 160 | rest | — | holdout | ok | 1.336 | 0.683 | 1.401 | **0.511** | 0.484 | 0.216 | — | — | 0.6853 / 0.6627 / 0.2260 |
| 26.5 | light | standard | 2x | texture | 160 | rest-tint-orange | yes | holdout | ok | 0.390 | 0.302 | 1.401 | **0.776** | 1.073 | 1.068 | — | — | 0.3678 / 0.3656 / 0.2260 |
| 27 | dark | standard | 1x | dom | 44 | inactive | — | calibration | REFUSED | 2.540 | 2.735 | 1.355 | **1.077** | 0.903 | 0.216 | 1.243 | — | 0.2037 / 0.1873 / 0.2158 |
| 27 | dark | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 1.683 | 1.183 | 1.386 | **0.703** | 0.647 | 0.003 | — | — | 0.2904 / 0.2915 / 0.2120 |
| 27 | dark | standard | 1x | dom | 44 | rest | — | calibration | REFUSED | 2.398 | 2.546 | 1.363 | **1.062** | 0.973 | 0.188 | 1.213 | — | 0.2254 / 0.1790 / 0.2090 |
| 27 | dark | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.625 | 0.446 | 1.386 | **0.714** | 1.486 | 1.544 | — | — | 0.4430 / 0.4274 / 0.2119 |
| 27 | dark | standard | 1x | dom | 96 | inactive | — | calibration | REFUSED | 3.933 | 3.949 | 1.367 | **1.004** | 0.903 | 0.197 | 1.739 | — | 0.1695 / 0.1597 / 0.2219 |
| 27 | dark | standard | 1x | dom | 96 | rest | — | calibration | REFUSED | 3.595 | 3.423 | 1.370 | **0.952** | 0.918 | 0.192 | 1.638 | — | 0.1887 / 0.1625 / 0.2212 |
| 27 | dark | standard | 1x | dom | 128 | inactive | — | probe | REFUSED | 3.767 | 3.654 | 1.364 | **0.970** | 0.900 | 0.210 | 1.743 | — | 0.1659 / 0.1604 / 0.2282 |
| 27 | dark | standard | 1x | dom | 130 | inactive | — | holdout | REFUSED | 3.918 | 3.314 | 1.374 | **0.846** | 0.905 | 0.179 | 1.792 | — | 0.1686 / 0.1620 / 0.2257 |
| 27 | dark | standard | 1x | dom | 160 | inactive | — | holdout | REFUSED | 3.916 | 4.025 | 1.380 | **1.028** | 0.923 | 0.204 | 1.798 | — | 0.1708 / 0.1589 / 0.2331 |
| 27 | dark | standard | 1x | dom | 160 | rest | — | holdout | REFUSED | 3.760 | 3.699 | 1.385 | **0.984** | 0.900 | 0.189 | 1.734 | — | 0.1814 / 0.1627 / 0.2331 |
| 27 | dark | standard | 1x | texture | 44 | inactive | — | calibration | REFUSED | 2.540 | 1.667 | 1.355 | **0.656** | 0.903 | 0.117 | 1.243 | — | 0.2037 / 0.1878 / 0.2158 |
| 27 | dark | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 1.683 | 0.578 | 1.386 | **0.344** | 0.647 | 0.006 | — | — | 0.2904 / 0.2896 / 0.2120 |
| 27 | dark | standard | 1x | texture | 44 | rest | — | calibration | REFUSED | 2.398 | 0.706 | 1.363 | **0.294** | 0.973 | 0.106 | 1.213 | 0.212 | 0.2254 / 0.1797 / 0.2090 |
| 27 | dark | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.625 | 0.823 | 1.386 | **1.318** | 1.486 | 1.540 | — | — | 0.4430 / 0.4285 / 0.2119 |
| 27 | dark | standard | 1x | texture | 96 | inactive | — | calibration | REFUSED | 3.933 | 2.014 | 1.367 | **0.512** | 0.903 | 0.118 | 1.739 | — | 0.1695 / 0.1619 / 0.2219 |
| 27 | dark | standard | 1x | texture | 96 | rest | — | calibration | REFUSED | 3.595 | 1.131 | 1.370 | **0.315** | 0.918 | 0.109 | 1.638 | — | 0.1887 / 0.1637 / 0.2212 |
| 27 | dark | standard | 1x | texture | 128 | inactive | — | probe | REFUSED | 3.767 | 1.941 | 1.364 | **0.515** | 0.900 | 0.125 | 1.743 | — | 0.1659 / 0.1614 / 0.2282 |
| 27 | dark | standard | 1x | texture | 130 | inactive | — | holdout | REFUSED | 3.918 | 1.808 | 1.374 | **0.462** | 0.905 | 0.108 | 1.792 | — | 0.1686 / 0.1631 / 0.2257 |
| 27 | dark | standard | 1x | texture | 160 | inactive | — | holdout | REFUSED | 3.916 | 2.102 | 1.380 | **0.537** | 0.923 | 0.127 | 1.798 | — | 0.1708 / 0.1606 / 0.2331 |
| 27 | dark | standard | 1x | texture | 160 | rest | — | holdout | REFUSED | 3.760 | 1.479 | 1.385 | **0.393** | 0.900 | 0.115 | 1.734 | — | 0.1814 / 0.1635 / 0.2331 |
| 27 | dark | standard | 2x | dom | 44 | inactive | — | calibration | REFUSED | 2.541 | 2.683 | 1.349 | **1.056** | 0.905 | 0.228 | 1.246 | — | 0.2046 / 0.1877 / 0.2167 |
| 27 | dark | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 1.679 | 1.173 | 1.379 | **0.699** | 0.648 | 0.002 | — | — | 0.2914 / 0.2916 / 0.2128 |
| 27 | dark | standard | 2x | dom | 44 | rest | — | calibration | REFUSED | 2.334 | 2.297 | 1.356 | **0.984** | 0.973 | 0.219 | 1.205 | — | 0.2262 / 0.1784 / 0.2099 |
| 27 | dark | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.559 | 0.455 | 1.379 | **0.813** | 1.484 | 1.542 | — | — | 0.4439 / 0.4275 / 0.2128 |
| 27 | dark | standard | 2x | dom | 96 | inactive | — | calibration | REFUSED | 3.881 | 3.625 | 1.364 | **0.934** | 0.906 | 0.235 | — | — | 0.1697 / 0.1602 / 0.2235 |
| 27 | dark | standard | 2x | dom | 96 | rest | — | calibration | REFUSED | 3.550 | 3.394 | 1.368 | **0.956** | 0.917 | 0.212 | — | — | 0.1890 / 0.1628 / 0.2224 |
| 27 | dark | standard | 2x | dom | 128 | inactive | — | probe | REFUSED | 3.751 | 3.451 | 1.362 | **0.920** | 0.902 | 0.240 | — | — | 0.1661 / 0.1607 / 0.2292 |
| 27 | dark | standard | 2x | dom | 130 | inactive | — | holdout | REFUSED | 3.954 | 3.290 | 1.373 | **0.832** | 0.907 | 0.204 | — | — | 0.1693 / 0.1623 / 0.2266 |
| 27 | dark | standard | 2x | dom | 160 | inactive | — | holdout | REFUSED | 3.937 | 3.808 | 1.381 | **0.967** | 0.920 | 0.235 | — | — | 0.1705 / 0.1595 / 0.2332 |
| 27 | dark | standard | 2x | dom | 160 | rest | — | holdout | REFUSED | 3.743 | 3.609 | 1.384 | **0.964** | 0.899 | 0.209 | — | — | 0.1811 / 0.1627 / 0.2336 |
| 27 | dark | standard | 2x | texture | 44 | inactive | — | calibration | REFUSED | 2.541 | 1.673 | 1.349 | **0.658** | 0.905 | 0.114 | 1.246 | — | 0.2046 / 0.1880 / 0.2167 |
| 27 | dark | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 1.679 | 0.416 | 1.379 | **0.248** | 0.648 | 0.003 | — | — | 0.2914 / 0.2901 / 0.2128 |
| 27 | dark | standard | 2x | texture | 44 | rest | — | calibration | REFUSED | 2.334 | 0.821 | 1.356 | **0.352** | 0.973 | 0.107 | 1.205 | — | 0.2262 / 0.1769 / 0.2099 |
| 27 | dark | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.559 | 0.768 | 1.379 | **1.373** | 1.484 | 1.539 | — | — | 0.4439 / 0.4278 / 0.2128 |
| 27 | dark | standard | 2x | texture | 96 | inactive | — | calibration | REFUSED | 3.881 | 1.921 | 1.364 | **0.495** | 0.906 | 0.123 | — | — | 0.1697 / 0.1625 / 0.2235 |
| 27 | dark | standard | 2x | texture | 96 | rest | — | calibration | REFUSED | 3.550 | 1.283 | 1.368 | **0.361** | 0.917 | 0.114 | — | — | 0.1890 / 0.1627 / 0.2224 |
| 27 | dark | standard | 2x | texture | 128 | inactive | — | probe | REFUSED | 3.751 | 1.848 | 1.362 | **0.493** | 0.902 | 0.130 | — | — | 0.1661 / 0.1616 / 0.2292 |
| 27 | dark | standard | 2x | texture | 130 | inactive | — | holdout | REFUSED | 3.954 | 1.756 | 1.373 | **0.444** | 0.907 | 0.111 | — | — | 0.1693 / 0.1633 / 0.2266 |
| 27 | dark | standard | 2x | texture | 160 | inactive | — | holdout | REFUSED | 3.937 | 2.025 | 1.381 | **0.514** | 0.920 | 0.132 | — | — | 0.1705 / 0.1608 / 0.2332 |
| 27 | dark | standard | 2x | texture | 160 | rest | — | holdout | REFUSED | 3.743 | 1.609 | 1.384 | **0.430** | 0.899 | 0.119 | — | — | 0.1811 / 0.1628 / 0.2336 |
| 27 | light | increased-contrast | 1x | dom | 44 | inactive | — | calibration | ok | 0.250 | 0.211 | 1.386 | **0.847** | 0.097 | 0.014 | — | — | 0.8805 / 0.9595 / 0.2119 |
| 27 | light | increased-contrast | 1x | dom | 44 | inactive | — | validation | ok | 0.245 | 0.287 | 1.070 | **1.172** | 0.118 | 0.063 | — | — | 0.8778 / 0.8829 / 0.2536 |
| 27 | light | increased-contrast | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.214 | 0.366 | 1.386 | **1.712** | 0.072 | 0.002 | — | — | 0.6838 / 0.7832 / 0.2119 |
| 27 | light | increased-contrast | 1x | dom | 44 | rest | — | calibration | ok | 0.311 | 0.267 | 1.386 | **0.858** | 0.109 | 0.043 | — | — | 0.8872 / 0.9163 / 0.2119 |
| 27 | light | increased-contrast | 1x | dom | 44 | rest | — | validation | ok | 0.299 | 0.333 | 1.070 | **1.116** | 0.128 | 0.062 | — | — | 0.8802 / 0.9166 / 0.2536 |
| 27 | light | increased-contrast | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.325 | 0.309 | 1.386 | **0.949** | 1.522 | 1.470 | — | — | 0.4106 / 0.4490 / 0.2119 |
| 27 | light | increased-contrast | 1x | dom | 96 | inactive | — | calibration | ok | 0.434 | 0.164 | 1.389 | **0.379** | 0.111 | 0.010 | — | — | 0.8853 / 0.9807 / 0.2147 |
| 27 | light | increased-contrast | 1x | dom | 96 | rest | — | calibration | ok | 0.465 | 0.356 | 1.389 | **0.766** | 0.116 | 0.041 | — | — | 0.8854 / 0.9108 / 0.2147 |
| 27 | light | increased-contrast | 1x | dom | 160 | inactive | — | holdout | ok | 0.561 | 0.152 | 1.401 | **0.272** | 0.121 | 0.008 | — | — | 0.8854 / 0.9824 / 0.2258 |
| 27 | light | increased-contrast | 1x | dom | 160 | rest | — | holdout | ok | 0.571 | 0.462 | 1.401 | **0.810** | 0.122 | 0.040 | — | — | 0.8858 / 0.9036 / 0.2258 |
| 27 | light | increased-contrast | 1x | texture | 44 | inactive | — | calibration | ok | 0.250 | 0.039 | 1.386 | **0.155** | 0.097 | 0.008 | — | — | 0.8805 / 0.9441 / 0.2119 |
| 27 | light | increased-contrast | 1x | texture | 44 | inactive | — | validation | ok | 0.245 | 0.051 | 1.070 | **0.206** | 0.118 | 0.017 | — | — | 0.8778 / 0.9279 / 0.2536 |
| 27 | light | increased-contrast | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.214 | 0.046 | 1.386 | **0.214** | 0.072 | 0.008 | — | — | 0.6838 / 0.7426 / 0.2119 |
| 27 | light | increased-contrast | 1x | texture | 44 | rest | — | calibration | ok | 0.311 | 0.253 | 1.386 | **0.815** | 0.109 | 0.050 | — | — | 0.8872 / 0.9009 / 0.2119 |
| 27 | light | increased-contrast | 1x | texture | 44 | rest | — | validation | ok | 0.299 | 0.292 | 1.070 | **0.977** | 0.128 | 0.058 | — | — | 0.8802 / 0.9084 / 0.2536 |
| 27 | light | increased-contrast | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.325 | 0.322 | 1.386 | **0.990** | 1.522 | 1.468 | — | — | 0.4106 / 0.4476 / 0.2119 |
| 27 | light | increased-contrast | 1x | texture | 96 | inactive | — | calibration | ok | 0.434 | 0.038 | 1.389 | **0.087** | 0.111 | 0.005 | — | — | 0.8853 / 0.9642 / 0.2147 |
| 27 | light | increased-contrast | 1x | texture | 96 | rest | — | calibration | ok | 0.465 | 0.350 | 1.389 | **0.752** | 0.116 | 0.052 | — | — | 0.8854 / 0.8992 / 0.2147 |
| 27 | light | increased-contrast | 1x | texture | 160 | inactive | — | holdout | ok | 0.561 | 0.037 | 1.401 | **0.066** | 0.121 | 0.003 | — | — | 0.8854 / 0.9754 / 0.2258 |
| 27 | light | increased-contrast | 1x | texture | 160 | rest | — | holdout | ok | 0.571 | 0.390 | 1.401 | **0.683** | 0.122 | 0.052 | — | — | 0.8858 / 0.8992 / 0.2258 |
| 27 | light | reduced-transparency | 1x | dom | 44 | inactive | — | calibration | ok | 0.208 | 0.302 | 1.386 | **1.456** | 0.079 | 0.036 | — | — | 0.9666 / 0.9188 / 0.2119 |
| 27 | light | reduced-transparency | 1x | dom | 44 | inactive | — | validation | ok | 0.209 | 0.428 | 1.070 | **2.048** | 0.099 | 0.104 | — | — | 0.9539 / 0.8499 / 0.2536 |
| 27 | light | reduced-transparency | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 0.172 | 0.484 | 1.386 | **2.824** | 0.055 | 0.002 | — | — | 0.7588 / 0.7228 / 0.2119 |
| 27 | light | reduced-transparency | 1x | dom | 44 | rest | — | calibration | ok | 0.269 | 0.579 | 1.386 | **2.155** | 0.084 | 0.078 | — | — | 0.9684 / 0.8850 / 0.2119 |
| 27 | light | reduced-transparency | 1x | dom | 44 | rest | — | validation | ok | 0.251 | 0.573 | 1.070 | **2.280** | 0.102 | 0.116 | — | — | 0.9563 / 0.8712 / 0.2536 |
| 27 | light | reduced-transparency | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.379 | 1.953 | 1.386 | **5.147** | 1.537 | 1.525 | — | — | 0.4264 / 0.4138 / 0.2119 |
| 27 | light | reduced-transparency | 1x | dom | 96 | inactive | — | calibration | ok | 0.328 | 0.334 | 1.389 | **1.016** | 0.078 | 0.028 | — | — | 0.9684 / 0.9377 / 0.2147 |
| 27 | light | reduced-transparency | 1x | dom | 96 | rest | — | calibration | ok | 0.365 | 0.862 | 1.389 | **2.360** | 0.080 | 0.077 | — | — | 0.9680 / 0.8909 / 0.2147 |
| 27 | light | reduced-transparency | 1x | dom | 160 | inactive | — | holdout | ok | 0.414 | 0.462 | 1.401 | **1.117** | 0.088 | 0.031 | — | — | 0.9657 / 0.9392 / 0.2258 |
| 27 | light | reduced-transparency | 1x | dom | 160 | rest | — | holdout | ok | 0.432 | 1.106 | 1.401 | **2.562** | 0.089 | 0.075 | — | — | 0.9660 / 0.8918 / 0.2258 |
| 27 | light | reduced-transparency | 1x | texture | 44 | inactive | — | calibration | ok | 0.208 | 0.229 | 1.386 | **1.104** | 0.079 | 0.029 | — | — | 0.9666 / 0.9450 / 0.2119 |
| 27 | light | reduced-transparency | 1x | texture | 44 | inactive | — | validation | ok | 0.209 | 0.173 | 1.070 | **0.829** | 0.099 | 0.037 | — | — | 0.9539 / 0.9384 / 0.2536 |
| 27 | light | reduced-transparency | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 0.172 | 0.302 | 1.386 | **1.759** | 0.055 | 0.006 | — | — | 0.7588 / 0.7216 / 0.2119 |
| 27 | light | reduced-transparency | 1x | texture | 44 | rest | — | calibration | ok | 0.269 | 0.301 | 1.386 | **1.119** | 0.084 | 0.057 | — | — | 0.9684 / 0.8887 / 0.2119 |
| 27 | light | reduced-transparency | 1x | texture | 44 | rest | — | validation | ok | 0.251 | 0.228 | 1.070 | **0.910** | 0.102 | 0.070 | — | — | 0.9563 / 0.8853 / 0.2536 |
| 27 | light | reduced-transparency | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.379 | 0.866 | 1.386 | **2.282** | 1.537 | 1.524 | — | — | 0.4264 / 0.4113 / 0.2119 |
| 27 | light | reduced-transparency | 1x | texture | 96 | inactive | — | calibration | ok | 0.328 | 0.221 | 1.389 | **0.674** | 0.078 | 0.027 | — | — | 0.9684 / 0.9467 / 0.2147 |
| 27 | light | reduced-transparency | 1x | texture | 96 | rest | — | calibration | ok | 0.365 | 0.331 | 1.389 | **0.906** | 0.080 | 0.055 | — | — | 0.9680 / 0.8926 / 0.2147 |
| 27 | light | reduced-transparency | 1x | texture | 160 | inactive | — | holdout | ok | 0.414 | 0.215 | 1.401 | **0.519** | 0.088 | 0.025 | — | — | 0.9657 / 0.9484 / 0.2258 |
| 27 | light | reduced-transparency | 1x | texture | 160 | rest | — | holdout | ok | 0.432 | 0.362 | 1.401 | **0.837** | 0.089 | 0.054 | — | — | 0.9660 / 0.8954 / 0.2258 |
| 27 | light | standard | 1x | dom | 32 | inactive | — | validation | ok | 1.539 | 1.733 | 1.826 | **1.126** | 0.716 | 0.416 | 0.831 | 0.721 | 0.4657 / 0.4707 / 0.1682 |
| 27 | light | standard | 1x | dom | 32 | rest | — | validation | ok | 1.307 | 1.848 | 1.833 | **1.413** | 0.721 | 0.420 | 0.747 | 0.691 | 0.5089 / 0.5148 / 0.1681 |
| 27 | light | standard | 1x | dom | 44 | inactive | — | calibration | ok | 1.795 | 1.836 | 1.386 | **1.023** | 0.748 | 0.441 | 0.915 | 0.710 | 0.4975 / 0.4940 / 0.2119 |
| 27 | light | standard | 1x | dom | 44 | inactive | — | validation | ok | 1.348 | 1.617 | 1.071 | **1.200** | 0.816 | 0.612 | 0.955 | 0.843 | 0.5215 / 0.4939 / 0.2533 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-blue | yes | calibration | ok | 1.692 | 1.589 | 1.386 | **0.940** | 0.543 | 0.005 | — | — | 0.3540 / 0.3966 / 0.2119 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 1.692 | 1.589 | 1.386 | **0.940** | 0.543 | 0.005 | — | — | 0.3540 / 0.3966 / 0.2119 |
| 27 | light | standard | 1x | dom | 44 | inactive-tint-orange-half | yes | calibration | ok | 1.781 | 2.069 | 1.386 | **1.162** | 0.647 | 0.227 | — | — | 0.4209 / 0.4446 / 0.2119 |
| 27 | light | standard | 1x | dom | 44 | rest | — | calibration | ok | 1.592 | 1.663 | 1.388 | **1.045** | 0.785 | 0.468 | 0.912 | 0.679 | 0.5353 / 0.5337 / 0.2118 |
| 27 | light | standard | 1x | dom | 44 | rest | — | validation | ok | 1.291 | 1.442 | 1.071 | **1.117** | 0.833 | 0.578 | 0.958 | 0.772 | 0.5540 / 0.5469 / 0.2535 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-blue | yes | calibration | ok | 0.201 | 0.795 | 1.386 | **3.946** | 1.707 | 1.680 | — | — | 0.1893 / 0.1875 / 0.2119 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.148 | 1.476 | 1.386 | **9.971** | 1.435 | 1.428 | — | — | 0.3377 / 0.3387 / 0.2119 |
| 27 | light | standard | 1x | dom | 44 | rest-tint-orange-half | yes | calibration | ok | 1.423 | 2.551 | 1.386 | **1.792** | 0.969 | 0.925 | — | — | 0.4086 / 0.4106 / 0.2119 |
| 27 | light | standard | 1x | dom | 96 | inactive | — | calibration | ok | 1.838 | 1.986 | 1.389 | **1.081** | 0.795 | 0.441 | 0.982 | 0.829 | 0.4955 / 0.4796 / 0.2147 |
| 27 | light | standard | 1x | dom | 96 | inactive-tint-orange | yes | validation | ok | 1.750 | 1.105 | 1.389 | **0.631** | 0.582 | 0.001 | — | — | 0.3500 / 0.3812 / 0.2147 |
| 27 | light | standard | 1x | dom | 96 | rest | — | calibration | ok | 1.512 | 1.691 | 1.389 | **1.118** | 0.789 | 0.443 | 0.899 | 0.731 | 0.5456 / 0.5482 / 0.2147 |
| 27 | light | standard | 1x | dom | 96 | rest-tint-orange | yes | validation | ok | 0.147 | 0.935 | 1.389 | **6.351** | 1.160 | 1.162 | — | — | 0.3353 / 0.3404 / 0.2147 |
| 27 | light | standard | 1x | dom | 128 | inactive | — | probe | ok | 1.709 | 2.003 | 1.381 | **1.172** | 0.824 | 0.472 | 0.981 | 0.890 | 0.5001 / 0.4745 / 0.2211 |
| 27 | light | standard | 1x | dom | 128 | rest | — | calibration | ok | 1.441 | 1.721 | 1.381 | **1.195** | 0.803 | 0.444 | 0.892 | 0.781 | 0.5639 / 0.5505 / 0.2211 |
| 27 | light | standard | 1x | dom | 130 | inactive | — | holdout | ok | 1.286 | 0.854 | 1.392 | **0.664** | 0.792 | 0.443 | 0.841 | 0.496 | 0.5362 / 0.5170 / 0.2190 |
| 27 | light | standard | 1x | dom | 130 | rest | — | holdout | ok | 1.048 | 0.612 | 1.392 | **0.584** | 0.762 | 0.403 | — | 0.405 | 0.6069 / 0.6099 / 0.2190 |
| 27 | light | standard | 1x | dom | 160 | inactive | — | holdout | ok | 1.734 | 2.110 | 1.401 | **1.217** | 0.855 | 0.478 | 1.001 | 0.929 | 0.5032 / 0.4734 / 0.2258 |
| 27 | light | standard | 1x | dom | 160 | inactive-tint-orange | yes | holdout | ok | 1.723 | 0.797 | 1.400 | **0.463** | 0.632 | 0.000 | — | — | 0.3520 / 0.3813 / 0.2258 |
| 27 | light | standard | 1x | dom | 160 | rest | — | holdout | ok | 1.414 | 1.810 | 1.400 | **1.280** | 0.802 | 0.438 | 0.875 | 0.811 | 0.5779 / 0.5516 / 0.2258 |
| 27 | light | standard | 1x | dom | 160 | rest-tint-orange | yes | holdout | ok | 0.151 | 1.029 | 1.401 | **6.819** | 1.050 | 1.045 | — | — | 0.3396 / 0.3432 / 0.2258 |
| 27 | light | standard | 1x | texture | 32 | inactive | — | validation | ok | 1.539 | 1.004 | 1.826 | **0.652** | 0.716 | 0.253 | 0.831 | 0.390 | 0.4657 / 0.4746 / 0.1682 |
| 27 | light | standard | 1x | texture | 32 | rest | — | validation | ok | 1.307 | 0.804 | 1.833 | **0.615** | 0.721 | 0.251 | 0.747 | 0.335 | 0.5089 / 0.5180 / 0.1681 |
| 27 | light | standard | 1x | texture | 44 | inactive | — | calibration | ok | 1.795 | 0.919 | 1.386 | **0.512** | 0.748 | 0.272 | 0.915 | 0.395 | 0.4975 / 0.4986 / 0.2119 |
| 27 | light | standard | 1x | texture | 44 | inactive | — | validation | ok | 1.348 | 0.742 | 1.071 | **0.551** | 0.816 | 0.320 | 0.955 | 0.418 | 0.5215 / 0.5152 / 0.2533 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-blue | yes | calibration | ok | 1.692 | 0.271 | 1.386 | **0.160** | 0.543 | 0.006 | — | — | 0.3540 / 0.3935 / 0.2119 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 1.692 | 0.271 | 1.386 | **0.160** | 0.543 | 0.006 | — | — | 0.3540 / 0.3935 / 0.2119 |
| 27 | light | standard | 1x | texture | 44 | inactive-tint-orange-half | yes | calibration | ok | 1.781 | 0.589 | 1.386 | **0.331** | 0.647 | 0.140 | — | — | 0.4209 / 0.4439 / 0.2119 |
| 27 | light | standard | 1x | texture | 44 | rest | — | calibration | ok | 1.592 | 0.827 | 1.388 | **0.520** | 0.785 | 0.267 | 0.912 | 0.365 | 0.5353 / 0.5388 / 0.2118 |
| 27 | light | standard | 1x | texture | 44 | rest | — | validation | ok | 1.291 | 0.662 | 1.071 | **0.513** | 0.833 | 0.312 | 0.958 | 0.393 | 0.5540 / 0.5611 / 0.2535 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-blue | yes | calibration | ok | 0.201 | 0.742 | 1.386 | **3.684** | 1.707 | 1.687 | — | — | 0.1893 / 0.1934 / 0.2119 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.148 | 0.629 | 1.386 | **4.251** | 1.435 | 1.433 | — | — | 0.3377 / 0.3422 / 0.2119 |
| 27 | light | standard | 1x | texture | 44 | rest-tint-orange-half | yes | calibration | ok | 1.423 | 0.842 | 1.386 | **0.592** | 0.969 | 0.910 | — | — | 0.4086 / 0.4161 / 0.2119 |
| 27 | light | standard | 1x | texture | 96 | inactive | — | calibration | ok | 1.838 | 0.940 | 1.389 | **0.512** | 0.795 | 0.272 | 0.982 | 0.423 | 0.4955 / 0.4852 / 0.2147 |
| 27 | light | standard | 1x | texture | 96 | inactive-tint-orange | yes | validation | ok | 1.750 | 0.165 | 1.389 | **0.094** | 0.582 | 0.003 | — | — | 0.3500 / 0.3836 / 0.2147 |
| 27 | light | standard | 1x | texture | 96 | rest | — | calibration | ok | 1.512 | 0.823 | 1.389 | **0.544** | 0.789 | 0.257 | 0.899 | 0.376 | 0.5456 / 0.5592 / 0.2147 |
| 27 | light | standard | 1x | texture | 96 | rest-tint-orange | yes | validation | ok | 0.147 | 0.447 | 1.389 | **3.039** | 1.160 | 1.163 | — | — | 0.3353 / 0.3443 / 0.2147 |
| 27 | light | standard | 1x | texture | 128 | inactive | — | probe | ok | 1.709 | 0.927 | 1.381 | **0.542** | 0.824 | 0.290 | 0.981 | 0.448 | 0.5001 / 0.4829 / 0.2211 |
| 27 | light | standard | 1x | texture | 128 | rest | — | calibration | ok | 1.441 | 0.822 | 1.381 | **0.571** | 0.803 | 0.268 | 0.892 | 0.401 | 0.5639 / 0.5615 / 0.2211 |
| 27 | light | standard | 1x | texture | 130 | inactive | — | holdout | ok | 1.286 | 0.511 | 1.392 | **0.397** | 0.792 | 0.279 | 0.841 | 0.307 | 0.5362 / 0.5254 / 0.2190 |
| 27 | light | standard | 1x | texture | 130 | rest | — | holdout | ok | 1.048 | 0.384 | 1.392 | **0.366** | 0.762 | 0.250 | — | 0.255 | 0.6069 / 0.6163 / 0.2190 |
| 27 | light | standard | 1x | texture | 160 | inactive | — | holdout | ok | 1.734 | 0.984 | 1.401 | **0.567** | 0.855 | 0.295 | 1.001 | 0.470 | 0.5032 / 0.4807 / 0.2258 |
| 27 | light | standard | 1x | texture | 160 | inactive-tint-orange | yes | holdout | ok | 1.723 | 0.106 | 1.400 | **0.061** | 0.632 | 0.001 | — | — | 0.3520 / 0.3803 / 0.2258 |
| 27 | light | standard | 1x | texture | 160 | rest | — | holdout | ok | 1.414 | 0.869 | 1.400 | **0.614** | 0.802 | 0.269 | 0.875 | 0.418 | 0.5779 / 0.5631 / 0.2258 |
| 27 | light | standard | 1x | texture | 160 | rest-tint-orange | yes | holdout | ok | 0.151 | 0.431 | 1.401 | **2.857** | 1.050 | 1.049 | — | — | 0.3396 / 0.3445 / 0.2258 |
| 27 | light | standard | 2x | dom | 32 | inactive | — | validation | ok | 1.900 | 1.984 | 1.814 | **1.044** | 0.709 | 0.474 | — | — | 0.4671 / 0.4721 / 0.1685 |
| 27 | light | standard | 2x | dom | 32 | rest | — | validation | ok | 1.334 | 2.100 | 1.818 | **1.574** | 0.718 | 0.430 | 0.751 | — | 0.5111 / 0.5137 / 0.1684 |
| 27 | light | standard | 2x | dom | 44 | inactive | — | calibration | ok | 1.819 | 1.765 | 1.379 | **0.970** | 0.749 | 0.540 | 0.923 | — | 0.4987 / 0.4949 / 0.2127 |
| 27 | light | standard | 2x | dom | 44 | inactive | — | validation | ok | 1.423 | 1.612 | 1.069 | **1.132** | 0.814 | 0.633 | 0.969 | 0.852 | 0.5257 / 0.5003 / 0.2543 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-blue | yes | calibration | ok | 1.728 | 1.642 | 1.379 | **0.950** | 0.544 | 0.003 | — | — | 0.3550 / 0.3967 / 0.2128 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-orange | yes | calibration | ok | 1.728 | 1.642 | 1.379 | **0.950** | 0.544 | 0.003 | — | — | 0.3550 / 0.3967 / 0.2128 |
| 27 | light | standard | 2x | dom | 44 | inactive-tint-orange-half | yes | calibration | ok | 1.802 | 2.082 | 1.379 | **1.155** | 0.648 | 0.278 | — | — | 0.4218 / 0.4442 / 0.2128 |
| 27 | light | standard | 2x | dom | 44 | rest | — | calibration | ok | 1.568 | 1.689 | 1.379 | **1.077** | 0.784 | 0.500 | 0.910 | — | 0.5375 / 0.5319 / 0.2128 |
| 27 | light | standard | 2x | dom | 44 | rest | — | validation | ok | 1.334 | 1.427 | 1.069 | **1.070** | 0.832 | 0.580 | 0.967 | 0.772 | 0.5596 / 0.5409 / 0.2544 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-blue | yes | calibration | ok | 0.233 | 0.664 | 1.379 | **2.850** | 1.702 | 1.677 | — | — | 0.1898 / 0.1875 / 0.2128 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange | yes | calibration | ok | 0.168 | 1.395 | 1.379 | **8.321** | 1.432 | 1.425 | — | — | 0.3383 / 0.3388 / 0.2128 |
| 27 | light | standard | 2x | dom | 44 | rest-tint-orange-half | yes | calibration | ok | 1.346 | 2.589 | 1.379 | **1.924** | 0.969 | 0.928 | — | — | 0.4100 / 0.4096 / 0.2128 |
| 27 | light | standard | 2x | dom | 96 | inactive | — | calibration | ok | 1.825 | 1.782 | 1.388 | **0.977** | 0.798 | 0.524 | 0.980 | — | 0.4982 / 0.4799 / 0.2153 |
| 27 | light | standard | 2x | dom | 96 | inactive-tint-orange | yes | validation | ok | 1.738 | 1.197 | 1.388 | **0.689** | 0.584 | 0.000 | — | — | 0.3521 / 0.3813 / 0.2153 |
| 27 | light | standard | 2x | dom | 96 | rest | — | calibration | ok | 1.512 | 1.605 | 1.388 | **1.061** | 0.789 | 0.476 | 0.899 | — | 0.5474 / 0.5493 / 0.2153 |
| 27 | light | standard | 2x | dom | 96 | rest-tint-orange | yes | validation | ok | 0.156 | 0.835 | 1.388 | **5.359** | 1.159 | 1.161 | — | — | 0.3356 / 0.3404 / 0.2153 |
| 27 | light | standard | 2x | dom | 128 | inactive | — | probe | ok | 1.700 | 1.890 | 1.381 | **1.112** | 0.826 | 0.538 | 0.980 | — | 0.5015 / 0.4745 / 0.2214 |
| 27 | light | standard | 2x | dom | 128 | rest | — | calibration | ok | 1.436 | 1.674 | 1.381 | **1.165** | 0.802 | 0.482 | 0.891 | — | 0.5641 / 0.5502 / 0.2214 |
| 27 | light | standard | 2x | dom | 130 | inactive | — | holdout | ok | 1.301 | 0.955 | 1.391 | **0.734** | 0.794 | 0.511 | 0.846 | 0.561 | 0.5387 / 0.5167 / 0.2193 |
| 27 | light | standard | 2x | dom | 130 | rest | — | holdout | ok | 1.054 | 0.662 | 1.391 | **0.628** | 0.762 | 0.440 | — | — | 0.6081 / 0.6089 / 0.2193 |
| 27 | light | standard | 2x | dom | 160 | inactive | — | holdout | ok | 1.745 | 1.938 | 1.401 | **1.111** | 0.854 | 0.542 | 1.003 | — | 0.5029 / 0.4739 / 0.2259 |
| 27 | light | standard | 2x | dom | 160 | inactive-tint-orange | yes | holdout | ok | 1.735 | 0.750 | 1.401 | **0.432** | 0.631 | 0.000 | — | — | 0.3518 / 0.3813 / 0.2259 |
| 27 | light | standard | 2x | dom | 160 | rest | — | holdout | ok | 1.413 | 1.704 | 1.401 | **1.206** | 0.801 | 0.482 | 0.874 | — | 0.5791 / 0.5516 / 0.2259 |
| 27 | light | standard | 2x | dom | 160 | rest-tint-orange | yes | holdout | ok | 0.174 | 0.967 | 1.401 | **5.573** | 1.050 | 1.047 | — | — | 0.3399 / 0.3404 / 0.2259 |
| 27 | light | standard | 2x | texture | 32 | inactive | — | validation | ok | 1.900 | 1.145 | 1.814 | **0.603** | 0.709 | 0.270 | — | — | 0.4671 / 0.4732 / 0.1685 |
| 27 | light | standard | 2x | texture | 32 | rest | — | validation | ok | 1.334 | 0.872 | 1.818 | **0.653** | 0.718 | 0.239 | 0.751 | — | 0.5111 / 0.5186 / 0.1684 |
| 27 | light | standard | 2x | texture | 44 | inactive | — | calibration | ok | 1.819 | 0.889 | 1.379 | **0.489** | 0.749 | 0.282 | 0.923 | — | 0.4987 / 0.4997 / 0.2127 |
| 27 | light | standard | 2x | texture | 44 | inactive | — | validation | ok | 1.423 | 0.734 | 1.069 | **0.515** | 0.814 | 0.330 | 0.969 | 0.424 | 0.5257 / 0.5214 / 0.2543 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-blue | yes | calibration | ok | 1.728 | 0.175 | 1.379 | **0.102** | 0.544 | 0.003 | — | — | 0.3550 / 0.3943 / 0.2128 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-orange | yes | calibration | ok | 1.728 | 0.175 | 1.379 | **0.102** | 0.544 | 0.003 | — | — | 0.3550 / 0.3943 / 0.2128 |
| 27 | light | standard | 2x | texture | 44 | inactive-tint-orange-half | yes | calibration | ok | 1.802 | 0.547 | 1.379 | **0.304** | 0.648 | 0.144 | — | — | 0.4218 / 0.4448 / 0.2128 |
| 27 | light | standard | 2x | texture | 44 | rest | — | calibration | ok | 1.568 | 0.853 | 1.379 | **0.544** | 0.784 | 0.260 | 0.910 | — | 0.5375 / 0.5390 / 0.2128 |
| 27 | light | standard | 2x | texture | 44 | rest | — | validation | ok | 1.334 | 0.680 | 1.069 | **0.509** | 0.832 | 0.303 | 0.967 | 0.391 | 0.5596 / 0.5622 / 0.2544 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-blue | yes | calibration | ok | 0.233 | 0.595 | 1.379 | **2.552** | 1.702 | 1.685 | — | — | 0.1898 / 0.1928 / 0.2128 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange | yes | calibration | ok | 0.168 | 0.484 | 1.379 | **2.888** | 1.432 | 1.430 | — | — | 0.3383 / 0.3422 / 0.2128 |
| 27 | light | standard | 2x | texture | 44 | rest-tint-orange-half | yes | calibration | ok | 1.346 | 0.838 | 1.379 | **0.623** | 0.969 | 0.908 | — | — | 0.4100 / 0.4160 / 0.2128 |
| 27 | light | standard | 2x | texture | 96 | inactive | — | calibration | ok | 1.825 | 0.910 | 1.388 | **0.498** | 0.798 | 0.283 | 0.980 | — | 0.4982 / 0.4872 / 0.2153 |
| 27 | light | standard | 2x | texture | 96 | inactive-tint-orange | yes | validation | ok | 1.738 | 0.147 | 1.388 | **0.084** | 0.584 | 0.002 | — | — | 0.3521 / 0.3850 / 0.2153 |
| 27 | light | standard | 2x | texture | 96 | rest | — | calibration | ok | 1.512 | 0.842 | 1.388 | **0.557** | 0.789 | 0.253 | 0.899 | — | 0.5474 / 0.5589 / 0.2153 |
| 27 | light | standard | 2x | texture | 96 | rest-tint-orange | yes | validation | ok | 0.156 | 0.489 | 1.388 | **3.141** | 1.159 | 1.162 | — | — | 0.3356 / 0.3440 / 0.2153 |
| 27 | light | standard | 2x | texture | 128 | inactive | — | probe | ok | 1.700 | 0.893 | 1.381 | **0.526** | 0.826 | 0.299 | 0.980 | — | 0.5015 / 0.4836 / 0.2214 |
| 27 | light | standard | 2x | texture | 128 | rest | — | calibration | ok | 1.436 | 0.827 | 1.381 | **0.576** | 0.802 | 0.267 | 0.891 | — | 0.5641 / 0.5610 / 0.2214 |
| 27 | light | standard | 2x | texture | 130 | inactive | — | holdout | ok | 1.301 | 0.522 | 1.391 | **0.401** | 0.794 | 0.288 | 0.846 | 0.314 | 0.5387 / 0.5258 / 0.2193 |
| 27 | light | standard | 2x | texture | 130 | rest | — | holdout | ok | 1.054 | 0.384 | 1.391 | **0.364** | 0.762 | 0.250 | — | 0.255 | 0.6081 / 0.6157 / 0.2193 |
| 27 | light | standard | 2x | texture | 160 | inactive | — | holdout | ok | 1.745 | 0.950 | 1.401 | **0.544** | 0.854 | 0.305 | 1.003 | — | 0.5029 / 0.4815 / 0.2259 |
| 27 | light | standard | 2x | texture | 160 | inactive-tint-orange | yes | holdout | ok | 1.735 | 0.099 | 1.401 | **0.057** | 0.631 | 0.001 | — | — | 0.3518 / 0.3808 / 0.2259 |
| 27 | light | standard | 2x | texture | 160 | rest | — | holdout | ok | 1.413 | 0.867 | 1.401 | **0.613** | 0.801 | 0.270 | 0.874 | — | 0.5791 / 0.5627 / 0.2259 |
| 27 | light | standard | 2x | texture | 160 | rest-tint-orange | yes | holdout | ok | 0.174 | 0.448 | 1.401 | **2.581** | 1.050 | 1.049 | — | — | 0.3399 / 0.3443 / 0.2259 |

