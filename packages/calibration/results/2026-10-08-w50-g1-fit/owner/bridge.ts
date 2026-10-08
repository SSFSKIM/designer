import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';
import { prepareCurrent, evaluate } from './api.ts';
import { pinnedBytes, type Pin } from './referee.ts';
import { ownerContracts, projectCurrent, projectCurrentBatch } from './witness.ts';

/** JSON stdin/stdout only. A caller may persist stdout to its own write-once scratch file;
 * this bridge has no output pathname or canonical-writing mode. Every data argument is a
 * file pin. Evaluation reconstructs current evidence rather than trusting serialized numbers.
 *
 * contracts: {mode:'contracts',python} — source-only; python is the pinned interpreter path.
 * prepare: {mode:'prepare',inputsPin}
 * project-current: {mode:'project-current',inputsPin,completedReferencesPin,contractsPin,row}
 * project-current-batch: {mode:'project-current-batch',inputsPin,completedReferencesPin,contractsPin,inventoryPin}
 * evaluate: {mode:'evaluate',inputsPin,completedReferencesPin,candidatesPin,capturesPin,intrinsicPin?}
 * The files carry PrepareInputs, OwnerReport, MatrixInput[], Record<cell,Capture>, and
 * IntrinsicInputs respectively, as exported by api.ts/intrinsic.ts.
 */
export function executeRequest(request:any) {
  const fields:Record<string,string[]>={
    prepare:['mode','inputsPin'],
    evaluate:['mode','inputsPin','completedReferencesPin','candidatesPin','capturesPin','intrinsicPin'],
    contracts:['mode','python'],
    'project-current':['mode','inputsPin','completedReferencesPin','contractsPin','row'],
    'project-current-batch':['mode','inputsPin','completedReferencesPin','contractsPin','inventoryPin'],
  };
  if(!Object.hasOwn(fields,request?.mode)) throw new Error('Unknown owner bridge mode');
  const getPin=(field:string)=>{
    const pin=request[field] as Pin|undefined;
    if(!pin||typeof pin.path!=='string'||!pin.path.startsWith('/')
      ||typeof pin.sha256!=='string'||!/^[a-f0-9]{64}$/.test(pin.sha256)) {
      throw new Error(`Owner bridge requires content pin ${field}; raw numeric maps are not inputs`);
    }
    return pin;
  };
  const read=(field:string)=>JSON.parse(pinnedBytes(getPin(field)).toString());
  // Validate the request's full shape before opening files, so misspelled/raw fields do not
  // disappear silently while a differently named pinned value is consumed.
  const allowed=new Set(fields[request.mode]);
  if(Object.keys(request).some(k=>!allowed.has(k))) throw new Error('Unexpected field: bridge accepts only named pins/selectors');
  if(request.mode==='contracts') {
    if(typeof request.python!=='string'||!request.python.startsWith('/')) throw new Error('Pinned interpreter path required');
    return ownerContracts(request.python);
  }
  if(request.mode==='project-current') return projectCurrent(getPin('inputsPin'),
    getPin('completedReferencesPin'),getPin('contractsPin'),request.row);
  if(request.mode==='project-current-batch') return projectCurrentBatch(getPin('inputsPin'),
    getPin('completedReferencesPin'),getPin('contractsPin'),getPin('inventoryPin'));
  const inputs=read('inputsPin');
  const context=prepareCurrent(inputs);
  if(request.mode==='prepare') return context.current;
  return evaluate(context,read('candidatesPin'),read('capturesPin'),read('completedReferencesPin'),
    request.intrinsicPin===undefined?undefined:read('intrinsicPin'));
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href) {
  const output=executeRequest(JSON.parse(readFileSync(0,'utf8')));
  process.stdout.write(JSON.stringify(output)+'\n');
}
