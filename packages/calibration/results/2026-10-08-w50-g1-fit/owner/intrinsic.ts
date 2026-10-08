import { SHIPPED_MATERIAL_PROFILE_DOCUMENTS, mergeMaterialProfiles } from '@vitreajs/vitrea-web';
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from '@vitrea/renderer-webgpu';
import { readCandidateDocument } from '../../../scripts/candidate-document.ts';
import { isDeepStrictEqual } from 'node:util';
import { pinnedBytes, checkOpacity, checkInheritance, assertDocumentPair, inheritanceMethods, type Pin, type Row } from './referee.ts';

export interface IntrinsicInputs {
  /** The two whole candidate declarations, at 0.25 and 0.5, including unchanged light endpoints. */
  candidateDeclarations: Pin[];
  recededRecords: Record<string, {
    /** Original frozen-current endpoint documents, in their declared roles (not fit baselines). */
    beforeActive: Pin; beforeReceded: Pin;
    /** JSON RecededMethodRecords envelope bound to the candidate receded endpoint's full SHA. */
    methods: Pin;
    /** JSON ActiveFittingRecords envelope bound to the candidate active endpoint's full SHA.
     * Retained inventory is copied unchanged from beforeActive.entries; newly fitted records
     * state measured status, resolved candidate value and nonempty source-method lines.
     * This is fitting evidence, separate from image statistics. A pinned bare entries map is
     * insufficient: it establishes byte integrity but not applicability to this candidate. */
    activeEntries: Pin;
  }>;
}
const unread = (reason:string) => ({state:'UNMEASURED',reason});
export function candidateIntrinsics(input:IntrinsicInputs,rows:Row[],currentRows:Row[] = []) {
  if(input.candidateDeclarations.length!==2) return {
    X75:unread('Both fixed-position candidate declarations required'),
    X76:unread('Both fixed-position candidate declarations required'),
  };
  const candidates=input.candidateDeclarations.map(pin=>{
    pinnedBytes(pin);
    return readCandidateDocument(pin.path);
  });
  const positions=candidates.map(c=>c.document.glassTintAmount);
  if(!positions.includes(.25)||!positions.includes(.5)||new Set(positions).size!==2) {
    throw new Error('Candidate declarations must name exactly glass0.25 and glass0.5');
  }
  const endpoints=new Map(candidates.flatMap(c=>Object.values(c.endpoints).map(e=>[e.path,e.sha256] as const)));
  for(const row of rows) {
    // Candidate endpoint membership is checked within this row's position AND role.
    const position=row.key.profileKey.endsWith('-glass0.25')?.25:row.key.profileKey.endsWith('-glass0.5')?.5:undefined;
    if(position===undefined) continue;
    const candidate=candidates.find(c=>c.document.glassTintAmount===position)!;
    const scheme=row.key.profileKey.includes('-dark-')?'dark':'light';
    assertDocumentPair(row,candidate.endpoints[`active.${scheme}`].sha256,
      candidate.endpoints[`receded.${scheme}`].sha256);
  }
  const posed:Record<string,any>={};
  for(const shipped of SHIPPED_MATERIAL_PROFILE_DOCUMENTS) {
    const replacement=candidates.find(c=>c.document.glassTintAmount===shipped.glassTintAmount);
    const document=replacement?.document??shipped;
    for(const scheme of ['light','dark'] as const) {
      posed[`${shipped.name}/${scheme}/active`]=document.active[scheme].patch;
      posed[`${shipped.name}/${scheme}/receded`]=mergeMaterialProfiles(
        document.active[scheme].patch as never,document.receded[scheme].patch as never);
    }
  }
  if(Object.keys(posed).length!==12) throw new Error('X75 shipped endpoint population changed');
  const X76:Record<string,any>={};
  for(const candidate of candidates) {
    const position=String(candidate.document.glassTintAmount);
    const records=input.recededRecords[position];
    if(!records) {X76[position]=unread('Pinned receded inheritance records missing');continue;}
    const current=currentRows.filter(r=>r.key.profileKey.endsWith(`-dark-standard-glass${position}`));
    if(!current.length) {X76[position]=unread('Pinned original-current document pair missing');continue;}
    for(const row of current) assertDocumentPair(row,records.beforeActive.sha256,records.beforeReceded.sha256);
    const beforeActive=JSON.parse(pinnedBytes(records.beforeActive).toString());
    const beforeReceded=JSON.parse(pinnedBytes(records.beforeReceded).toString());
    const recededRecords=JSON.parse(pinnedBytes(records.methods).toString());
    const activeRecords=JSON.parse(pinnedBytes(records.activeEntries).toString());
    assertEndpointIdentity(beforeActive,Number(position),'active');
    assertEndpointIdentity(beforeReceded,Number(position),'receded');
    const activeEndpoint=candidate.endpoints['active.dark'];
    const recededEndpoint=candidate.endpoints['receded.dark'];
    const active=JSON.parse(pinnedBytes(activeEndpoint).toString());
    const receded=JSON.parse(pinnedBytes(recededEndpoint).toString());
    assertEndpointIdentity(active,Number(position),'active');
    assertEndpointIdentity(receded,Number(position),'receded');
    const activeResolved=withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,active.patch);
    const applicability=checkRecordApplicability({activeSha256:activeEndpoint.sha256,
      recededSha256:recededEndpoint.sha256,activeResolved,
      beforeResolved:withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,beforeActive.patch),
      beforePatch:beforeActive.patch,activePatch:active.patch,
      beforeEntries:beforeActive.entries??{},activeRecords,recededRecords});
    if(applicability.state!=='MEASURED') {X76[position]=applicability;continue;}
    X76[position]={...checkFamilyInheritance({
      activeResolved,activePatch:active.patch,
      activeEntries:applicability.activeEntries,beforePatch:beforeReceded.patch,beforeEntries:beforeReceded.entries??{},
      candidatePatch:receded.patch,methods:applicability.methods,
    }),applicability,provenance:{records,active:activeEndpoint,receded:recededEndpoint},
      beforeActiveProfile:beforeActive.profileKey};
  }
  return {X75:checkOpacity(posed),X76,provenance:{candidateDeclarations:input.candidateDeclarations,
    endpointHashes:Object.fromEntries(endpoints)}};
}

