"""Write the initial machine declaration and pins, refusing to overwrite evidence."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
G0 = HERE.parent / '2026-09-26-w39-g0-colour-edge-bed'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
closure = dict(
    schema='w41-closure-1', boundsDeclarationSha256=sha(HERE / 'bounds-declaration.txt'),
    supersededDeclarationHashes=[], charterRevision='9762ef9c',
    endpoints=['light-active', 'light-inactive', 'dark-active', 'dark-inactive'],
    scales=[1, 2], g0Roles=['calibration'],
    body=dict(deepCSS=6, minimumPopulation=4, repeatCount=7,
              statistic='median of seven per-run channel deep medians',
              bar='0.5 + 0.5 * ptp(run statistics)',
              neutralKnots=[40,56,72,88,104,128,150],
              neutralOrdinates={'light-active':[152,160,168,176,183,195,205],
                               'light-inactive':[150,157,164,171,178,188,197],
                               'dark-active':[69,83,96,108,119,134,146],
                               'dark-inactive':[60,74,87,100,111,127,140]},
              neutralInterpolation='encoded linear; end-segment continuation then clip'),
    families={
        'B0':dict(name='H3',chromaticParametersPerEndpoint=6,fit=False,space='decoded F then matrix',status='historical baseline'),
        'B1':dict(name='E3',chromaticParametersPerEndpoint=3,nodes=[63,93,118],bounds=[0,3],space='encoded luma/chroma',interpolation='linear; held outside',solver='certified LP'),
        'B2':dict(name='EH6',chromaticParametersPerEndpoint=6,nodes=[0,60,120,180,240,300],bounds=[0,3],space='encoded luma/chroma; OKLab input hue',interpolation='periodic linear',solver='certified LP'),
        'B3':dict(name='O12',chromaticParametersPerEndpoint=12,nodeCubes=[.05,.11,.18],bounds=[-8,8],space='OKLab',interpolation='linear; held matrix outside; neutral tone end segment',solver='local multistart'),
        'S0':dict(parameters=0,expression='B(x)',landable=False),
        'S1':dict(parameters=4,mBounds=[0,1],expression='B(m*x+(1-m)*referenceFrameMean)',landable=False),
        'S2':dict(parameters=6,mBounds=[0,1],activeAmplitudeBounds=[-255,255],inactiveAmplitude=0,expression='clip(S1+a*(y-yc)/height)',landable=False),
        'G':dict(parameters=7,widthBounds=[0,2],widthUnit='device px',betaBounds=[0,1],activeGammaConstraint='abs(gamma)<=1-beta',inactiveGamma=0,normalisation='maximum over all unit normals'),
        'G-css':dict(parameters=7,widthBounds=[0,2],widthUnit='CSS px',otherwise='G'),
        'G-curvature':dict(parameters=8,rhoBoundsCSS=[-22,22],arcCoverage='clip(A*(1+rho/R),0,1)',R='nominal circle radius or rrect declared 22 CSS px',straight='A'),
        'M0':dict(parameters=8,perEndpoint=2,tBounds=[0,3],kBounds=[-255,255],space='encoded',expression='clip(t*b+k)',combinedWithG=15),
        'M1':dict(parameters=32,perEndpoint=8,nodes=[40,56,72,88,104,128,150,255],ordinateBounds=[0,255],monotone=True,space='encoded',interpolation='linear; end segment continued then clip',combinedWithG=39),
        'M2':dict(parameters=36,extraDarkParameters=4,kappaBounds=[0,16],Y0Bounds=[0,1],space='M1 plus linear-light contextual correction',gamut='held-luma chroma compression',combinedWithG=43)},
    strip=dict(scenes=['v90-c-c44__rest','v270-c-c44__rest','v90-c-c44__inactive','v270-c-c44__inactive'],widthCSS=48,minimumInwardCSS=6,arcs=False,referenceDomainCodes=[121,135],rowStatistic='per-run row median, then seven-run median',diagnostic='row mean reproduces memo',mean='complete no-glass frame',scales=[1,2],postReadMaskChanges=False),
    stroke=dict(outerCSS=4,shellRange='range(0,4*scale)',minimumPopulation=4,angularBins=16,straightSides=['top','bottom','left','right'],interiorWitnessShells=[-1,-2,-3],boundary='diagnostic only',quadrature=16,sensitivityQuadrature=32,referenceInterpolation='pixel-centred bilinear; edge held',compositeSpace='encoded',support='outside supplied path only',order=['inactive','active with shipped shadow held']),
    shadowControls=dict(outer='all required bins beyond band with zero inactive departure; shells 2..4*scale-1 and zero straight shell1 remain controls',additional=dict(scheme='dark',pose='active',part='straight',side='top',backgrounds=['g128','g255']),lightActiveTop='stroke bin, NOT shadow-only',claim='conditional on held model, not native shadow identification'),
    censor=dict(low=5,high=250,constraint='one-sided rail; uncensored channels retained; bridges retained',statuses=['measured','censored-bound-satisfied','UNMEASURED'],failedRail='UNMEASURED with binding boundFailure',heldout='any censored channel makes cell UNMEASURED for held-out coverage',w39FitPopulation=dict(cells=404,channels=1212),w41FitPopulation=dict(cells=408,uncensoredChannels=1220,railBounds=4)),
    scoring=dict(bound='max(1,bar)',edge='mean absolute pixel error per channel/bin; absolute before spatial reduction',deep='absolute median error',repeats='all seven',mass='equal cell, equal channel/bin within cell',report=['least-squares','minimax','worst-channel','all-channel','rank','singular values','convergence']),
    optimisation=dict(seed=4100,starts=16,baseline='identity/zero',ls=dict(max_nfev=3000,ftol=1e-10,xtol=1e-10,gtol=1e-10),minimax=dict(method='SLSQP epigraph',maxiter=3000,ftol=1e-10),nonlinearClaim='LOCAL',lpGapCodes=1e-5),
    survival=dict(roles=['calibration','validation'],everyRequiredComparison=True,bound='max(1,bar)'),
    resolution=dict(bound='max(3,sum of bars)',belowEveryDiscriminator='insufficient resolution',spatial='calibration finding only; no holdout referee'),
    receipt=dict(log='packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/wave-identification-receipt.jsonl',oneExposure=True,failedAttemptSpends=True,bind=['scenes','split','inventory','declaration','closure','instrument and runner sources','numerical candidates and frozen predictions','renderer revision and source hashes','renderer configuration','frozen rendered predictions'],capture='web-plannable held-out cells inside receipt; verify against frozen rendered predictions',nativeOnly=['grey255 bottom pair'],both=['circular160x96 pair','witness200x44 pair','six held-out colours'],g0DryRun='calibration stand-in, scratch receipt, synthetic capture backend, no browser'),
    noShippedChanges=True)
pins=dict(schema='w41-pins-1',archive=dict(tag='w39-archive',assetSha256='489db938a1e234a772ba7223d24fbaf76d137ef5d9e5b2421ed84a86894426b5',bytes=13658148,inventorySha256='58329732f947d42cd5e1518962016191faaa79d89b7089c6dadf5724dde35f61'),boundsDeclarationSha256=closure['boundsDeclarationSha256'],files={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'apps/reference-apple/scenes-w39-colour-edge.json',G0/'split.json',G0/'wave.py',G0/'w39_readers.py',G0/'w39_archive.py',ROOT/'docs/doperpowers/specs/2026-09-27-w41-archive-reread.md']})
for name,data in [('closure.json',closure),('pins.json',pins)]:
    with (HERE/name).open('x') as f: f.write(json.dumps(data,indent=2,allow_nan=False)+'\n')
print(closure['boundsDeclarationSha256'])
