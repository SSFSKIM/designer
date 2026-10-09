import { isDeepStrictEqual } from 'node:util';
import { execFileSync } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { bindSource } from './source.ts';
import { candidateIntrinsics, type IntrinsicInputs } from './intrinsic.ts';
import { documentRoles, loadContracts, classifyCell, pinnedBytes, readMatrix, identity, recountBlack,
  pairedCoherence, coherenceOwnerScope, checkOpacity, checkInheritance, validateCapture,
  OWNER_SOURCE_SHA256, type Contracts, type Row, type Pin, type Capture, type Evidence } from './referee.ts';

const HERE = dirname(fileURLToPath(import.meta.url));
const C1_SCOPE = "W32 C1 — the shadow's exterior shape, per span (claims §5.169)";
const unread = (reason:string):Evidence => ({state:'UNMEASURED',reason});
const notApplicable = (reason:string):Evidence => ({state:'NOT_APPLICABLE',reason});
const pos = (r:Row) => r.key.profileKey.endsWith('-glass0.25') ? .25 : .5;
const standard = (r:Row) => /^apple-macos-27\.0-[12]x-(light|dark)-standard-glass(0\.25|0\.5)$/.test(r.key.profileKey);
export interface MatrixInput {
  matrix: Pin;
  /** Descriptor pathname -> full digest, for every document any row in this file names. */
  documents: Record<string,string>;
}
export interface PrepareInputs {
  declaration: Pin;
  current: MatrixInput[];
  references: MatrixInput[];
  captures: Record<string,Capture>;
  referenceCaptures: Record<string,Capture>;
  python: string;
}
function documentsOf(row:Row): Record<string,string> {
  return Object.fromEntries(Object.values(documentRoles(row)).map(pin=>[pin.path,pin.sha256]));
}
function rowsOf(inputs:MatrixInput[]) {
  const rows:Row[]=[];
  for(const input of inputs) {
    for(const row of readMatrix(pinnedBytes(input.matrix),input.matrix.sha256)) {
      for(const [path,short] of Object.entries(documentsOf(row))) {
        if(!/^[0-9a-f]{64}$/.test(input.documents[path]??'') || input.documents[path]?.slice(0,12)!==short) {
          throw new Error('Matrix row document differs from pinned generation');
        }
      }
      rows.push(row);
    }
  }
  if(new Set(rows.map(identity)).size!==rows.length) throw new Error('Multiple generations for same cell');
  return rows;
}
function referenceFor(C:Contracts,row:Row,refs:Row[]) {
  const scheme = row.key.profileKey.includes('-dark-')?'dark':'light';
  const pair=pos(row)===.25?C.GLASS025_REFERENCE[scheme==='dark'?1:0]:C.BASELINE[scheme];
  const found=refs.find(r=>identity(r)===identity(row));
  if(!found) return undefined;
  const hashes=documentRoles(found);
  if(hashes.materialProfile.sha256!==pair.active||hashes.recededProfile.sha256!==pair.receded) {
    throw new Error(`Wrong original owner baseline for ${identity(row)}`);
  }
  return found;
}
function declaredScene(declaration:any,r:Row) {
  const scene=declaration.scenes.find((s:any)=>s.id===r.key.sceneId);
  if(!scene) throw new Error('Row scene absent from declaration');
  const roles=Object.entries(declaration.split).filter(([role,ids])=>!role.startsWith('$')
    && (ids as string[]).includes(scene.id)).map(([role])=>role);
  if(roles.length!==1 || roles[0]!==r.fixtureSet || scene.state!==r.state) {
    throw new Error('Row role/state differs from declaration');
  }
  return {scene,component:declaration.components[scene.component],role:roles[0]};
}
function c1Rows(C:Contracts,rows:Row[],declaration:any) {
  const selectors=['spanOf','deriveClause'].map(n=>`${C1_SCOPE}/${n}`);
  const api=bindSource(C.text,OWNER_SOURCE_SHA256,selectors,{
    ...C.c1,components:declaration.components,
    glassOf:(profile:string)=>profile.endsWith('-glass0.25')?.25:profile.endsWith('-glass0.5')?.5:undefined,
    atAShippedDocument:()=>true, // rowsOf already proved the explicitly pinned candidate generation.
    inRecordedRole:(row:Row)=>row.fixtureSet==='recorded'||declaration.split.recorded?.includes(row.key.sceneId),
  });
  return [...api.deriveClause(rows,.25),...api.deriveClause(rows,.5)] as any[];
}
export function c1Evidence(C:Contracts,rows:Row[],declaration:any,expectedKeys:string[]):Evidence {
  const derived=c1Rows(C,rows,declaration);
  const actual=new Set(derived.map(d=>identity(d.cell)));
  const missing=expectedKeys.filter(k=>!actual.has(k));
  const unexpected=[...actual].filter(k=>!expectedKeys.includes(k));
  if(missing.length || unexpected.length || !expectedKeys.length) {
    return {...unread('C1 complete declared bed required'),missing,unexpected};
  }
  const groups=new Map<string,any[]>();
  for(const d of derived) {
    const r=d.cell,profile=r.key.profileKey;
    const comp=declaration.components[r.key.sceneId.split('__')[1]];
    const span=Math.min(...(comp.size??comp.base?.size??[]));
    const bed=`${profile.includes('-2x-')?2:1}x ${profile.includes('-dark-')?'dark':'light'}`;
    const key=`${pos(r)}/${bed}/${span}`;
    groups.set(key,[...(groups.get(key)??[]),{...d,span,bed}]);
  }
  const represented=new Set(rows.filter(standard).map(r=>`${pos(r)}/${r.key.profileKey.includes('-2x-')?2:1}x ${r.key.profileKey.includes('-dark-')?'dark':'light'}`));
  const missingGroups=[...represented].flatMap(bed=>C.c1.C1_SPANS
    .map((span:number)=>`${bed}/${span}`).filter((key:string)=>!groups.has(key)));
  if(missingGroups.length) return {...unread('C1 complete declared span groups required'),missingGroups};
  const perBed:Record<string,any>={};
  for(const [key,entries] of groups) {
    const first=entries[0];
    if(pos(first.cell)===.5 && entries.length!==C.c1.CONTRIBUTING_CELLS[first.bed][first.span]) {
      return {...unread('C1 fixed 0.5 bed count incomplete'),bed:key,actual:entries.length,
        expected:C.c1.CONTRIBUTING_CELLS[first.bed][first.span]};
    }
    const T=C.c1.upperMiddle(entries.map(e=>e.T));
    perBed[key]={cells:entries.length,T,verdict:T<=C.c1.C1_TOLERANCE?'within':'failure'};
  }
  return {state:'MEASURED',verdict:Object.values(perBed).some(g=>g.verdict==='failure')?'failure':'within',
    perBed,cells:derived.map(d=>({key:identity(d.cell),T:d.T,bandsUsed:d.bandsUsed,
      native:d.cell.shadow.affineNative,candidate:d.cell.shadow.affineWeb}))};
}
export function chromaAggregate(C:Contracts,cells:Evidence[],expected:number):Evidence {
  if(cells.length!==expected||!cells.length||cells.some(c=>c.state!=='MEASURED')) {
    return {...unread('M1 complete scheme/pose bed required'),expected,actual:cells.length};
  }
  const values=cells.map(c=>c.R as number).sort((a,b)=>a-b);
  const middle=values.length/2;
  const median=values.length%2?values[Math.floor(middle)]!:(values[middle-1]!+values[middle]!)/2;
  return {state:'MEASURED',median,cells:values.length,verdict:median>=C.CHROMA_MEDIAN_MIN
    && median<=C.CHROMA_MEDIAN_MAX?'within':'failure'};
}
function blackMember(C:Contracts,r:Row,decl:any) {
  const {scene,component,role}=declaredScene(decl,r);
  return standard(r)&&r.key.web.renderer==='webgpu'&&r.tier==='texture'
    && ['calibration','validation','probe'].includes(role!)&&['rest','inactive'].includes(scene.state)
    && C.BLACK.includes(scene.background)&&['rrect','capsule'].includes(component.kind);
}
function edgeMember(r:Row,decl:any) {
  const {scene,component,role}=declaredScene(decl,r);
  return standard(r)&&r.key.web.renderer==='webgpu'&&r.key.web.samplingBackend==='gpu-texture'
    && ['calibration','validation','probe'].includes(role!)&&scene.state==='rest'
    && ['rrect','capsule','group'].includes(component.kind);
}
function edgeEvidence(r:Row,reference:Row|undefined,capture:Capture|undefined,
  referenceCapture:Capture|undefined,decl:any,python:string):Evidence {
  if(!capture||!reference||!referenceCapture) return unread('E2 requires pinned native/candidate/original-reference captures');
  validateCapture(r,capture,decl);validateCapture(reference,referenceCapture,decl);
  if(capture.native.sha256!==referenceCapture.native.sha256) throw new Error('E2 native generation differs');
  const {component}=declaredScene(decl,r);
  const output=execFileSync(python,['-I','-B',resolve(HERE,'edge.py')],{input:JSON.stringify({
    native:capture.native,current:referenceCapture.web,candidate:capture.web,component,
    scale:r.key.profileKey.includes('-2x-')?2:1,identity:[r.key.profileKey,r.key.sceneId]}),encoding:'utf8',maxBuffer:8*1024*1024});
  const result=JSON.parse(output);
  // Python's current means its supplied fixed original reference, not W50's current.
  const {current:referenceValue,...rest}=result;
  return {...rest,...(referenceValue===undefined?{}:{reference:referenceValue}),
    provenance:{capture,referenceCapture}};
}
export interface Prepared {
  inputs:PrepareInputs; contracts:Contracts; declaration:any; currentRows:Row[]; referenceRows:Row[];
  current:OwnerReport;
}
export interface OwnerReport {
  cells:Record<string,Record<string,Evidence>>;
  aggregates:Record<string,Evidence>;
  provenance:unknown;
  intrinsic:unknown;
  noNewTrade:string;
}