export interface ActiveFittingRecords {
  endpointSha256: string;
  retainedMeasuredEntries: Record<string,any>;
  fittedEntries: Record<string,{status:'measured';value:unknown;method:string[]}>;
}
export interface RecededMethodRecords {
  endpointSha256: string;
  methods: Record<string,string[]|{held:string[]}>;
}
const flatten=(node:any,prefix='',out:Record<string,any>={}):Record<string,any>=>{
  for(const [key,value] of Object.entries(node)) {
    const path=prefix?`${prefix}.${key}`:key;
    if(value&&typeof value==='object'&&!Array.isArray(value)) flatten(value,path,out);
    else out[path]=value;
  }
  return out;
};
/** The before pair is frozen by role/hash before its records may justify inherited leaves. */
export function assertEndpointIdentity(document:any,position:number,pose:'active'|'receded') {
  const key=`apple-macos-27.0-1x-dark-standard-glass${position}${pose==='receded'?'-receded':''}`;
  if(document.profileKey!==key
    || (document.glassTintAmount!==undefined && document.glassTintAmount!==position)
    || (pose==='active' && document.kind==='receded-endpoint')
    || (pose==='receded' && document.kind!==undefined && document.kind!=='receded-endpoint')) {
    throw new Error('Endpoint identity does not match dark position/pose');
  }
}
/** DL5o (a). A document sealed before X76 (the shipped 0.5 dark pair, `0eac5b294cc2` /
 * `5cec8c961201`) keys its provenance entries by FAMILY rather than by leaf. An entry is
 * family-keyed when it records a measurement (status `measured…`) and cannot be a leaf record:
 * its key names no flattened material leaf, or its value is a plain object, which a flattened
 * leaf never is. Every other entry keeps X76's original leaf-keyed reading. */
const isPlainObject=(value:unknown):value is Record<string,unknown>=>
  value!==null&&typeof value==='object'&&!Array.isArray(value);
