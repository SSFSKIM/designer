import {readFileSync, realpathSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,relative,isAbsolute} from 'node:path';
import {colourlessTintEvidence, type SceneSpec, type Manifest} from '../../../cli/gates.ts';

export interface NativeRequest {
  profile: string;
  scenes: string[];
  sets: string[];
  native: {scene: string; path: string; sha256: string}[];
}

/** Select the original tree, not the worktree copy; compare and its capture child inherit it. */
export function selectFixtures(request: NativeRequest & {fixtures:{path:string;manifest:{path:string;sha256:string}}}) {
  const root=realpathSync(request.fixtures.path);
  if(!request.native.length || request.native.some(pin=>
    realpathSync(pin.path)!==realpathSync(resolve(root,request.profile,pin.scene+'.png')))) {
    throw Error('Original native pins differ from selected fixture root');
  }
  const path=realpathSync(request.fixtures.manifest.path);
  if(path!==resolve(root,'manifest.json'))throw Error('Native manifest pin names another fixture root');
  const bytes=readFileSync(path);
  if(createHash('sha256').update(bytes).digest('hex')!==request.fixtures.manifest.sha256) {
    throw Error('Changed native manifest pin');
  }
  process.env.VITREA_FIXTURES=root;
  return {root,manifest:JSON.parse(bytes.toString()) as Manifest};
}

/** Only selected original native pins may be read. This is not a global tint certification. */
export function admitNative(spec: SceneSpec, manifest: Manifest, root: string, request: NativeRequest) {
  const profiles=manifest.profiles.filter(p=>p.profileKey===request.profile);
  if(profiles.length!==1 || !request.scenes.length || new Set(request.scenes).size!==request.scenes.length ||
     request.native.length!==request.scenes.length || new Set(request.native.map(p=>p.scene)).size!==request.scenes.length) {
    throw Error('Invalid selected native membership');
  }
  const profile=profiles[0]!;
  const selected=request.scenes.map(id=>{
    const scene=spec.scenes.filter(s=>s.id===id);
    const fixtures=profile.fixtures.filter(f=>f.sceneId===id);
    const pin=request.native.find(p=>p.scene===id);
    const roles=Object.entries(spec.split).filter(([,ids])=>ids.includes(id)).map(([role])=>role);
    if(scene.length!==1 || fixtures.length!==1 || !pin || roles.length!==1 ||
       !request.sets.includes(roles[0]!) || fixtures[0]!.fixtureSet!==roles[0] ||
       fixtures[0]!.materialRendered!==true) throw Error('Selected native identity/split/material differs');
    const path=realpathSync(resolve(root,fixtures[0]!.file));
    const within=relative(realpathSync(root),path);
    if(within.startsWith('..') || isAbsolute(within))throw Error('Native pin escapes fixture root');
    if(path!==realpathSync(pin.path) || !/^[0-9a-f]{64}$/.test(pin.sha256)) throw Error('Native pin path differs');
    return {scene:scene[0]!,fixture:fixtures[0]!,pin,path};
  });
  // Validate the entire path population before opening any PNG. Byte identity uses the
  // original references, never a newly minted hash that could bless replaced evidence.
  for(const item of selected) {
    if(createHash('sha256').update(readFileSync(item.path)).digest('hex')!==item.pin.sha256) {
      throw Error('Original native pin changed');
    }
  }
  const boundedSpec={...spec,scenes:selected.map(s=>s.scene)};
  const boundedManifest={...manifest,profiles:[{...profile,fixtures:selected.map(s=>s.fixture)}]};
  const missingTint=colourlessTintEvidence(boundedSpec,boundedManifest,root);
  if(missingTint) throw Error('Selected native tint seeds produced identical bytes');
  const groups=new Map<string,string[]>();
  for(const {scene} of selected) {
    if(scene.tint===undefined || scene.state==='inactive')continue;
    const key=`${scene.background}|${scene.component}|${scene.state}`;
    groups.set(key,[...(groups.get(key)??[]),scene.id]);
  }
  const comparable=[...groups.values()].filter(g=>g.length>=2);
  return {schema:'w50-selected-native-admission-1',status:'ADMITTED',profile:request.profile,
    native:request.native,scope:'selected-run-only',
    tint:{status:comparable.length?'NO_DUPLICATE_IN_SELECTED_PAIRS':'NOT_COMPARABLE',
      comparedGroups:comparable,inactiveExempt:selected.filter(s=>s.scene.tint!==undefined &&
        s.scene.state==='inactive').map(s=>s.scene.id)}};
}
