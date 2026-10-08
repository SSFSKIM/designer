import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { isDeepStrictEqual } from 'node:util';
import { dirname, relative, resolve as resolvePath } from 'node:path';
import { fileURLToPath } from 'node:url';
import { readCandidateDocument } from '../../../scripts/candidate-document.ts';
import { candidateMaterialLabel } from '../../../src/material-selection.ts';
import type { Pin, Row } from '../owner/referee.ts';

type Roles = Record<'materialProfile'|'recededProfile',Pin>;
interface LegacyIdentity {
  documentRoles(row:Row):Roles;
  assertDocumentPair(row:Row,active:string,receded:string):void;
}
const fullHash=/^[0-9a-f]{64}$/;
function pinned(pin:Pin) {
  const bytes=readFileSync(pin.path);
  if(!fullHash.test(pin.sha256)||createHash('sha256').update(bytes).digest('hex')!==pin.sha256) {
    throw new Error(`Candidate identity hash differs from full pin: ${pin.path}`);
  }
  return bytes;
}

/** Candidate identity is a declaration, never a fabricated pair of shipped descriptor clauses.
 * Legacy rows retain the frozen role parser. The registry is one fixed cohort per position;
 * callers cannot silently combine two proposals because some endpoint bytes happen to agree. */
export function createIdentityResolver(declarations:readonly Pin[],legacy:LegacyIdentity) {
  const registered=declarations.map(pin=>{
    pinned(pin);
    const candidate=readCandidateDocument(pin.path);
    if(![.25,.5].includes(candidate.document.glassTintAmount)) {
      throw new Error('Candidate position is outside the fixed owner cohort');
    }
    const relativePath=relative(resolvePath(dirname(fileURLToPath(import.meta.url)),'../../../../..'),pin.path);
    const shown=relativePath.startsWith('..')?pin.path:relativePath;
    return {declaration:{...pin},candidate,shown};
  });
  if(new Set(registered.map(r=>r.candidate.document.glassTintAmount)).size!==registered.length) {
    throw new Error('Multiple candidate cohorts at one glass position');
  }
  function readRegistered(path:string) {
    const entry=registered.find(r=>r.declaration.path===path);
    if(!entry) throw new Error('Candidate declaration path is not registered');
    pinned(entry.declaration);
    for(const endpoint of Object.values(entry.candidate.endpoints)) pinned(endpoint);
    return entry;
  }
  function resolve(row:Row) {
    const descriptor=row.key.web.capturePath;
    if(typeof descriptor!=='string') throw new Error('Missing capture descriptor');
    const candidateFields=/(?:^|[\s,])(?:candidateDocument|declarationSha256|name|glassTintAmount)=/.test(descriptor)
      ||/(?:^|[\s,])materialProfile=candidate(?:$|[\s,])/.test(descriptor);
    if(!candidateFields) return undefined;
    const matches=[...descriptor.matchAll(/(?:^|[\s,])candidateDocument=([^\s,]+)/g)];
    if(matches.length!==1) throw new Error('Candidate declaration stamp is missing or ambiguous');
    const matched=registered.find(r=>r.shown===matches[0]![1]);
    if(!matched) throw new Error('Candidate declaration stamp path is not registered');
    const entry=readRegistered(matched.declaration.path);
    const candidate=entry.candidate;
    const stamp=candidateMaterialLabel({declaration:entry.shown,
      sha256:entry.declaration.sha256.slice(0,12),name:candidate.document.name,
      glassTintAmount:candidate.document.glassTintAmount});
    const start=descriptor.indexOf(stamp),end=start+stamp.length;
    if(start<0||(start>0&&!/[\s,]/.test(descriptor[start-1]!))
      ||(end<descriptor.length&&!/[\s,]/.test(descriptor[end]!))) {
      throw new Error('Candidate stamp differs from registered declaration');
    }
    const rest=descriptor.slice(0,start)+descriptor.slice(end);
    if(/(?:^|[\s,])(?:materialProfile|recededProfile|candidateDocument|declarationSha256|name|glassTintAmount|crossPosition)=/.test(rest)) {
      throw new Error('Mixed candidate stamp, shipped roles or crossPosition');
    }
    const profile=/^apple-macos-27\.0-[12]x-(light|dark)-(?:standard|reduced-transparency|increased-contrast(?:-coupled)?)-glass(0\.25|0\.5)$/.exec(row.key.profileKey);
    if(!profile||Number(profile[2])!==candidate.document.glassTintAmount) {
      throw new Error('Candidate profile scheme/position differs from declaration');
    }
    const scheme=profile[1] as 'light'|'dark';
    const active=candidate.endpoints[`active.${scheme}`];
    const receded=candidate.endpoints[`receded.${scheme}`];
    return {declaration:{...entry.declaration},candidate,active,receded,scheme,
      position:candidate.document.glassTintAmount,endpoints:candidate.endpoints};
  }
  function roles(row:Row):Roles {
    const resolved=resolve(row);
    return resolved?{
      materialProfile:{path:resolved.active.path,sha256:resolved.active.sha256.slice(0,12)},
      recededProfile:{path:resolved.receded.path,sha256:resolved.receded.sha256.slice(0,12)},
    }:legacy.documentRoles(row);
  }
  function documents(row:Row):Record<string,string> {
    const resolved=resolve(row);
    return Object.fromEntries((resolved?[resolved.active,resolved.receded]:Object.values(roles(row)))
      .map(pin=>[pin.path,pin.sha256]));
  }
  function assertDocumentPair(row:Row,active:string,receded:string) {
    const resolved=resolve(row);
    if(!resolved) return legacy.assertDocumentPair(row,active,receded);
    if(!fullHash.test(active)||!fullHash.test(receded)
      ||resolved.active.sha256!==active||resolved.receded.sha256!==receded) {
      throw new Error('Candidate document pair differs from declaration roles');
    }
  }
  function assertEndpointIdentity(document:any,position:number,pose:'active'|'receded',
    fallback:(document:any,position:number,pose:'active'|'receded')=>void) {
    for(const entry of registered) {
      readRegistered(entry.declaration.path);
      for(const slot of ['active.dark','receded.dark'] as const) {
        const endpoint=JSON.parse(pinned(entry.candidate.endpoints[slot]).toString());
        if(!isDeepStrictEqual(document,endpoint)) continue;
        if(entry.candidate.document.glassTintAmount!==position||!slot.startsWith(pose+'.')) {
          throw new Error('Candidate endpoint identity differs from position/pose');
        }
        return;
      }
    }
    fallback(document,position,pose);
  }
  return {resolve,roles,documents,assertDocumentPair,assertEndpointIdentity,
    readCandidateDocument:(path:string)=>readRegistered(path).candidate,
    declarations:registered.map(r=>({...r.declaration}))};
}
export type IdentityResolver=ReturnType<typeof createIdentityResolver>;
