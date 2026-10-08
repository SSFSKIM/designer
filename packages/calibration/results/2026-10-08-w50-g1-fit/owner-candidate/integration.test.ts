import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync,rmSync,readFileSync } from 'node:fs';
import { dirname,join,resolve,relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { PNG } from 'pngjs';
import { candidateFixture,put,hash } from './identity.test.ts';
import { prepareCurrent } from '../owner/api.ts';
import { executeRequest } from './bridge.ts';
const home=dirname(fileURLToPath(import.meta.url));
const repo=resolve(home,'../../../../..');
const prefix='packages/calibration/results/2026-10-08-w50-g1-fit/owner/';

test('exposure bridge evaluates untouched real candidate rows against sealed synthetic current evidence',()=>{
  const dir=mkdtempSync(join(home,'.synthetic-'));
  const saved={...process.env};
  try {
    const f=candidateFixture(dir,.25,'candidate25'),f50=candidateFixture(dir,.5,'candidate50');
    const cohort=[f.pin,f50.pin].map(pin=>({...pin,path:relative(repo,pin.path)}));
    const scene='light-solid__box__rest',profile=f.row.key.profileKey,key=`${profile}/webgpu/${scene}`;
    const decl=put(dir,'scenes.json',{canvas:{width:4,height:4},components:{box:{kind:'rrect',size:[2,2]}},
      scenes:[{id:scene,component:'box',background:'light-solid',state:'rest'}],split:{calibration:[scene]}});
    const image=PNG.sync.write({width:4,height:4,data:Buffer.alloc(64,255)} as PNG);
    const png=put(dir,'native.png',image),backdrop=put(dir,'backdrop.png',image),web=put(dir,'web.png',image);
    const matrix=(name:string,a:string,b:string,level:number)=>{
      const active=a.padEnd(64,'0'),receded=b.padEnd(64,'0');
      const row={...f.row,key:{...f.row.key,sceneId:scene,web:{renderer:'webgpu',samplingBackend:'css-backdrop',
        sceneId:scene,pixelSize:[4,4],capturePath:`viewport=4x4, deviceScaleFactor=1, materialProfile=a sha256:${active.slice(0,12)} recededProfile=r sha256:${receded.slice(0,12)}`}},
        material:{interiorMeanNative:{value:.2},interiorMeanWeb:{value:level}}};
      return {row,input:{matrix:put(dir,name,{schemaVersion:5,cells:[row]}),documents:{a:active,r:receded}}};
    };
    const current=matrix('current.json','b2d074d2df24','940384c06f73',.21);
    const original=matrix('reference.json','d0219cd684bf','f0b36a71772a',.2);
    const currentCapture={web,native:png,backdrop,metadata:put(dir,'current-meta.json',current.row.key.web),
      documents:current.input.documents};
    const inputs={declaration:decl,current:[current.input],references:[original.input],captures:{[key]:currentCapture},
      referenceCaptures:{},python:'/not-executed-in-this-cell'};
    const report=prepareCurrent(inputs).current;
    const closurePath=resolve(repo,prefix+'r3/source-closure.json'),closureBytes=readFileSync(closurePath);
    const frozenSourceClosure={path:closurePath,sha256:hash(closureBytes)};
    const closure=JSON.parse(closureBytes.toString());
    const sourcePins=Object.fromEntries(closure.sources.filter((p:any)=>
      ['api.ts','referee.ts','intrinsic.ts','source.ts'].some(n=>p.path===prefix+n))
      .map((p:any)=>[p.path,{path:resolve(repo,p.path),sha256:p.sha256}]));
    const tuple=[profile,'webgpu',scene,'owner-contracts'];
    const inventory=put(dir,'inventory.json',{cells:[{profile,renderer:'webgpu',scene,statistic:'owner-contracts'}]});
    const config=put(dir,'config.json',{schema:'w50-owner-candidate-config-1',ownerInputs:put(dir,'inputs.json',inputs),
      completedOwnerReferences:put(dir,'report-current.json',report),originalInventory:inventory,
      frozenSourceClosure,sourcePins,python:'/live-guarded-not-used',runtimeClosure:put(dir,'runtime.json',{sources:[]})});
    const dependencies={gateKeys:[],exposureKeys:[tuple],ownerUnionKeys:[tuple]};
    const root=put(dir,'root.json',{repo,inputs:[config],references:inventory,phaseDependencies:dependencies});
    const intrinsic=put(dir,'intrinsic.json',{candidateDeclarations:cohort,recededRecords:{}});
    const gateBatch=put(dir,'gate-batch.json',{phase:'gate',cohort,ownerIntrinsicRecords:intrinsic});
    const gateContract=put(dir,'gate-contract.json',{phase:'gate',cohort,batch:gateBatch,executionRootSha256:root.sha256});
    const gateCaptures={status:'CAPTURED',candidateSha256s:cohort.map(p=>p.sha256).sort(),captures:[]};
    const gateResult=put(dir,'gate.result.json',{contractSha256:gateContract.sha256,captures:gateCaptures,
      report:{status:'PASS_EXPOSED_OWNER_PENDING',ownerChecks:'PENDING_FULL_UNION',candidateSha256s:gateCaptures.candidateSha256s}});
    const batch=put(dir,'exposure-batch.json',{phase:'exposure',cohort,ownerIntrinsicRecords:intrinsic});
    const contract=put(dir,'exposure-contract.json',{phase:'exposure',cohort,batch,gateContract,gateResult,
      executionRootSha256:root.sha256});
    const claim=put(dir,'exposure-contract.json.started.json',{phase:'exposure',contractSha256:contract.sha256,
      batchSha256:batch.sha256,output:dir,gpuLease:'synthetic-live-claim',numericalAdmission:{admitted:true}});
    const row={...f.row,key:{...f.row.key,sceneId:scene,web:{...f.row.key.web,sceneId:scene,pixelSize:[4,4],
      samplingBackend:'css-backdrop'}},material:{interiorMeanNative:{value:.2},interiorMeanWeb:{value:.22}}};
    const endpoint=f.candidate.endpoints['active.dark'];
    const material={profileKey:endpoint.profileKey,resolvedMaterialSha256:endpoint.resolvedMaterialSha256,
      glassTintAmount:.25,tuned:false};
    const page={sceneId:scene,requestedRenderer:'webgpu',windowActivation:'active',colorScheme:'dark',materialMode:'candidate',
      candidateDocument:{mode:'candidate',declarationSha256:f.pin.sha256.slice(0,12)},material,
      groups:[{state:{activeRenderer:'webgpu',health:'ok',materialDocument:material}}]};
    const record={profile,renderer:'webgpu',scene,sceneSource:'canonical',lane:'candidate',candidate:cohort[0],endpoint,
      matrix:put(dir,'candidate-matrix.json',{schemaVersion:5,cells:[row]}),row,
      artifacts:{png:web,cell:put(dir,'candidate-meta.json',row.key.web),report:put(dir,'candidate-report.json',{page})}};
    const snapshot=put(dir,'snapshot.json',{schema:'w50-owner-live-capture-union-1',phase:'exposure',config,
      executionRoot:root,contract,batch,claim,gateResult,cohort,ownerIntrinsicRecords:intrinsic,output:dir,
      ownerUnionKeys:[tuple],expectedExposureCells:inventory? [{profile,renderer:'webgpu',scene,statistic:'owner-contracts'}]:[],
      unionExpectedCells:[{profile,renderer:'webgpu',scene,statistic:'owner-contracts'}],gateCaptures,
      exposureCaptures:{...gateCaptures,captures:[record]}});
    Object.assign(process.env,{W50_OWNER_LIVE_CONFIG:config.path,W50_OWNER_LIVE_CONFIG_SHA256:config.sha256,
      W50_OWNER_LIVE_ROOT_SHA256:root.sha256,W50_OWNER_LIVE_SNAPSHOT_SHA256:snapshot.sha256});
    const before=JSON.stringify(row);
    const result=executeRequest({snapshot,config});
    assert.equal(result.cells[key].L1.candidate,.22);assert.equal(result.cells[key].L1.current,.21);
    assert.equal(result.cells[key].L1.reference,.2);assert.equal(result.cells[key].L1.verdict,'failure');
    assert.equal(result.liveUnion.scope,'FULL_SAME_CANDIDATE_UNION; metric evidence only, full judge owns verdict');
    assert.equal(result.intrinsic.X76['0.25'].state,'UNMEASURED');
    assert.equal(Object.hasOwn(result,'status'),false);assert.equal(JSON.stringify(row),before);
    assert.deepEqual(JSON.parse(JSON.stringify(result)),result);
  }finally{
    for(const key of Object.keys(process.env)) if(!(key in saved)) delete process.env[key];
    Object.assign(process.env,saved);rmSync(dir,{recursive:true});
  }
});