/** Reads only caller-pinned files; neither function writes or chooses a current generation.
 * Every owner-contract inventory row can retain the whole per-cell axis map: it is not
 * converted into a fabricated scalar 'native/current owner PASS'. */
export function prepareCurrent(inputs:PrepareInputs):Prepared {
  const contracts=loadContracts();
  const declaration=JSON.parse(pinnedBytes(inputs.declaration).toString());
  const currentRows=rowsOf(inputs.current),referenceRows=rowsOf(inputs.references);
  for(const row of currentRows) declaredScene(declaration,row);
  const prepared={inputs,contracts,declaration,currentRows,referenceRows} as Prepared;
  prepared.current=jsonNative(evaluateRows(prepared,currentRows,inputs.captures,false));
  return prepared;
}
export const prepare_current=prepareCurrent;
export function evaluate(context:Prepared,candidate:MatrixInput[],captures:Record<string,Capture>,
  completedReferences:OwnerReport, intrinsic?:IntrinsicInputs):OwnerReport {
  if(!isDeepStrictEqual(completedReferences,context.current)) {
    throw new Error('Completed owner references differ from fixed pre-fit reading');
  }
  const candidateRows=rowsOf(candidate);
  const report=evaluateRows(context,candidateRows,captures,true);
  report.intrinsic=intrinsic?candidateIntrinsics(intrinsic,candidateRows,context.currentRows)
    :{X75:unread('Candidate declarations not supplied'),X76:unread('Candidate inheritance records not supplied')};
  return jsonNative(report);
}
/** Reports cross a JSON boundary. Omit absent object fields, never synthesize numeric
 * readings from them; unsupported array holes and nonfinite readings refuse instead. */