export function partitionEntries(entries:Record<string,any>,leaves:readonly string[]) {
  const leafEntries:Record<string,any>={},familyEntries:Record<string,any>={};
  for(const [key,entry] of Object.entries(entries)) {
    const family=typeof entry?.status==='string'&&entry.status.startsWith('measured')
      &&(!leaves.includes(key)||isPlainObject(entry.value));
    (family?familyEntries:leafEntries)[key]=entry;
  }
  return {leafEntries,familyEntries};
}
/** A leaf falls under a family when one of the family's names (its own key, and every key of
 * its `value` and `previous` objects) is the leaf, a material node above it, or its trailing
 * path. Deliberately inclusive: it decides whether a moved leaf refuses the family's hold. */
export function fallsUnder(leaf:string,key:string,entry:any) {
  const names=[key,...[entry.value,entry.previous].filter(isPlainObject).flatMap(o=>Object.keys(o))];
  return names.some(name=>leaf===name||leaf.startsWith(name+'.')||leaf.endsWith('.'+name));
}
/** DL5o (a): a historical family entry is admitted VERBATIM, from the pinned before document,
 * as that family's hold when no leaf the candidate moves falls under it and it carries a
 * reading. Otherwise it is refused, and every member leaf of the document's patch needs its own
 * per-leaf record (a family containing a moved leaf needs per-leaf fitted records). */
export function admitFamilies(familyEntries:Record<string,any>,moved:readonly string[],
  patchLeaves:readonly string[]) {
  // Historical methods are prose, blank separator lines included; a reading is any nonblank text.
  const reading=(m:unknown)=>(typeof m==='string'&&m.trim()!=='')||(Array.isArray(m)
    &&m.every(line=>typeof line==='string')&&m.some(line=>line.trim()!==''));
  const admitted:Record<string,{members:string[]}>={};
  const refused:Record<string,{members:string[];moved:string[];reason:string}>={};
  for(const [key,entry] of Object.entries(familyEntries)) {
    const members=patchLeaves.filter(leaf=>fallsUnder(leaf,key,entry)).sort();
    const under=moved.filter(leaf=>fallsUnder(leaf,key,entry)).sort();
    if(under.length||!reading(entry.method)) refused[key]={members:[...new Set([...members,...under])].sort(),
      moved:under,reason:under.length?'A moved leaf falls under the family':'The family entry carries no reading'};
    else admitted[key]={members};
  }
  return {admitted,refused};
}
/** Applicability, not a fit verdict. Byte-pinning a record alone does not bind what it measured. */
export function checkRecordApplicability(input:{activeSha256:string;recededSha256:string;
  beforeResolved:any;activeResolved:any;beforePatch:any;activePatch:any;beforeEntries:Record<string,any>;
  activeRecords:ActiveFittingRecords;recededRecords:RecededMethodRecords}) {
  for(const [envelope,digest] of [[input.activeRecords,input.activeSha256],
    [input.recededRecords,input.recededSha256]] as const) {
    if(!/^[0-9a-f]{64}$/.test(digest) || envelope?.endpointSha256!==digest) {
      throw new Error('Fitting record endpoint hash does not bind candidate endpoint');
    }
  }
  const before=flatten(input.beforeResolved),resolved=flatten(input.activeResolved);
  const moved=Object.keys({...before,...resolved}).filter(k=>!isDeepStrictEqual(before[k],resolved[k]));
  const {leafEntries,familyEntries}=partitionEntries(input.beforeEntries,Object.keys({...before,...resolved}));
  const families=admitFamilies(familyEntries,moved,
    Object.keys({...flatten(input.beforePatch),...flatten(input.activePatch)}));
  const retained=input.activeRecords.retainedMeasuredEntries, fitted=input.activeRecords.fittedEntries;
  if(!retained||!fitted||!input.recededRecords.methods) throw new Error('Incomplete fitting record envelope');
  for(const [leaf,entry] of Object.entries(retained)) {
    if(Object.hasOwn(familyEntries,leaf)) {
      throw new Error(`Family-keyed historical entry is admitted from the before document, not retained: ${leaf}`);
    }
    if(entry.status!=='measured'||!isDeepStrictEqual(entry,leafEntries[leaf])||moved.includes(leaf)) {
      throw new Error(`Retained historical active record changed: ${leaf}`);
    }
  }
  if(Object.keys(retained).some(leaf=>Object.hasOwn(fitted,leaf))) throw new Error('Ambiguous active fitting record');
  const activeEntries={...retained,...fitted};
  for(const [leaf,entry] of Object.entries(activeEntries)) {
    if(!Object.hasOwn(resolved,leaf)||!isDeepStrictEqual(entry.value,resolved[leaf])) {
      throw new Error(`Active fitting record value differs from resolved candidate: ${leaf}`);
    }
  }
  const required=new Set([...moved,...Object.entries(leafEntries)
    .filter(([,entry])=>entry.status==='measured').map(([leaf])=>leaf),
    ...Object.values(families.refused).flatMap(family=>family.members)]);
  const {isMethod}=inheritanceMethods();
  const invalidFitted=Object.keys(fitted).filter(leaf=>fitted[leaf]!.status!=='measured'
    ||!isMethod(fitted[leaf]!.method));
  const missingActive=[...new Set([...required].filter(leaf=>!activeEntries[leaf]
    ||(moved.includes(leaf)&&!fitted[leaf])).concat(invalidFitted))].sort();
  return {state:missingActive.length?'UNMEASURED' as const:'MEASURED' as const,
    ...(missingActive.length?{reason:'Candidate active fitted-leaf records incomplete'}:{}),
    missingActive,activeEntries,methods:input.recededRecords.methods,
    retainedHistoricalLeaves:Object.keys(retained).sort(),newlyFittedLeaves:Object.keys(fitted).sort(),
    familyHolds:families};
}
/** X76's receded check, DL5o (a) on top of the original. The original algorithm (referee.ts
 * checkInheritance, W49a seal.ts 197-230) reads the leaf-keyed records alone. A leaf it would
 * report missing because it is stated at the active's value with no leaf record is then held by
 * an ADMITTED family of the before receded document, when the before document states it at the
 * same value. Every member of a REFUSED family must carry its own per-leaf record: a fitted
 * method, an explicit hold, or an unmoved leaf-keyed historical measurement. */
