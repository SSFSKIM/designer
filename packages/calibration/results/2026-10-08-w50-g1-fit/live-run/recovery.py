"""W50 G1 DL5p: the bind-only recovery of root 2's ONE assembled candidate under root 3.

Root 2's first initialize assembled the sole point (the candidate cohort and initializer.json
under fit/live-initializer/candidates/<digest>/) and then bind_arguments refused on a role
vocabulary seam (fit/live-initializer/attempt-1-refusal.json). DL5p (c) carries that point
forward by hash, with its root-2 provenance, and binds it under root 3; it is never
re-initialised or re-assembled, and its bytes never change.

The point is admitted only through the declaration beside this file (dl5p-recovery.json),
which states nothing but committed root-2 facts:
    ruling       DL5p's paragraph in the charter, by SHA-256, as committed at the ruling commit;
    predecessor  root 2's pin, its pre-fit evidence and seal, and the commit that sealed them;
    refusal      the preservation record and the commit that introduced it with the 11 files;
    initializer  initializer.json's pin, and cohort the two candidate documents by position.

evidence() authenticates every one of those against the working tree AND against git: each
file's bytes equal its blob at its commit, which is an ancestor of HEAD, so a byte rewritten
and re-pinned after the fact is still refused. The refusal's file list must be exactly the
cohort's closure (the two candidate documents, their eight endpoints and initializer.json),
and the provenance the point carries (initializer.json's preFitEvidence and every endpoint
method line that names a pre-fit evidence) must be root 2's pre-fit evidence and nothing else.

admit() also requires the root to register the declaration prospectively among its sealed
inputs and to be the DL5p successor of root 2: its supersedes record (schema
w50-live-root-supersession-2) pins root 2, is ruled by DL5p, and names root 2's committed pre-fit
history exactly. The dispatcher re-checks that link itself in the bind child (authority.py);
this check only decides that the operator may ask for a bind at all.

provenance() is also what the operator's candidate record reads at every later step: a point
whose provenance is not the root's own pre-fit evidence is admitted only with a recovery
record that admit() authenticates (run.py Operator.candidate). Nothing here widens what any
other root, record or provenance is admitted with.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess

SCHEMA = 'w50-live-run-dl5p-recovery-declaration-1'
RECORD = 'w50-live-run-dl5p-recovery-1'
LINK = 'w50-live-root-supersession-2'
REFUSAL = 'w50-initializer-attempt-preservation-1'
REFUSED = 'REFUSED_DURING_ARGUMENT_BINDING'
RULING = 'DL5p'
KEYS = {'schema', 'statement', 'ruling', 'predecessor', 'refusal', 'initializer', 'cohort'}
NAMED = re.compile(r'pre-fit evidence (\S+) sha256 ([0-9a-f]{64})')


class Refused(ValueError):
    """The recovery is not admitted; the message names a field, never a value."""


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text())


def require(condition, message):
    if not condition: raise Refused(message)


def pin(repo, path):
    path = Path(path).resolve()
    return {'path': str(path.relative_to(Path(repo).resolve())), 'sha256': sha(path)}


def checked(repo, item):
    require(isinstance(item, dict) and set(item) == {'path', 'sha256'} and isinstance(item['path'], str) and
            isinstance(item['sha256'], str) and re.fullmatch('[0-9a-f]{64}', item['sha256']), 'A recovery pin is malformed')
    repo = Path(repo).resolve(); path = (repo/item['path']).resolve()
    require(path.is_relative_to(repo) and path.is_file() and sha(path) == item['sha256'],
            'A recovery pin names changed or missing bytes')
    return path


def git(repo, *args): return subprocess.run(['git', '-C', str(repo), *args], capture_output=True)


def commit(repo, value):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{40}', value) and
            git(repo, 'cat-file', '-t', value).stdout == b'commit\n', 'A recovery commit is not a commit of this repository')
    require(git(repo, 'merge-base', '--is-ancestor', value, 'HEAD').returncode == 0, 'A recovery commit is not on this history')
    return value


def committed(repo, at, item):
    """The pinned bytes are the blob at `at`, as well as the working tree's."""
    path = checked(repo, item)
    blob = git(repo, 'cat-file', 'blob', f'{at}:{item["path"]}')
    require(blob.returncode == 0 and blob.stdout == path.read_bytes(), 'A recovery file differs from its committed bytes')
    return path


