/** A driver invocation is one remaining, source-bound W51 member, not arbitrary CLI data. */
import {readFileSync,realpathSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';

const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const canonical=value=>Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?
  Object.fromEntries(Object.keys(value).sort().map(key=>[key,canonical(value[key])])):value;
const same=(a,b)=>JSON.stringify(canonical(a))===JSON.stringify(canonical(b));
function pinned(pin,base='/') {
  const path=resolve(base,pin.path);
  if(realpathSync(path)!==path)throw Error('W51 evidence path is not ordinary');
  const bytes=readFileSync(path);
  if(sha(bytes)!==pin.sha256)throw Error('W51 renderer content pin changed');
  return {path,bytes,value:JSON.parse(bytes)};
}

export function validateAuthority(authority,argv,leaseToken) {
  const root=pinned(authority.root),repo=root.value.repo;
  if(readFileSync(root.path+'.sha256','utf8')!==`${authority.root.sha256}  ${root.path.split('/').at(-1)}\n`) {
    throw Error('W51 renderer root is unsealed');
  }
  const contract=pinned(authority.contract),batch=pinned(authority.batch),claim=pinned(authority.claim);
  if(contract.value.executionRootSha256!==authority.root.sha256 ||
     contract.value.batch.sha256!==authority.batch.sha256 ||
     !Object.values(root.value.batches).some(pin=>same(pin,contract.value.batch)) ||
     !same(claim.value.logicalContract,authority.contract) || claim.value.gpuLease!==leaseToken) {
    throw Error('W51 renderer authority does not bind its actual phase/lease');
  }
  if(existsSync(contract.path+'.phase/analysis.started.json'))throw Error('W51 analysis already consumed');
  const attempt=pinned(claim.value.attempt);
  if(claim.path!==resolve(dirname(attempt.path),'started.json') ||
     !same(attempt.value.logicalContract,authority.contract) ||
     !attempt.value.members.some(member=>same(member,authority.member)) ||
     existsSync(resolve(dirname(attempt.path),'failure.json')) ||
     existsSync(resolve(dirname(attempt.path),'complete.json')) ||
     existsSync(resolve(dirname(attempt.path),'members',authority.member.id+'.json')) ||
     existsSync(resolve(dirname(attempt.path),'recovered',authority.member.id+'.json'))) {
    throw Error('W51 member is not in an active capture attempt');
  }
  process.kill(claim.value.pid,0);
  const member=authority.member,run=member.run,base=batch.value.runs[member.runIndex];
  const expected={...base,scenes:[member.scene],candidate:member.candidate,
    captureRoot:run.captureRoot,matrixPath:run.matrixPath};
  delete expected.baselineCandidate;
  const destination=resolve(contract.value.logicalOutput,'attempts',String(attempt.value.ordinal).padStart(6,'0'),
    'quarantine',member.id);
  if(!same(expected,run) || !base.scenes.includes(member.scene) || member.lane!=='candidate' ||
     resolve(run.captureRoot)!==resolve(destination,'captures') ||
     resolve(run.matrixPath)!==resolve(destination,'matrix.json') ||
     !root.value.cohort.some(pin=>same(pin,run.candidate)))throw Error('W51 render member changed fixed batch');
  const candidate=pinned(run.candidate,repo);
  for(const pin of Object.values(candidate.value.endpoints))pinned(pin,dirname(candidate.path));
  const match=/^apple-macos-27\.0-([12])x-(dark|light)-standard-glass(0\.25|0\.5)$/.exec(run.profile);
  if(!match)throw Error('W51 renderer profile is outside the fixed cohort');
  const wanted=run.sceneSource==='canonical'?
    [member.scene,'--renderer',run.renderer,'--scale',match[1],'--color-scheme',match[2],
      '--candidate-document',candidate.path,'--out',resolve(run.captureRoot,run.profile),'--alpha']:
    ['--renderer',run.renderer,'--scale',match[1],'--color-scheme','dark','--frames','32',
      '--candidate-document',candidate.path,'--out',run.captureRoot,member.scene];
  if(!same(argv,wanted))throw Error('W51 renderer arguments differ from the fixed member');
  return {root:authority.root,contract:authority.contract,batch:authority.batch,member:member.id};
}

export function admit(argv=process.argv.slice(2)) {
  const path=process.env.W51_MEMBER_AUTHORITY,digest=process.env.W51_MEMBER_AUTHORITY_SHA256;
  if(!path || !digest)throw Error('W51 member authority required');
  const authority=pinned({path,sha256:digest});
  return validateAuthority(authority.value,argv,readFileSync('/tmp/w49-gpu.lock','utf8'));
}
