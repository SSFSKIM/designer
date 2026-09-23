#!/usr/bin/env python3
"""W34 identification roles, payload access and one-exposure receipt (§5.174).

This is a procedural boundary, not encryption. Producers may archive every
state, including holdout, but publish only inventory/hashes/admission. Readers
check identification membership before opening any pixel, crop or statistic;
the fixture's broad probe role is never an analytical permission.
"""
import argparse
from contextlib import contextmanager
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
ROLES = ('calibration', 'validation', 'holdout')


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def stable(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def native_only(component):
    if component['kind'] == 'none' or component.get('opaque') is True: return True
    if component['kind'] == 'group': return any(native_only(s) for s in component['items'])
    if component['kind'] == 'stack': return any(native_only(component[k]) for k in ['base','over'])
    return False


class Wave:
    def __init__(self, scenes, split, pins):
        self.scenes_path, self.split_path = Path(scenes), Path(split)
        pinned = json.loads(Path(pins).read_text())
        self.scenes_sha, self.split_sha = digest(scenes), digest(split)
        if self.scenes_sha != pinned['scenesSha256']: raise ValueError('scenes hash mismatch')
        if self.split_sha != pinned['splitSha256']: raise ValueError('split hash mismatch')
        self.spec = json.loads(self.scenes_path.read_text())
        self.split = json.loads(self.split_path.read_text())
        self.scenes = {s['id']:s for s in self.spec['scenes']}
        assigned = [s for role in ROLES for s in self.split[role]]
        if len(self.scenes) != len(self.spec['scenes']) or len(assigned) != len(set(assigned)) \
                or set(assigned) != set(self.scenes):
            raise ValueError('identification membership must be complete, unique and disjoint')
        fixture = self.spec['split']
        if set(fixture.get('probe',[])) != set(self.scenes) or any(
                fixture.get(role,[]) for role in ['calibration','validation','holdout','recorded']):
            raise ValueError('fixture membership must be probe only')
        self.roles = {s:role for role in ROLES for s in self.split[role]}
        self.cells = set()
        for profile in self.spec['profiles']:
            ids = self.scenes if profile['scenes'] == 'all' else profile['scenes']
            for sid in ids:
                if sid not in self.scenes: raise ValueError('profile membership names unknown scene')
                self.cells.add(profile['key']+'/'+sid)

    def select(self, roles=('calibration','validation'), authorization=None):
        if not roles or any(r not in ROLES for r in roles): raise ValueError('unknown identification role')
        if 'holdout' in roles:
            if authorization is None: raise PermissionError('holdout requires the wave receipt')
            authorization.check(self)
        return sorted(s for s,r in self.roles.items() if r in roles)

    def launch_scenes(self, roles=('calibration','validation'), authorization=None):
        return [s for s in self.select(roles, authorization)
                if not native_only(self.spec['components'][self.scenes[s]['component']])]

    def reader(self, root, roles=('calibration','validation'), authorization=None):
        return Reader(self, root, roles, authorization)


class Reader:
    def __init__(self, wave, root, roles, authorization):
        self.wave, self.root = wave, Path(root).resolve()
        self.allowed = set(wave.select(roles, authorization))
        self.authorization = authorization
        raw_inventory = (self.root/'inventory.json').read_bytes()
        self.generation = hashlib.sha256(raw_inventory).hexdigest()
        if 'holdout' in roles: authorization.check(wave, self.generation)
        inventory = json.loads(raw_inventory)
        if inventory.get('scenesSha256') != wave.scenes_sha or inventory.get('splitSha256') != wave.split_sha:
            raise ValueError('evidence generation does not name this pinned declaration')
        self.entries = {}
        for row in inventory['entries']:
            cell = row['cell']
            if cell not in wave.cells: raise ValueError('inventory names undeclared cell')
            sid = cell.split('/',1)[1]
            parts = Path(row['path']).parts
            if not parts or parts[0] != wave.roles[sid] or '..' in parts or Path(row['path']).is_absolute():
                raise ValueError('payload placement disagrees with identification role')
            key = (cell,row['kind'])
            if key in self.entries: raise ValueError('duplicate payload identity')
            self.entries[key] = row

    def read(self, cell, kind):
        if cell not in self.wave.cells: raise ValueError('undeclared cell')
        sid = cell.split('/',1)[1]
        if sid not in self.allowed:
            raise PermissionError(self.wave.roles[sid]+' payload is outside authorised identification roles')
        if self.wave.roles[sid] == 'holdout': self.authorization.check(self.wave, self.generation)
        row = self.entries[(cell,kind)]
        path = (self.root/row['path']).resolve()
        if self.root not in path.parents: raise ValueError('payload escaped evidence root')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != row['sha256']: raise ValueError('payload hash mismatch')
        return raw

    def report_inventory(self):
        # Never read or deserialise payload here, even for admitted holdout cells.
        return [{k:r[k] for k in ['cell','kind','sha256','path']} for r in self.entries.values()]


class _Authorization:
    def __init__(self, configuration):
        self.configuration, self.active = configuration, True

    def check(self, wave, generation=None):
        if not self.active: raise PermissionError('inactive exposure receipt')
        if self.configuration['scenes'] != wave.scenes_sha or self.configuration['split'] != wave.split_sha:
            raise PermissionError('receipt does not authorise this declaration')
        if generation is not None and generation not in self.configuration['generation']:
            raise PermissionError('receipt does not authorise this evidence generation')


class Receipt:
    def __init__(self, log, configuration):
        self.log, self.configuration = Path(log), configuration
        if not {'scenes','split','generation','instrument','closure','candidate'} <= set(configuration):
            raise ValueError('incomplete identification configuration')
        generations = configuration['generation']
        if not isinstance(generations, list) or not generations or any(
                not isinstance(g, str) or len(g) != 64 or any(c not in '0123456789abcdef' for c in g)
                for g in generations):
            raise ValueError('generation must freeze the permitted inventory SHA-256 hashes')
        self.sha = hashlib.sha256(stable(configuration).encode()).hexdigest()

    def append(self,event):
        self.log.parent.mkdir(parents=True,exist_ok=True)
        with self.log.open('a') as f:
            f.write(stable(dict(at=stamp(),event=event,configurationSha256=self.sha,
                                configuration=self.configuration))+'\n')
            f.flush();os.fsync(f.fileno())

    @contextmanager
    def expose(self):
        lock = self.log.with_suffix(self.log.suffix+'.lock')
        try: fd = os.open(lock,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        except FileExistsError: raise PermissionError('exposure already active or interrupted')
        os.close(fd)
        token = None
        try:
            # The entire wave is spent, not just an individual candidate digest.
            # A failed attempt and a process killed after begin both consume it.
            if self.log.exists() and self.log.stat().st_size:
                raise PermissionError('wave holdout exposure already spent; changed candidates do not reset it')
            self.append('begin')
            token = _Authorization(self.configuration)
            try:
                yield token
            except BaseException:
                self.append('failed');raise
            else: self.append('complete')
        finally:
            if token is not None: token.active = False
            lock.unlink()


def committed(path):
    path = Path(path).resolve()
    relative = path.relative_to(ROOT)
    saved = subprocess.check_output(['git','-C',str(ROOT),'show','HEAD:'+str(relative)],stderr=subprocess.PIPE)
    if saved != path.read_bytes(): raise ValueError('configuration input is not committed: '+str(path))
    return hashlib.sha256(saved).hexdigest()


def configuration(wave, inventories, candidate, runner):
    # Exact committed inputs, not today's shipped material: the canonical G3
    # holdout recorder intentionally remains untouched.
    return dict(scenes=wave.scenes_sha,split=wave.split_sha,generation=sorted({digest(p) for p in inventories}),
                instrument={str(p.relative_to(ROOT)):committed(p) for p in
                    [HERE/'instrument.py',HERE/'archive.py',HERE/'wave.py',Path(runner).resolve()]},
                closure=committed(HERE/'closure.json'),
                candidate=dict(sha256=committed(candidate),document=json.loads(Path(candidate).read_text())))


def default_wave():
    return Wave(ROOT/'apps/reference-apple/scenes-w34-contour.json',HERE/'split.json',HERE/'pins.json')


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    sub=ap.add_subparsers(dest='action',required=True)
    plan=sub.add_parser('plan');plan.add_argument('--roles',default='calibration,validation')
    plan.add_argument('--fixtures',type=Path,required=True);plan.add_argument('--out-matrix',type=Path,required=True)
    plan.add_argument('--captures',type=Path,required=True);plan.add_argument('--execute',action='store_true')
    report=sub.add_parser('inventory');report.add_argument('root',type=Path)
    expose=sub.add_parser('expose');expose.add_argument('--inventory',type=Path,action='append',required=True)
    expose.add_argument('--candidate',type=Path,required=True);expose.add_argument('--runner',type=Path,required=True)
    args=ap.parse_args();wave=default_wave()
    if args.action=='inventory': print(json.dumps(wave.reader(args.root).report_inventory(),indent=2))
    elif args.action=='plan':
        ids=wave.launch_scenes(args.roles.split(','))
        if not ids: raise ValueError('no glass scenes selected')
        # Both output seams are mandatory, and neither may reach canonical data.
        canonical=[ROOT/'apps/reference-apple/fixtures',ROOT/'packages/calibration/results/matrix.json',
                   ROOT/'packages/calibration/web-captures']
        for path in [args.fixtures,args.out_matrix,args.captures]:
            resolved=path.resolve()
            if any(resolved==c or c in resolved.parents for c in canonical):
                raise ValueError('wave launcher refuses canonical fixture or output paths')
        command=['pnpm','--dir',str(ROOT),'--filter','@vitrea/calibration','run','compare','--',
                 '--set','probe','--scene',','.join(ids),'--renderer','webgpu',
                 '--out-matrix',str(args.out_matrix.resolve()),'--write-partial']
        env={**os.environ,'VITREA_SCENES':str(wave.scenes_path),'VITREA_FIXTURES':str(args.fixtures.resolve()),
             'VITREA_WEB_CAPTURES':str(args.captures.resolve())}
        print(json.dumps(dict(command=command,environment={k:v for k,v in env.items() if k.startswith('VITREA_')}),indent=2))
        if args.execute: subprocess.run(command,env=env,check=True)
    else:
        if any(importlib.util.find_spec(name) is None for name in ['numpy','PIL']):
            raise SystemExit('expose needs Python3.12 with numpy/PIL; no receipt was spent')
        config=configuration(wave,args.inventory,args.candidate,args.runner)
        with Receipt(HERE/'wave-identification-receipt.jsonl',config).expose() as token:
            runpy.run_path(str(args.runner),init_globals={'W34_WAVE':wave,'W34_AUTHORIZATION':token},run_name='__main__')


if __name__=='__main__':main()
