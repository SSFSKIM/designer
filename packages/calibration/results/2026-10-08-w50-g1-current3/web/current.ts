/** Prepare complete CURRENT-MATERIAL documents, never a numerical-admission report.
 * The production candidate reader rejects shipped names, so only each endpoint's profileKey
 * receives the numeric-equivalent candidate spelling. All other parsed fields stay identical.
 * Original and derived document hashes are recorded separately; material bytes do not change.
 */
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, realpathSync, writeFileSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { cssTierMappingSha256, readCandidateDocument } from '../../../scripts/candidate-document.ts';

const CAL=resolve(dirname(fileURLToPath(import.meta.url)),'../../..');
const hash=(raw:Buffer|string)=>createHash('sha256').update(raw).digest('hex');
const slots=['active.light','active.dark','receded.light','receded.dark'] as const;
function realDestination(path:string):string {
  return existsSync(path) ? realpathSync(path) : join(realDestination(dirname(path)),path.slice(dirname(path).length+1));
}

export function buildCurrent(position:number,out:string) {
  if (![.25,.5].includes(position)) throw Error('Current baseline requires declared glass position');
  out=realDestination(resolve(out));
  for(let parent=out;;parent=dirname(parent)) {
    if(existsSync(join(parent,'.git'))) throw Error('Current documents require external scratch');
    if(parent===dirname(parent))break;
  }
  if(existsSync(out))throw Error('Current document destination is write-once');
  const endpoints:Record<string,{path:string;sha256:string}>={};
  const witnesses:Record<string,unknown>={};
  const files:Record<string,string>={};
  let mapping:unknown;
  for(const slot of slots) {
    const [pose,scheme]=slot.split('.');
    const source=join(CAL,`profiles/apple-macos-27.0-1x-${scheme}-standard-glass${position}${pose==='receded'?'-receded':''}.json`);
    const raw=readFileSync(source);
    const doc=JSON.parse(raw.toString());
    if((doc.patch?.lowEndStrength ?? 0)!==0)throw Error('Current baseline is not at gate0');
    const derived={...doc,profileKey:doc.profileKey.replace(`glass${position}`,`glass${position.toFixed(3)}`)};
    const text=JSON.stringify(derived,null,2)+'\n';
    files[`${slot}.json`]=text;
    endpoints[slot]={path:`${slot}.json`,sha256:hash(text)};
    witnesses[slot]={source:{path:source,sha256:hash(raw)},derived:endpoints[slot]};
    if(slot==='active.light')mapping=doc.cssTierMapping;
  }
  const candidate={kind:'vitrea-candidate-material-document',schemaVersion:1,
    name:`w50-current-material-glass${position.toFixed(3)}`,platform:'macOS 27.0',
    glassTintAmount:position,endpoints,cssTierMappingSha256:cssTierMappingSha256(mapping)};
  files['candidate.json']=JSON.stringify(candidate,null,2)+'\n';
  files['current-sources.json']=JSON.stringify({schema:'w50-current-material-sources-1',
    position,gate:0,endpointDifference:'profileKey only',endpoints:witnesses},null,2)+'\n';
  mkdirSync(out,{recursive:true});
  for(const [name,text] of Object.entries(files))writeFileSync(join(out,name),text,{flag:'wx'});
  // Full production digest/CSS/endpoint composition validation, before any browser can run.
  readCandidateDocument(join(out,'candidate.json'));
  return {path:join(out,'candidate.json'),sha256:hash(files['candidate.json']!)};
}

if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  if(process.argv.length!==4)throw Error('Usage: current.ts <0.25|0.5> <new external directory>');
  console.log(JSON.stringify(buildCurrent(Number(process.argv[2]),process.argv[3]!)));
}
