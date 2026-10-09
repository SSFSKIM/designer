// DL5f: the replacement NEWBED host, shared unchanged by current/candidate and GPU/CSS.
// Canonical scene.ts and its historical source-profile box model remain untouched.
import {readFileSync,realpathSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
export const SCENES=fileURLToPath(new URL('../../2026-10-08-w50-g0-declaration/bed/scenes-w50.json',import.meta.url));
const SCENES_SHA='945e66e1f5daa34d693e2a8d82404740b4bee8e6af3b02ddd8624fdba99a1a8b';
const HTML=fileURLToPath(new URL('../../../web/index.html',import.meta.url));
export function admitHost(scenes=process.env.VITREA_SCENES) {
  if(typeof scenes!=='string' || realpathSync(scenes)!==realpathSync(SCENES) ||
    createHash('sha256').update(readFileSync(scenes)).digest('hex')!==SCENES_SHA)
    throw Error('Replacement host requires exact sealed W50 NEWBED scenes');
}
export function installHost(html,context,scenes=process.env.VITREA_SCENES) {
  admitHost(scenes);
  if(realpathSync(context.filename)!==realpathSync(HTML))throw Error('Unexpected replacement host HTML');
  if(!html.includes('id="stage"') || !html.includes('src="./scene.ts"'))throw Error('Missing production stage entry');
  return [{tag:'style',attrs:{id:'w50-dl5f-border-box'},
    children:'.glass-host { box-sizing: border-box; }',injectTo:'head'}];
}
export function hostPlugin() {
  admitHost();
  return {name:'w50-dl5f-newbed-host',transformIndexHtml:{order:'pre',handler:installHost}};
}