def paragraph(text, ident=RULING):
    """The ruling's paragraph: from the line opening with `<id> (` to the first blank line."""
    lines = text.splitlines(); starts = [i for i, l in enumerate(lines) if l.startswith(ident+' (')]
    require(len(starts) == 1, 'The charter does not hold exactly one ruling paragraph')
    out = []
    for line in lines[starts[0]:]:
        if not line.strip(): break
        out.append(line)
    return '\n'.join(out)+'\n'


def ruling_sha(text): return hashlib.sha256(paragraph(text).encode()).hexdigest()


def closure(repo, initializer, cohort):
    """The files the point is: initializer.json, then each candidate document (one per position,
    in position order) and its four endpoints. Root 2's point is 11 files."""
    require(isinstance(cohort, list) and len(cohort) == 2 and
            [c.get('position') if isinstance(c, dict) else None for c in cohort] == [.25, .5] and
            all(set(c) == {'position', 'path', 'sha256'} for c in cohort), 'The cohort is not one candidate per position')
    checked(repo, initializer); files = [{'path': initializer['path'], 'sha256': initializer['sha256']}]
    for item in cohort:
        path = checked(repo, {'path': item['path'], 'sha256': item['sha256']})
        document = load(path)
        require(document.get('glassTintAmount') == item['position'] and isinstance(document.get('endpoints'), dict) and
                len(document['endpoints']) == 4, 'A candidate document names another position or endpoint set')
        files.append({'path': item['path'], 'sha256': item['sha256']})
        for endpoint in document['endpoints'].values():
            target = (path.parent/endpoint['path']).resolve()
            require(target.parent == path.parent, 'A candidate endpoint is outside its candidate')
            files.append({'path': str(target.relative_to(Path(repo).resolve())), 'sha256': endpoint['sha256']})
    for item in files: checked(repo, item)
    require(len({f['path'] for f in files}) == len(files), 'The point names one file twice')
    return files


def _strings(value):
    if isinstance(value, str): yield value
    elif isinstance(value, dict):
        for item in value.values(): yield from _strings(item)
    elif isinstance(value, list):
        for item in value: yield from _strings(item)


def provenance(repo, initializer, cohort):
    """Every pre-fit evidence the point names: initializer.json's preFitEvidence and each endpoint
    method line's, distinct and sorted. A point whose initializer names none is refused."""
    named = load(checked(repo, initializer)).get('preFitEvidence')
    require(isinstance(named, dict) and set(named) == {'path', 'sha256'}, 'The initializer names no pre-fit evidence')
    found = {(named['path'], named['sha256'])}
    for item in closure(repo, initializer, cohort)[1:]:
        for text in _strings(load(checked(repo, item))):
            found |= set(NAMED.findall(text))
    return [{'path': p, 'sha256': s} for p, s in sorted(found)]


