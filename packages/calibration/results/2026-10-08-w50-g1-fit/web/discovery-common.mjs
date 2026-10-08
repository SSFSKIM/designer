// Source-discovery helpers are not imported by the runtime admission guard.
import {existsSync,readdirSync,realpathSync} from 'node:fs';
import {dirname,join,resolve,relative,isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
export const HERE=dirname(fileURLToPath(import.meta.url));
export const CAL=resolve(HERE,'../../..');
export const ROOT=realpathSync(resolve(CAL,'../..'));
export const WAVE=resolve(HERE,'..');

export function assertPreseal(wave=WAVE) {
  if(!existsSync(wave))return;
  for(const entry of readdirSync(wave,{withFileTypes:true})) {
    if(entry.name==='execution-root.json')throw Error('Discovery refused: execution root already sealed');
    if(entry.isDirectory() && entry.name!=='node_modules' && entry.name!=='.git')
      assertPreseal(join(wave,entry.name));
  }
}
export function inside(path,root) {
  const rel=relative(root,path);return !rel.startsWith('..') && !isAbsolute(rel);
}
export function assertDataPath(path,scratch) {
  if(typeof path!=='string' && !(path instanceof URL))return;
  const absolute=resolve(path instanceof URL?fileURLToPath(path):path);
  if(inside(absolute,resolve(scratch)))return;
  if(/\.(png|jpe?g|webp|tiff?|heic|zip|tar|gz)$/i.test(absolute) ||
    /\/(fixtures|web-captures[^/]*|generations|superseded)\//.test(absolute) ||
    /\/matrix\.json$/.test(absolute))throw Error(`Discovery refuses real measurement data: ${absolute}`);
}
export function freshExternal(path) {
  if(!isAbsolute(path) || existsSync(path))throw Error('Require a fresh scratch output directory');
  let parent=dirname(resolve(path));
  while(!existsSync(parent))parent=dirname(parent);
  const real=realpathSync(parent);
  for(let dir=real;;dir=dirname(dir)) {
    if(existsSync(join(dir,'.git')))throw Error('Require fresh scratch outside every checkout');
    if(dir===dirname(dir))break;
  }
  return resolve(path);
}