function jsonNative<T>(value:T):T {
  if(Array.isArray(value)) return value.map(item=>{
    if(item===undefined) throw new Error('Undefined array entry in owner report');
    return jsonNative(item);
  }) as T;
  if(value!==null && typeof value==='object') return Object.fromEntries(Object.entries(value)
    .filter(([,item])=>item!==undefined).map(([key,item])=>[key,jsonNative(item)])) as T;
  if(typeof value==='number'&&!Number.isFinite(value)) throw new Error('Nonfinite owner reading');
  return value;
}
function evaluateRows(context:Prepared,rows:Row[],captures:Record<string,Capture>,candidate:boolean):OwnerReport {
  const C=context.contracts,decl=context.declaration;
  const expected=new Set(context.currentRows.map(identity));
  for(const r of rows) {
    if(!expected.has(identity(r))) throw new Error('Unexpected owner row outside fixed current inventory');
    declaredScene(decl,r);
  }
  // The frozen-current inventory supplies the native/backdrop identity for each cell. A
  // candidate cannot manufacture that association by handing us two well-hashed PNGs.
  const boundCaptures:Record<string,Capture>={};
  for(const r of rows) {
    const key=identity(r),capture=captures[key];
    if(!capture) continue;
    validateCapture(r,capture,decl);
    if(candidate) {
      const frozen=context.inputs.captures[key];
      if(!frozen) continue;
      const before=context.currentRows.find(row=>identity(row)===key)!;
      validateCapture(before,frozen,decl);
      if(capture.native.sha256!==frozen.native.sha256
        ||capture.backdrop.sha256!==frozen.backdrop.sha256) {
        throw new Error(`Candidate native/backdrop differs from same-cell frozen inventory: ${key}`);
      }
    }
    boundCaptures[key]=capture;
  }
  captures=boundCaptures;
  const byKey=new Map(rows.map(r=>[identity(r),r]));
  const cells:OwnerReport['cells']={};
  for(const current of context.currentRows) {
    const key=identity(current),r=byKey.get(key);
    if(!r) {
      cells[key]=Object.fromEntries(['M1','M2','C1','X1','L1','E2','coherence'].map(a=>[a,unread('Required row not in phase') ]));
      const scope=coherenceOwnerScope(C,current,decl);
      Object.assign(cells[key]!.coherence,scope,scope.diagnosticOnly
        ?{reason:'Optional coherence diagnostic row not in phase'}:{});
      continue;
    }
    const reference=standard(r)?referenceFor(C,r,context.referenceRows):undefined;
    const axes=classifyCell(C,r,reference);
    axes.X1=blackMember(C,r,decl)?captures[key]?recountBlack(C,r,captures[key]!,decl)
      :unread('X1 requires actual capture pixels'):notApplicable('Outside X1 declared population');
    const edgeReference=pos(r)===.25?reference:current;
    const edgeCapture=pos(r)===.25?context.inputs.referenceCaptures[key]:context.inputs.captures[key];
    axes.E2=edgeMember(r,decl)?edgeEvidence(r,edgeReference,captures[key],edgeCapture,decl,context.inputs.python)
      :notApplicable('Outside E2 declared population');
    axes.E2.referenceMeaning=pos(r)===.25?'Original adopted d0219/c05 historical reading'
      :'W50 caller-pinned frozen-current price (generation/document pair in provenance); not an existing E2 owner bound';
    // Extra diagnostics do not extend the source owner's presence requirement. The W50
    // caller decides its own evidence completeness separately from this retained contract.
    const coherenceScope=coherenceOwnerScope(C,r,decl);
    const twinKey=`${r.key.profileKey}/webgpu/${r.key.sceneId}`;
    axes.coherence={...(r.key.web.renderer==='css'
      ?pairedCoherence(C,r,byKey.get(twinKey),captures[key],captures[twinKey],
        coherenceScope.sourceOwnerNumericWindowAdopted)
      :notApplicable('Paired coherence is reported on the CSS row')), ...coherenceScope};
    if(candidate) for(const [axis,evidence] of Object.entries(axes)) {
      const before=context.current.cells[key]?.[axis];
      if(before) evidence.current=before.candidate??before.readings??
        (axis==='coherence'?{deltaE:before.deltaE,ratio:before.ratio}:null);
    }
    cells[key]=axes;
  }
  const requiredC1=c1Rows(C,context.currentRows,decl).map(d=>identity(d.cell));
  const aggregates:Record<string,Evidence>={C1:c1Evidence(C,rows,decl,requiredC1)};
  for(const position of [.25,.5]) for(const scheme of ['light','dark']) for(const pose of ['rest','inactive']) {
    const members=context.currentRows.filter(r=>pos(r)===position&&r.key.profileKey.includes(`-${scheme}-`)
      &&r.state===pose&&classifyCell(C,r).M1.state!=='NOT_APPLICABLE');
    if(!members.length) continue;
    const expectedCount=C.m1[`${scheme}|${pose==='rest'?'active':'inactive'}`];
    aggregates[`M1/${position}/${scheme}/${pose}`]=chromaAggregate(C,
      members.map(r=>cells[identity(r)]!.M1),expectedCount);
  }
  const c1Cells=c1Rows(C,rows,decl);
  for(const r of rows) {
    const d=c1Cells.find(e=>identity(e.cell)===identity(r));
    cells[identity(r)]!.C1=d?{state:'MEASURED',verdict:'reported',T:d.T,
      native:r.shadow.affineNative,candidate:r.shadow.affineWeb,
      ...(candidate?{current:context.current.cells[identity(r)]?.C1.candidate,
        currentT:context.current.cells[identity(r)]?.C1.T}:{}),
      reason:'Per-cell reading; adopted verdict is complete bed×span upper-middle aggregate'}
      :requiredC1.includes(identity(r))?unread('Previously contributing C1 cell lost required bands/support')
      :notApplicable('Outside C1 contributing population; owner selection unchanged');
  }
  if(candidate) {
    const currentC1=context.current.aggregates.C1;
    aggregates.C1.current={state:currentC1.state,perBed:currentC1.perBed,cells:currentC1.cells};
    if(Array.isArray(aggregates.C1.cells)) for(const cell of aggregates.C1.cells) {
      const before=context.current.cells[cell.key]?.C1;
      cell.current=before?.candidate; cell.currentT=before?.T;
    }
  }
  return {cells,aggregates,provenance:{owner:C.source,current:context.inputs.current,
    fixedReferences:context.inputs.references,declaration:context.inputs.declaration},
    intrinsic:{X75:unread('Intrinsic candidate check is separate'),X76:unread('Intrinsic candidate check is separate')},
    noNewTrade:'E2 remains read/listed, not a new absolute gate. Named owner misses and exclusions remain explicit; '
      +'native/current/candidate deltas are evidence for the W50 intersection, not an invented trade budget.'};
}
