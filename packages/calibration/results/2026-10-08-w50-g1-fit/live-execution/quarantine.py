"""Instrument publication boundary; role discipline, NOT same-user OS isolation.

Raw child streams and numerical payloads remain in quarantine. Public events are
constructed from an allowlist rather than redacted arbitrary objects. Agents must not
open quarantine/native archives directly before the full-union analytical marker.
"""
import contextlib
import hashlib
import json
import os
import re
from pathlib import Path
import sys
import traceback

CODES={'CAPTURE_QUALIFIED','ATTEMPT_COMPLETE','INSTRUMENT_FAULT','CENSUS_REFUSED','LEASE_LOST',
       'NATIVE_COMPLETE','ANALYSIS_COMPLETE','ANALYSIS_STOPPED','REFUSED'}
FIELDS={'phase','attempt','member','retained','remaining','analysisStarted','nativeComplete'}

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def public_event(code,**metadata):
    if code not in CODES or not set(metadata)<=FIELDS:raise ValueError('Not an allowlisted public event')
    if any(type(value) not in (str,int,bool) for value in metadata.values()):raise ValueError('Public metadata must be scalar')
    if 'phase' in metadata and metadata['phase'] not in ('fit','gate','exposure'):raise ValueError('Invalid public phase')
    for key,value in metadata.items():
        if key in ('attempt','retained','remaining') and (type(value) is not int or value<0):raise ValueError('Invalid public count')
        if key in ('analysisStarted','nativeComplete') and type(value) is not bool:raise ValueError('Invalid public state')
        if key=='member' and (not isinstance(value,str) or not re.fullmatch('[a-f0-9]{64}',value)):raise ValueError('Invalid opaque member identity')
    return {'schema':'w50-live-public-event-1','code':code,**metadata}


def run_private(log,callback):
    """Internal callback boundary. The caller must never publish the success payload."""
    log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('x') as stream:return _capture_stream(stream,callback)


def run_silent(callback):
    with open(os.devnull,'w') as stream:return _capture_stream(stream,callback)


def _capture_stream(stream,callback):
    saved=[os.dup(1),os.dup(2)]
    try:
        for out in (sys.stdout,sys.stderr):
            try:out.flush()
            except (AttributeError,OSError):pass
        os.dup2(stream.fileno(),1);os.dup2(stream.fileno(),2)
        with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
            try:return True,callback()
            except BaseException:
                traceback.print_exc(file=stream)
                return False,{'code':'INSTRUMENT_FAULT'}
    finally:
        stream.flush()
        for fd,original in zip((1,2),saved):os.dup2(original,fd);os.close(original)


def read_payload(context,item):
    dispatcher=sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:raise ValueError('No real analytical capability')
    dispatcher.require_context(context)
    dispatcher.require_payload(context,item)
    if context.get('stage')!='analysis':raise ValueError('Protected payload is sealed until full-union analysis')
    path=Path(item['path'])
    if not path.is_file() or sha(path)!=item['sha256']:raise ValueError('Protected payload changed')
    return json.loads(path.read_text())
