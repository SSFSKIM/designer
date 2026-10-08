/** DL5h transport only: retain both actual loads; admission is the separate repeat referee. */
import {mkdir,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve} from 'node:path';
type Capture={png:Buffer;report:unknown};
const sha=(raw:Buffer|string)=>createHash('sha256').update(raw).digest('hex');
export async function retainPair(directory:string,scene:string,tier:string,
  first:Capture,second:Capture,deterministic:boolean,repeatNoise:number|null) {
  await mkdir(directory,{recursive:true});
  async function save(name:string,raw:Buffer|string) {
    const path=resolve(directory,name);await writeFile(path,raw,{flag:'wx'});
    return {path,sha256:sha(raw)};
  }
  async function member(capture:Capture,ordinal:'first'|'second') {
    return {image:await save(`${scene}__${tier}${ordinal==='second'?'__repeat':''}.png`,capture.png),
      report:await save(`page__${tier}__${ordinal}.json`,JSON.stringify(capture.report,null,2)+'\n')};
  }
  const pair={schema:1,kind:'w50-retained-repeat-pair',reading:'first',scene,renderer:tier,
    deterministic,repeatNoise,first:await member(first,'first'),second:await member(second,'second')};
  await save(`repeat__${tier}.json`,JSON.stringify(pair,null,2)+'\n');
  return pair;
}
