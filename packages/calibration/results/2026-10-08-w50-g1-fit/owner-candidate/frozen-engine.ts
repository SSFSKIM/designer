import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { isDeepStrictEqual } from 'node:util';
import { execFileSync } from 'node:child_process';
import assert from 'node:assert/strict';
import { SHIPPED_MATERIAL_PROFILE_DOCUMENTS, mergeMaterialProfiles } from '@vitreajs/vitrea-web';
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from '@vitrea/renderer-webgpu';
import { decodePng } from '../../../src/image.ts';
import { oklabDeltaE } from '../../../src/metrics/perceptual.ts';
import { opaqueGlassViolations } from '../../../scripts/no-opaque-glass.ts';
import { bindSource, assertedNumbers } from '../owner/source.ts';
import type { Pin, Row, Capture } from '../owner/referee.ts';
import type { MatrixInput, Prepared, OwnerReport } from '../owner/api.ts';
import type { IntrinsicInputs } from '../owner/intrinsic.ts';
import { createIdentityResolver } from './identity.ts';

const HOME=dirname(fileURLToPath(import.meta.url));
const CAL=resolve(HOME,'../../..');
const PREFIX='packages/calibration/results/2026-10-08-w50-g1-fit/owner/';
export interface CandidateEngineInputs {
  /** Whole-file hashes supplied by the externally pinned frozen owner closure, never self-hashed. */
  sourcePins:Record<string,Pin>;
  declarations:Pin[];
}

/** The frozen algorithms are AST-bound, not copied. These explicit selector/dependency lists
 * are the audit surface: candidate adaptation replaces only document and capture boundaries.
 * Exported function declarations retain their export assignments in transpilation; `exports`
 * is an explicit disposable binding, not permission to load a module or execute its imports. */
