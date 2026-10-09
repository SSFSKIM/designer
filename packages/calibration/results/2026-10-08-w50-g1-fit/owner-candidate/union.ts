import { isDeepStrictEqual } from 'node:util';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import type { Pin, Row, Capture } from '../owner/referee.ts';

export const cellId=(row:{profile:string;renderer:string;scene:string})=>
  `${row.profile}/${row.renderer}/${row.scene}`;
const rowId=(row:Row)=>`${row.key.profileKey}/${row.key.web.renderer}/${row.key.sceneId}`;
const tupleId=(key:string[])=>`${key[0]}/${key[1]}/${key[2]}`;
export function readPinned(pin:Pin):Buffer {
  if(!pin||typeof pin.path!=='string'||!pin.path.startsWith('/')||!/^\w{64}$/.test(pin.sha256)
    ||!/^[a-f0-9]{64}$/.test(pin.sha256)) throw Error('Expected absolute full-hash pin');
  const bytes=readFileSync(pin.path);
  if(createHash('sha256').update(bytes).digest('hex')!==pin.sha256) throw Error(`Changed pinned bytes: ${pin.path}`);
  return bytes;
}
export const readJson=(pin:Pin):any=>JSON.parse(readPinned(pin).toString());
export const samePin=(a:Pin,b:Pin)=>a?.path===b?.path&&a?.sha256===b?.sha256;
export const absolutePin=(pin:Pin,repo:string):Pin=>({path:resolve(repo,pin.path),sha256:pin.sha256});

/** Membership only: no pixels, owner metrics or held current rows substitute for candidates.
 * Other admitted canonical statistics may use rows outside the original owner dependency
 * context; those records stay in the physical union but do not invent new owner members. */
export function selectOwnerUnion(currentRows:Row[],dependencies:any,cohort:Pin[],gate:any,exposure:any,repo='/') {
  const cohortHashes=cohort.map(pin=>pin.sha256).sort();
  if(new Set(cohort.map(pin=>pin.path)).size!==cohort.length||new Set(cohortHashes).size!==cohort.length) {
    throw Error('Duplicate candidate cohort');
  }
  const needed=new Set(currentRows.map(rowId));
  if(needed.size!==currentRows.length) throw Error('Duplicate owner dependency context');
  const all=new Map<string,any>();
  let excludedBaselineRecords=0;
  for(const [phase,bundle] of [['gate',gate],['exposure',exposure]] as const) {
    if(bundle?.status!=='CAPTURED'||!Array.isArray(bundle.captures)
      ||!isDeepStrictEqual(bundle.candidateSha256s,cohortHashes)) throw Error('Capture bundle candidate cohort differs');
    const allowed=new Set((phase==='gate'?dependencies.gateKeys:dependencies.exposureKeys).map(tupleId));
    for(const record of bundle.captures) {
      if(record.sceneSource!=='canonical') continue;
      if(record.lane==='current') {excludedBaselineRecords++;continue;}
      if(record.lane!=='candidate'||!cohort.some(pin=>samePin(absolutePin(pin,repo),absolutePin(record.candidate,repo)))) {
        throw Error('Canonical record is not the frozen candidate');
      }
      const key=cellId(record);
      if(!allowed.has(key)) throw Error(`Canonical record outside ${phase} membership: ${key}`);
      if(all.has(key)) throw Error(`Duplicate candidate union record: ${key}`);
      if(rowId(record.row)!==key) throw Error('Record identity differs from raw matrix row');
      all.set(key,record);
    }
  }
  const missing=[...needed].filter(key=>!all.has(key));
  if(missing.length) throw Error(`Owner union missing candidate dependencies (no held-row fill): ${missing.join(',')}`);
  const ownerKeys=dependencies.ownerUnionKeys.map(tupleId);
  if(new Set(ownerKeys).size!==ownerKeys.length||ownerKeys.some((key:string)=>!needed.has(key))) {
    throw Error('Owner union keys differ from original owner dependency context');
  }
  return {records:[...all.values()].filter(record=>needed.has(cellId(record))),
    allCanonicalRecords:[...all.values()],excludedBaselineRecords,
    excludedNonownerCanonicalKeys:[...all.keys()].filter(key=>!needed.has(key)).sort()};
}

/** Check the endpoint that actually drew, not merely the requested declaration. The full
 * endpoint files have already passed the production candidate-document reader. */