def evidence(repo, path):
    """The declaration, with every committed root-2 fact it states authenticated (module docstring)."""
    repo = Path(repo).resolve(); decl = load(path)
    require(isinstance(decl, dict) and set(decl) == KEYS and decl['schema'] == SCHEMA, 'Unknown recovery declaration')
    ruling, before, refusal = decl['ruling'], decl['predecessor'], decl['refusal']
    require(isinstance(ruling, dict) and set(ruling) == {'id', 'charter', 'commit', 'paragraphSha256'} and
            ruling['id'] == RULING and isinstance(ruling['charter'], str), 'The declaration names another ruling')
    commit(repo, ruling['commit'])
    shown = git(repo, 'show', f'{ruling["commit"]}:{ruling["charter"]}')
    require(shown.returncode == 0 and ruling_sha(shown.stdout.decode()) == ruling['paragraphSha256'] and
            ruling_sha((repo/ruling['charter']).read_text()) == ruling['paragraphSha256'],
            'The DL5p paragraph differs from the ruling as committed')
    require(isinstance(before, dict) and set(before) == {'root', 'preFitEvidence', 'preFitEvidenceSeal', 'commit'},
            'The declaration does not name root 2\'s pre-fit history')
    root2 = checked(repo, before['root']); commit(repo, before['commit'])
    evidence_path = committed(repo, before['commit'], before['preFitEvidence'])
    seal = committed(repo, before['commit'], before['preFitEvidenceSeal'])
    require(evidence_path.parent == root2.parent and
            evidence_path.name == root2.name.removesuffix('.json')+'.pre-fit-evidence.json' and
            seal.name == evidence_path.name+'.sha256' and
            seal.read_text() == f'{before["preFitEvidence"]["sha256"]}  {evidence_path.name}\n',
            'The pre-fit evidence is not root 2\'s own sealed slot')
    require(isinstance(refusal, dict) and set(refusal) == {'record', 'commit'}, 'The declaration names no refusal')
    commit(repo, refusal['commit'])
    record = load(committed(repo, refusal['commit'], refusal['record']))
    require(record.get('schema') == REFUSAL and record.get('status') == REFUSED and record.get('root') == before['root'],
            'The refusal is not root 2\'s argument-binding refusal')
    files = closure(repo, decl['initializer'], decl['cohort'])
    listed = [{'path': f.get('path'), 'sha256': f.get('sha256')} for f in record.get('files', [])]
    key = lambda f: (f['path'], f['sha256'])
    require(sorted(listed, key=key) == sorted(files, key=key) and len(listed) == len(files),
            'The refusal does not preserve exactly the declared point')
    for item in files: committed(repo, refusal['commit'], item)
    require(provenance(repo, decl['initializer'], decl['cohort']) == [before['preFitEvidence']],
            'The point carries provenance other than root 2\'s pre-fit evidence')
    return decl


def admit(repo, root, doc, path):
    """evidence(), and the root registers this declaration and is root 2's DL5p successor."""
    repo = Path(repo).resolve(); decl = evidence(repo, path); before = decl['predecessor']
    require(pin(repo, path) in doc.get('inputs', []), 'The root does not register this recovery declaration')
    link = doc.get('supersedes')
    require(isinstance(link, dict) and link.get('schema') == LINK and link.get('root') == before['root'] and
            (link.get('ruling') or {}).get('id') == RULING, 'The root is not root 2\'s DL5p successor')
    history = link.get('history')
    require(isinstance(history, dict) and history.get('commit') == before['commit'] and
            history.get('entries') == [before['preFitEvidence'], before['preFitEvidenceSeal']],
            'The root admits another pre-fit history than the declared one')
    require(Path(root).resolve().parent == checked(repo, before['root']).parent, 'The root is not beside root 2')
    return decl


def declare(repo, *, charter, ruling_commit, root, evidence_commit, refusal, refusal_commit, initializer, cohort, statement):
    """The declaration's body from its named facts (used once for dl5p-recovery.json, and by tests)."""
    repo = Path(repo).resolve(); root = Path(root).resolve()
    evidence_path = root.with_name(root.name.removesuffix('.json')+'.pre-fit-evidence.json')
    return {'schema': SCHEMA, 'statement': statement,
            'ruling': {'id': RULING, 'charter': charter, 'commit': ruling_commit,
                       'paragraphSha256': ruling_sha((repo/charter).read_text())},
            'predecessor': {'root': pin(repo, root), 'preFitEvidence': pin(repo, evidence_path),
                            'preFitEvidenceSeal': pin(repo, str(evidence_path)+'.sha256'), 'commit': evidence_commit},
            'refusal': {'record': pin(repo, refusal), 'commit': refusal_commit},
            'initializer': pin(repo, initializer),
            'cohort': [{'position': p, **pin(repo, path)} for p, path in cohort]}