export function checkFamilyInheritance(input:{activeResolved:any;activePatch:any;
  activeEntries:Record<string,any>;beforePatch:any;beforeEntries:Record<string,any>;
  candidatePatch:any;methods:Record<string,any>}) {
  const mine=flatten(input.candidatePatch),before=flatten(input.beforePatch);
  const {leafEntries,familyEntries}=partitionEntries(input.beforeEntries,
    Object.keys({...flatten(input.activeResolved),...before,...mine}));
  const original=checkInheritance({...input,beforeEntries:leafEntries});
  // The original reads movement on the candidate's own keys; a family is also refused when the
  // candidate DROPS a member it stated, since that leaf then silently takes the active's value.
  const dropped=Object.keys(before).filter(leaf=>!Object.hasOwn(mine,leaf));
  const families=admitFamilies(familyEntries,[...original.moved,...dropped],Object.keys({...before,...mine}));
  const heldByFamily:Record<string,string>={};
  for(const [family,{members}] of Object.entries(families.admitted)) for(const leaf of members) {
    if(original.inherited.includes(leaf)&&Object.hasOwn(before,leaf)&&Object.hasOwn(mine,leaf)
      &&isDeepStrictEqual(before[leaf],mine[leaf])) heldByFamily[leaf]??=family;
  }
  const {isMethod,isHold}=inheritanceMethods();
  const perLeaf=(leaf:string)=>isMethod(input.methods[leaf])||isHold(input.methods[leaf])
    ||(leafEntries[leaf]?.status==='measured'&&!original.moved.includes(leaf));
  const missing=[...new Set([...original.missing.filter(leaf=>!Object.hasOwn(heldByFamily,leaf)),
    ...Object.values(families.refused).flatMap(family=>family.members).filter(leaf=>!perLeaf(leaf))])].sort();
  return {...original,verdict:missing.length?'failure' as const:'within' as const,missing,
    familyHolds:{...families,heldByFamily},
    port:'DL5o (a): historical family-keyed entries admitted verbatim as holds; refused families need per-leaf records'};
}