export function checkDrawnIdentity(record:any,envelope:any,candidate:any,scene:any) {
  const page=envelope?.page;
  const scheme=record.profile.includes('-dark-')?'dark':'light';
  const pose=scene.state==='inactive'?'receded':'active';
  const endpoint=candidate.endpoints[`${pose}.${scheme}`];
  if(!endpoint||envelope.fallback||envelope.problems?.length||page?.problems?.length
    ||page?.sceneId!==record.scene||page.requestedRenderer!==record.renderer
    ||page.windowActivation!==(pose==='receded'?'inactive':'active')||page.colorScheme!==scheme
    ||page.materialMode!=='candidate'||page.candidateDocument?.mode!=='candidate'
    ||page.candidateDocument.declarationSha256!==candidate.declaration.sha256.slice(0,12)) {
    throw Error('Drawn capture identity differs from candidate/scene');
  }
  for(const field of ['profileKey','resolvedMaterialSha256']) {
    if(record.endpoint?.[field]!==endpoint[field]) throw Error('Drawn record endpoint differs');
  }
  if(record.endpoint.path!==undefined&&!samePin(record.endpoint,endpoint)) throw Error('Drawn endpoint file pin differs');
  if(!Array.isArray(page.groups)||!page.groups.length) throw Error('Drawn group population missing');
  for(const group of page.groups) {
    if(group.state?.activeRenderer!==record.renderer||group.state?.health!=='ok') throw Error('Drawn group tier/health differs');
  }
  for(const material of [page.material,...page.groups.map((group:any)=>group.state.materialDocument)]) {
    if(material?.tuned!==false||material.glassTintAmount!==candidate.position
      ||material.profileKey!==endpoint.profileKey||material.resolvedMaterialSha256!==endpoint.resolvedMaterialSha256) {
      throw Error('Drawn endpoint/digest/position differs');
    }
  }
}

/** Authenticate only raw canonical record data. Matrices are deduplicated by full pin and
 * every recorded row is compared structurally with its immutable matrix member. */
export function admittedCandidateRows(records:any[],resolver:any,declaration:any,currentCaptures:Record<string,Capture>,repo='/') {
  const matrices=new Map<string,{pin:Pin;rows:Map<string,Row>}>();
  const rows:Row[]=[],captures:Record<string,Capture>={};
  for(const record of records) {
    const key=cellId(record),pin=record.matrix as Pin;
    let matrix=matrices.get(pin.path);
    if(matrix&&!samePin(matrix.pin,pin)) throw Error('Two hashes for one candidate matrix');
    if(!matrix) {
      const raw=readJson(pin);
      if(raw.schemaVersion!==5||!Array.isArray(raw.cells)) throw Error('Candidate matrix is not schema5');
      const byKey=new Map<string,Row>();
      for(const row of raw.cells) {
        const identity=rowId(row);
        if(byKey.has(identity)) throw Error('Duplicate row in candidate matrix');
        byKey.set(identity,row);
      }
      matrix={pin,rows:byKey};matrices.set(pin.path,matrix);
    }
    const actual=matrix.rows.get(key);
    if(!actual||!isDeepStrictEqual(actual,record.row)) throw Error('Capture record row differs from pinned matrix');
    const binding=resolver.resolve(actual);
    if(!binding) throw Error('Live owner row is not candidate mode');
    const candidate={declaration:absolutePin(record.candidate,repo),position:binding.position,endpoints:binding.endpoints};
    if(!samePin(candidate.declaration,binding.declaration)) throw Error('Record candidate differs from raw matrix stamp');
    const metadata=readJson(record.artifacts.cell);
    if(!isDeepStrictEqual(metadata,actual.key.web)) throw Error('Canonical metadata differs from matrix web record');
    const scene=declaration.scenes.find((item:any)=>item.id===record.scene);
    if(!scene) throw Error('Canonical scene absent from original declaration');
    checkDrawnIdentity(record,readJson(record.artifacts.report),candidate,scene);
    const originals=currentCaptures[key];
    if(!originals) throw Error(`Missing original native/backdrop binding: ${key}`);
    rows.push(actual);
    captures[key]={web:record.artifacts.png,metadata:record.artifacts.cell,
      native:originals.native,backdrop:originals.backdrop,documents:resolver.documents(actual)};
  }
  return {rows,captures,matrices:[...matrices.values()].map(value=>value.pin)};
}
