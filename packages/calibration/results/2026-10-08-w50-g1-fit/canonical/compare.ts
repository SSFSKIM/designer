/** Bounded native preflight before the production compare entrypoint's eager main. */
import {readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {admitNative} from './native-admission.ts';

const args=process.argv.slice(2);
if(args[0]!=='--admission' || args[2]!=='--receipt' || args[4]!=='--')throw Error('Bounded admission arguments required');
const bytes=readFileSync(args[1]!);
const requestSha256=createHash('sha256').update(bytes).digest('hex');
if(requestSha256!==process.env.W50_NATIVE_REQUEST_SHA256)throw Error('Changed selected native request');
const request=JSON.parse(bytes.toString());
const repo=resolve(fileURLToPath(new URL('.',import.meta.url)),'../../../../..');
const spec=JSON.parse(readFileSync(resolve(repo,'apps/reference-apple/scenes.json'),'utf8'));
const fixtures=resolve(repo,'apps/reference-apple/fixtures');
const manifest=JSON.parse(readFileSync(resolve(fixtures,'manifest.json'),'utf8'));
const receipt=admitNative(spec,manifest,fixtures,request);
const compareArgs=args.slice(5);
const value=(flag:string)=>compareArgs[compareArgs.indexOf(flag)+1];
if(value('--profile')!==request.profile || !request.scenes.includes(value('--scene')) ||
   value('--set')!==request.sets.join(',') || compareArgs.includes('--allow-colourless-tints')) {
  throw Error('Compare arguments differ from admitted native run');
}
writeFileSync(args[3]!,JSON.stringify({...receipt,requestSha256:createHash('sha256').update(bytes).digest('hex')},null,2)+'\n',{flag:'wx'});
// Only the global scan is bypassed: all production per-cell native/material/pose checks remain.
process.argv=[process.argv[0]!,process.argv[1]!,...compareArgs,'--allow-colourless-tints'];
await import('../../../cli/compare.ts');