export function createCandidateEngine(input:CandidateEngineInputs) {
  const source:Record<string,{text:string;pin:Pin}>={};
  for(const name of ['source.ts','referee.ts','api.ts','intrinsic.ts']) {
    const pin=input.sourcePins[PREFIX+name];
    if(!pin||!/^[0-9a-f]{64}$/.test(pin.sha256)) throw new Error(`Missing full source pin: ${name}`);
    const bytes=readFileSync(pin.path);
    if(createHash('sha256').update(bytes).digest('hex')!==pin.sha256) throw new Error(`Frozen source hash changed: ${name}`);
    // The imported binder must itself be the pinned original, even if callers use relocated sources.
    if(name==='source.ts'&&createHash('sha256').update(readFileSync(resolve(HOME,'../owner/source.ts')))
      .digest('hex')!==pin.sha256) throw new Error('Imported frozen source binder differs from pin');
    source[name]={text:bytes.toString(),pin:{...pin}};
  }
  const bind=(name:string,selectors:readonly string[],bindings:Record<string,unknown>={})=>
    bindSource(source[name]!.text,source[name]!.pin.sha256,selectors,{exports:{},...bindings});
  const base=bind('referee.ts',[
    'OWNER_SOURCE_SHA256','X76_SOURCE_SHA256','C1_SCOPE','X1_SCOPE','L1_SCOPE',
    'sha','identity','cellKey','position','value','ownerReading','na','unread','measured','standard',
    'loadContracts','pinnedBytes','documentRoles','assertDocumentPair','readMatrix','classifyCell',
    'coherenceOwnerScope','checkInheritance','checkOpacity','inheritanceMethods',
  ],{readFileSync,createHash,resolve,CAL,OWNER:resolve(CAL,'test/adopted-thresholds.test.ts'),
    bindSource,assertedNumbers,opaqueGlassViolations,Buffer});
  const identityResolver=createIdentityResolver(input.declarations,{
    documentRoles:base.documentRoles,assertDocumentPair:base.assertDocumentPair,
  });
  const legacy=bind('referee.ts',['captureBytes'],{documentRoles:base.documentRoles,
    pinnedBytes:base.pinnedBytes,decodePng});

  /** The sole new pixel kernel. The shipped-role regex is internal to frozen captureBytes,
   * so candidate stamps cannot enter it honestly. Its remaining boundary checks are retained;
   * metric arithmetic, masks and coherence all remain frozen-source functions below. */
  function captureBytes(row:Row,capture:Capture,declaration?:any) {
    const candidate=identityResolver.resolve(row);
    if(!candidate) return legacy.captureBytes(row,capture,declaration);
    const metadata=JSON.parse(base.pinnedBytes(capture.metadata).toString());
    if(metadata.capturePath!==row.key.web.capturePath) throw new Error('Capture descriptor differs from row');
    if(metadata.sceneId!==row.key.sceneId) throw new Error('Capture scene differs from row');
    if(metadata.renderer!==row.key.web.renderer) throw new Error('Capture renderer differs from row');
    if(typeof metadata.samplingBackend!=='string'||!metadata.samplingBackend
      ||metadata.samplingBackend!==row.key.web.samplingBackend) throw new Error('Capture sampling backend differs from row');
    if(!isDeepStrictEqual(capture.documents,identityResolver.documents(row))) {
      throw new Error('Capture does not bind the complete candidate document pair');
    }
    const bytes={web:base.pinnedBytes(capture.web),native:base.pinnedBytes(capture.native),
      backdrop:base.pinnedBytes(capture.backdrop)};
    const images=Object.values(bytes).map(bytes=>decodePng(bytes as Buffer));
    const size=[images[0]!.width,images[0]!.height];
    if(!isDeepStrictEqual(metadata.pixelSize,size)
      ||images.some(image=>image.width!==size[0]||image.height!==size[1])) {
      throw new Error('Capture/native/backdrop pixel size or dimensions differ');
    }
    const scale=row.key.profileKey.includes('-2x-')?2:1;
    if(declaration&&(size[0]!==declaration.canvas.width*scale||size[1]!==declaration.canvas.height*scale)) {
      throw new Error('Capture pixel size differs from declared canvas and profile scale');
    }
    const viewport=metadata.capturePath.match(/viewport=(\d+)x(\d+)/);
    const dpr=metadata.capturePath.match(/deviceScaleFactor=([\d.]+)/);
    if((dpr&&Number(dpr[1])!==scale)||(viewport
      &&(Number(viewport[1])*scale!==size[0]||Number(viewport[2])*scale!==size[1]))) {
      throw new Error('Capture pixel size differs from descriptor viewport/scale');
    }
    return bytes;
  }
  const pixels=bind('referee.ts',['validateCapture','recountBlack','pairedCoherence'],{
    captureBytes,resolve,CAL,bindSource,decodePng,assert,oklabDeltaE,
    OWNER_SOURCE_SHA256:base.OWNER_SOURCE_SHA256,X1_SCOPE:base.X1_SCOPE,
    unread:base.unread,measured:base.measured,cellKey:base.cellKey,value:base.value,
  });
  // DL5o (a): the family-keyed history admission is intrinsic.ts's own; the original leaf-keyed
  // receded algorithm stays referee.ts checkInheritance, bound in unchanged.
  const records=bind('intrinsic.ts',['unread','flatten','assertEndpointIdentity','isPlainObject',
    'partitionEntries','fallsUnder','admitFamilies','checkRecordApplicability','checkFamilyInheritance'],{
    isDeepStrictEqual,inheritanceMethods:base.inheritanceMethods,checkInheritance:base.checkInheritance,
  });
  const assertEndpointIdentity=(document:any,position:number,pose:'active'|'receded')=>
    identityResolver.assertEndpointIdentity(document,position,pose,records.assertEndpointIdentity);
  const intrinsic=bind('intrinsic.ts',['candidateIntrinsics'],{
    unread:records.unread,pinnedBytes:base.pinnedBytes,
    readCandidateDocument:identityResolver.readCandidateDocument,
    assertDocumentPair:identityResolver.assertDocumentPair,
    SHIPPED_MATERIAL_PROFILE_DOCUMENTS,mergeMaterialProfiles,
    assertEndpointIdentity,withMaterialOverrides,DEFAULT_MATERIAL_PROFILE,
    checkRecordApplicability:records.checkRecordApplicability,
    checkFamilyInheritance:records.checkFamilyInheritance,checkOpacity:base.checkOpacity,
  });
  const api=bind('api.ts',[
    'C1_SCOPE','unread','notApplicable','pos','standard','documentsOf','rowsOf','referenceFor',
    'declaredScene','c1Rows','c1Evidence','chromaAggregate','blackMember','edgeMember','edgeEvidence',
    'jsonNative','evaluateRows',
  ],{documentRoles:identityResolver.roles,readMatrix:base.readMatrix,pinnedBytes:base.pinnedBytes,
    identity:base.identity,bindSource,OWNER_SOURCE_SHA256:base.OWNER_SOURCE_SHA256,
    validateCapture:pixels.validateCapture,execFileSync,resolve,HERE:resolve(HOME,'../owner'),
    classifyCell:base.classifyCell,recountBlack:pixels.recountBlack,
    coherenceOwnerScope:base.coherenceOwnerScope,pairedCoherence:pixels.pairedCoherence});

  function rowsOf(inputs:MatrixInput[]):Row[] {
    // The unchanged reader compares 12-hex legacy role stamps. Candidates additionally require
    // the registered full endpoint SHA; a colliding prefix is not a declaration identity.
    for(const input of inputs) for(const row of base.readMatrix(base.pinnedBytes(input.matrix),input.matrix.sha256)) {
      if(!identityResolver.resolve(row)) continue;
      for(const [path,sha] of Object.entries(identityResolver.documents(row))) {
        if(input.documents[path]!==sha) throw new Error('Candidate matrix document differs from full declaration pin');
      }
    }
    return api.rowsOf(inputs);
  }
  function evaluateRows(context:Prepared,rows:Row[],captures:Record<string,Capture>,candidate=true):OwnerReport {
    for(const row of rows) identityResolver.roles(row);
    return api.jsonNative(api.evaluateRows(context,rows,captures,candidate));
  }
  function candidateIntrinsics(inputs:IntrinsicInputs,rows:Row[],currentRows:Row[]=[]):any {
    for(const pin of inputs.candidateDeclarations) {
      const registered=identityResolver.declarations.find(p=>p.path===pin.path);
      if(!registered||registered.sha256!==pin.sha256) throw new Error('Intrinsic declaration hash differs from registered cohort');
    }
    return intrinsic.candidateIntrinsics(inputs,rows,currentRows);
  }
  return {evaluateRows,rowsOf,identityResolver,candidateIntrinsics,assertEndpointIdentity,captureBytes,
    validateCapture:pixels.validateCapture,pairedCoherence:pixels.pairedCoherence,
    recountBlack:pixels.recountBlack,classifyCell:base.classifyCell,loadContracts:base.loadContracts,
    sourcePins:Object.fromEntries(Object.values(source).map(s=>[s.pin.path,{...s.pin}]))};
}
