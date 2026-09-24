"""Prove every pre-existing index value remains byte-identical (§5.179)."""
import json,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3];rel='packages/calibration/results/superseded/index.json'
old=subprocess.check_output(['git','-C',str(ROOT),'show','26be8ede:'+rel]).decode();new=(ROOT/rel).read_text();before=json.loads(old);after=json.loads(new);decoder=json.JSONDecoder()
def raw_value(text,key):
    match=re.search(re.escape(json.dumps(key))+r'\s*:\s*',text)
    if not match:raise ValueError(key)
    _,end=decoder.raw_decode(text,match.end());return text[match.end():end]
files={name:raw_value(old,name)==raw_value(new,name) for name in before['files']}
old_lookup=raw_value(old,'byDocumentSha256');new_lookup=raw_value(new,'byDocumentSha256')
aliases={h:raw_value(old_lookup,h)==raw_value(new_lookup,h) for h in before['byDocumentSha256']}
metadata={k:raw_value(old,k)==raw_value(new,k) for k in ['what','rule','claimsFields']}
result=dict(sourceCommit='26be8ede',files=files,aliases=aliases,metadata=metadata,sharedReceded=after['sharedReceded'],newFiles=sorted(set(after['files'])-set(before['files'])))
with (HERE/'index-history-preservation.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
assert all(files.values()) and all(aliases.values()) and all(metadata.values())
print('byte-identical index entries:',len(files),'files,',len(aliases),'aliases,',len(metadata),'metadata fields; added',result['newFiles'])
