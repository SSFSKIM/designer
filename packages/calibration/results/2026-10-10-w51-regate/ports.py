"""Declarative, reviewable source wiring deltas over immutable W50 scientific components.

Generated ports are ordinary prospective sources, not runtime patches. This module is used
only to author and compare them. Every listed replacement must occur exactly once; all other
syntax is inherited verbatim. DL5 adds the explicitly fingerprinted policy functions and
exact grading/wiring edits below; measurement and historical comparisons stay inherited.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIT = HERE.parent/'2026-10-08-w50-g1-fit'
CURRENT = HERE.parent/'2026-10-08-w50-g1-current3'


def replace(text, old, new):
    if text.count(old) != 1: raise ValueError('Ambiguous scientific port replacement: '+old[:80])
    return text.replace(old, new)


def expected():
    output = {}
    old = FIT/'judge/live.py'; text = old.read_text()
    text = replace(text, 'HERE = Path(__file__).resolve().parent',
        "HERE = Path(__file__).resolve().parent.parent/'2026-10-08-w50-g1-fit/judge'")
    text = replace(text, "root = live.sealed(context['executionRoot'])", "root = live.scientific_inputs(context)")
    text = replace(text, "root['phaseDependencies'] != context['phaseDependencies']", 'False')
    text = replace(text, "        raise ValueError('Analysis context differs from its sealed root')\n    return root",
        "        raise ValueError('Analysis context differs from its sealed dataset')\n    live.validate_context_population(context, root)\n    return root")
    text = replace(text, "T = source(HERE/'targets.py', 'w50_judge_live_targets')",
        "T = source(Path(__file__).resolve().parent/'judge_targets.py', 'w51_judge_targets')")
    output['judge.py'] = (old, text)

    old = FIT/'judge/targets.py'; text = old.read_text()
    text = replace(text, "R = source(HERE/'rules.py', 'w50_judge_targets_rules')",
        "R = source(HERE/'judge_rules.py', 'w51_judge_rules')")
    output['judge_targets.py'] = (old, text)

    old = FIT/'judge/rules.py'; text = old.read_text()
    text = replace(text, 'HERE = Path(__file__).resolve().parent',
        "HERE = Path(__file__).resolve().parent.parent/'2026-10-08-w50-g1-fit/judge'")
    text = replace(text, "KEY = ('profile', 'renderer', 'scene', 'statistic')",
        "Q = types.ModuleType('w51_judge_projection'); Q.__file__ = str(HERE.parent/'measurement/projection.py')\n"
        "exec(compile(Path(Q.__file__).read_bytes(), Q.__file__, 'exec'), Q.__dict__)\n"
        "KEY = ('profile', 'renderer', 'scene', 'statistic')")
    text = replace(text,
        "frozen=row['sceneSource'] == 'canonical' and row['renderer'] == 'webgpu' and name == row['statistic']",
        "frozen=row['sceneSource'] == 'canonical' and name == row['statistic'] and Q.frozen_scope(row['originalReference'])")
    output['judge_rules.py'] = (old, text)

    old = FIT/'measurement/phase.py'; text = old.read_text()
    text = replace(text, 'HERE = Path(__file__).resolve().parent',
        "HERE = Path(__file__).resolve().parent.parent/'2026-10-08-w50-g1-fit/measurement'")
    text = replace(text, "S = source(HERE/'phase_sources.py', 'w50_phase_sources')",
        "S = source(Path(__file__).resolve().parent/'phase_sources.py', 'w51_phase_sources')")
    text = replace(text, "root = dispatcher.sealed(context['executionRoot'])", "root = dispatcher.scientific_inputs(context)")
    text += '\n\ndef evaluate(context, captures, config):\n    return measure_phase(context, captures, config)\n'
    output['measurement.py'] = (old, text)

    old = FIT/'measurement/phase_sources.py'; text = old.read_text()
    text = replace(text, 'HERE = Path(__file__).resolve().parent',
        "PORT = Path(__file__).resolve().parent\nHERE = PORT.parent/'2026-10-08-w50-g1-fit/measurement'")
    text = replace(text, "C = source(CURRENT3/'canonical/adapter.py', 'w50_phase_paired_canonical')",
        "C = source(PORT/'canonical/adapter.py', 'w51_phase_paired_canonical')")
    text = replace(text, "L = source(FIT/'live-roles/common.py', 'w50_phase_live_role_common')",
        "L = source(PORT/'role_common.py', 'w51_phase_live_role_common')\nAUTH = source(PORT/'semantics.py', 'w51_scene_authority')")
    text = replace(text, "root != self.dispatcher.sealed(context['executionRoot'])", "root != self.dispatcher.scientific_inputs(context)")
    text = replace(text, "            if Path(pins['scenes']['path']).resolve() != C.SCENES or doc['canvas'] != plan['canvas']:",
        "            AUTH.same_scene(pins['scenes'], C.scenes_path(run), self.root['externalInputs'] + self.root['inputs'])\n            if doc['canvas'] != plan['canvas']:")
    text = replace(text,
        "        # The root's own composed current evidence (authority.current_authority binds its ordered\n        # instrument/result chains at root admission); measured against these same native reads.",
        "        # W51 imports this completed current evidence by its dataset content pin. Historical\n        # composition metadata is preserved, but no historical source-proof chain is executed.")
    text = replace(text, "AUTH = source(PORT/'semantics.py', 'w51_scene_authority')",
        "AUTH = source(PORT/'semantics.py', 'w51_scene_authority')\nSTATIC = source(PORT/'static.py', 'w51_static_reference_authority')")
    text = replace(text, "        canonical = self.registered(config['canonicalReferenceEvidence'])",
        "        STATIC.canonical_authority(self.dispatcher.sealed(context['executionRoot']), root, config)\n"
        "        canonical = self.registered(config['canonicalReferenceEvidence'])")
    output['phase_sources.py'] = (old, text)

    old = FIT/'live-roles/common.py'; text = old.read_text()
    text = replace(text, 'HERE = Path(__file__).resolve().parent',
        "HERE = Path(__file__).resolve().parent.parent/'2026-10-08-w50-g1-fit/live-roles'")
    text = text.replace("root = live.sealed(context['executionRoot'])", "root = live.scientific_inputs(context)")
    text = replace(text, 'helper.S.M.N.required_arguments(inventory)',
        'helper.S.M.N.required_arguments(helper.S.STATIC.numerical_inventory(context))')
    output['role_common.py'] = (old, text)

    old = FIT/'live-roles/capture.py'; text = old.read_text()
    text = replace(text, "str(HERE/'common.py')", "str(HERE/'role_common.py')")
    text = replace(text, "(HERE/'common.py').read_bytes()", "(HERE/'role_common.py').read_bytes()")
    text = replace(text, "TRANSPORTS = {'canonical': str((C.CURRENT3/'canonical/adapter.py').relative_to(REPO)),",
        "TRANSPORTS = {'canonical': str((HERE/'canonical/adapter.py').relative_to(REPO)),")
    text = replace(text, "str((C.CURRENT3/'web/adapter.py').relative_to(REPO))", "str((HERE/'web/adapter.py').relative_to(REPO))")
    text = replace(text, 'C.sha(canonical.SCENES)', 'C.sha(canonical.scenes_path(run))')
    text = replace(text,
        "The config (schema w50-live-capture-config-1) pins the two transports by content. Their paths\nare fixed to CURRENT3's DL5h transports, so a config cannot route a member elsewhere.",
        "The config (schema w50-live-capture-config-1) pins the prospective W51 ports of CURRENT3's\npaired transports. Their paths are fixed; neither dataset can select another implementation.")
    output['capture.py'] = (old, text)

    old = CURRENT/'web/adapter.py'; text = old.read_text()
    text = replace(text, 'HERE = Path(__file__).resolve().parent',
        "PORT = Path(__file__).resolve().parent\nHERE = PORT.parent.parent/'2026-10-08-w50-g1-current3/web'")
    text = replace(text, "str(HERE/'capture-web.ts'),'--renderer'", "str(PORT/'capture-web.ts'),'--renderer'")
    text = replace(text, "        argv = ['node','--import','tsx','--import',str(HERE/'node-guard.mjs'),",
        "        env.update(sys.modules['w50_g1_dispatch'].render_environment(context,run))\n        argv = ['node','--import','tsx','--import',str(HERE/'node-guard.mjs'),")
    output['web/adapter.py'] = (old, text)

    old = CURRENT/'canonical/adapter.py'; text = old.read_text()
    text = replace(text, "WEB = HERE.parent/'web'", "WEB = CAL/'results/2026-10-08-w50-g1-current3/web'")
    text = replace(text, "doc=read(SCENES) if document is None else document", "doc=read(scenes_path(run)) if document is None else document")
    text = replace(text, "def capture_environment(root,closure,digest,captures,matrix,guard):",
        "def capture_environment(root,closure,digest,captures,matrix,guard,scenes):")
    text = replace(text, "VITREA_SCENES=str(Path(root)/'apps/reference-apple/scenes.json')", "VITREA_SCENES=str(scenes)")
    text = replace(text, "root=read(context['executionRoot'])", "root=dispatcher.scientific_inputs(context)")
    text = replace(text, "required=[SCENES,ROOT/'pnpm-lock.yaml'", "required=[scenes_path(run),ROOT/'pnpm-lock.yaml'")
    text = replace(text, "GUARD_WEB/'node-guard.mjs')\n    env['W50_NATIVE", "GUARD_WEB/'node-guard.mjs',scenes_path(run))\n    env['W50_NATIVE")
    text = replace(text, "scenesSha256=sha(SCENES)", "scenesSha256=sha(scenes_path(run))")
    text = replace(text, "str(WEB/'capture-web.ts'),scene", "str(HERE.parent/'web/capture-web.ts'),scene")
    text = replace(text, "    env['W50_NATIVE_REQUEST_SHA256']=sha(admission)",
        "    env.update(dispatcher.render_environment(context,run))\n    env['W50_NATIVE_REQUEST_SHA256']=sha(admission)")
    text += '''\n\ndef scenes_path(run):\n    pin = run.get('scenesDocument')\n    if not isinstance(pin,dict): raise ValueError('Canonical run needs its dataset scene document')\n    path = ROOT/pin['path']\n    if path.resolve()!=path or path.is_symlink() or sha(path)!=pin['sha256']:\n        raise ValueError('Changed dataset scene document')\n    return path\n'''
    output['canonical/adapter.py'] = (old, text)

    old = CURRENT/'canonical/compare.ts'; text = old.read_text()
    text = replace(text, "const spec=JSON.parse(readFileSync(resolve(repo,'apps/reference-apple/scenes.json'),'utf8'));",
        "if(!process.env.VITREA_SCENES)throw Error('Bound dataset scene document required');\nconst spec=JSON.parse(readFileSync(process.env.VITREA_SCENES,'utf8'));")
    output['canonical/compare.ts'] = (old, text)
    old = CURRENT/'canonical/native-admission.ts'
    output['canonical/native-admission.ts'] = (old, old.read_text())

    old = CURRENT/'repeat/admission.py'; text = old.read_text()
    text = replace(text, 'HERE=Path(__file__).resolve().parent',
        "PORT=Path(__file__).resolve().parent\nHERE=PORT.parent/'2026-10-08-w50-g1-current3/repeat'")
    text = replace(text, "S=source(HERE/'sources.py','w50_repeat_sources')", "S=source(PORT/'repeat_sources.py','w51_repeat_sources')")
    text = replace(text, "root=dispatcher.sealed(context['executionRoot'])", "root=dispatcher.scientific_inputs(context)")
    text = replace(text, "adapter=source(HERE.parent/('web' if run['sceneSource']=='w50' else 'canonical')/'adapter.py',",
        "adapter=source((HERE.parent/'web/adapter.py' if run['sceneSource']=='w50' else PORT/'canonical/adapter.py'),")
    text = replace(text, 'S.M.N.required_arguments(inventory)',
        'S.M.N.required_arguments(S.STATIC.numerical_inventory(context))')
    output['repeat.py'] = (old, text)

    old = CURRENT/'repeat/sources.py'; text = old.read_text()
    text = replace(text, 'HERE = Path(__file__).resolve().parent',
        "PORT = Path(__file__).resolve().parent\nHERE = PORT.parent/'2026-10-08-w50-g1-current3/repeat'")
    text = replace(text, "R = source(FIT/'references/canonical.py', 'w50_repeat_canonical_sources')",
        "R = source(FIT/'references/canonical.py', 'w50_repeat_canonical_sources')\nSTATIC = source(PORT/'static.py', 'w51_static_repeat_authority')")
    start = text.index("    scenes, published = R.json_pin(config['scenes']), R.json_pin(config['publishedManifest'])")
    end = text.index("    return canonical_statistics(", start)
    text = text[:start]+'''    bound = STATIC.canonical_pair(config, rows)\n    scenes, scene, scale, native_pin, background_pin, runs = (bound[k] for k in\n        ('scenes','scene','scale','native','background','runs'))\n    shape = (scenes['canvas']['height']*scale,scenes['canvas']['width']*scale)\n    native, background = (R.decode_verified(pin,shape) for pin in (native_pin,background_pin))\n    repeats = [R.decode_verified(r['frame'],shape) for r in runs]\n    bg_kind = scenes['backgrounds'][scene['background']]['kind']\n    enriched = [dict(r,backgroundKind=bg_kind) for r in rows]\n    provenance = bound['provenance']\n'''+text[end:]
    text = replace(text, "native_batch = A.native_contract(repo,config['native'])", "native_batch = STATIC.native_batch(context, config['native'])")
    output['repeat_sources.py'] = (old, text)

    old = FIT/'live-execution/lifecycle.py'; text = old.read_text()
    text = replace(text, 'from pathlib import Path',
        "from pathlib import Path\nimport types\n\n_JOURNAL = Path(__file__).resolve().parent/'journal.py'\nJ = types.ModuleType('w51_store_journal'); J.__file__ = str(_JOURNAL)\nexec(compile(_JOURNAL.read_bytes(), str(_JOURNAL), 'exec'), J.__dict__)")
    start=text.index('def write_once(path,value):');end=text.index('\n\ndef native_payload',start)
    text=text[:start]+"def write_once(path,value):\n    return J.write_bytes(path,encode(value))\n"+text[end:]
    output['lifecycle.py'] = (old, text)
    for name, changes in DL5_WIRING.items():
        original, text = output[name]
        for before, after in changes: text = replace(text, before, after)
        output[name] = (original, text)
    return output



# DL5 adds only these new policy functions. Their declared AST fingerprints name the
# prospective implementation; the source root additionally binds every file byte.
# Existing functions remain compared against W50 plus the exact wiring deltas below.
DL5_NEW_FUNCTIONS = {
    'judge.py': {
        'landing_inputs': '9cb4df18eaca0eaf068dd573ae3e811df47a2784a288ce7032585ed511c0c581',
    },
    'judge_rules.py': {
        '_digest': '51c8c537b7d34a8306d38ac855ff9633e9e8a0978280e7c88c0e1154979d8ae2',
        'authenticate_policy': 'bd6730bee03902febef8b60375afb4f945065e311a6988a93e2f7c1bc04c29fc',
        '_apply_landing_policy': 'de37a3ff4708958791b093e9d6763ecbc8e29694e4a8bed3f18e23740e667029',
        'route_row': '8e95cdcb8d1e2624ba2001a61bd71ebea83c7245702175b8be208b1c75b2392d',
        '_finite': '88a1177134ab0438cb5162a5e0fcc946f92e8b465a3fb139c13e1f726ced4e66',
        'route_aggregates': '3e36de2395890476a9a98812fe7ee15b9c5f71ae17a6a2251852bc69abeaf01d',
    },
}
DL5_BASE_SHA256 = {
    'judge.py': '69b235198b4299eef490cb0a217f2a48e540349c4cf292a45b56da4123fef8b2',
    'judge_rules.py': '840302e6caaa75044206a2960b257f17c057b1a3ce93c6bf877c92747049398d',
}

DL5_WIRING = {
    'judge.py': [
        (
            'N = R.N\n',
            'N = R.N\n'
            "S = source(Path(__file__).resolve().parent/'static.py', 'w51_judge_static')\n",
        ),
        (
            'def route(rows, root):\n'
            "    return R.route_rows(rows, inventory_sha256=root['references']['sha256'],\n"
            "                        reported_keys=root['reportedKeys'], empty_support_keys=root['emptySupportKeys'])\n",
            'def route(rows, root, landing_policy):\n'
            "    return R.route_rows(rows, inventory_sha256=root['references']['sha256'],\n"
            "        reported_keys=root['reportedKeys'], empty_support_keys=root['emptySupportKeys'],\n"
            "        landing_policy=landing_policy, policy_sha256=root['landingPolicy']['sha256'])\n",
        ),
        (
            "            'schema', 'references', 'binding', 'ownerContracts', 'targets', 'ownerUnion'}:\n",
            "            'schema', 'references', 'binding', 'ownerContracts', 'targets', 'ownerUnion', 'landingPolicy'}:\n",
        ),
        (
            '    document, inventory = originals(context, live, root)\n',
            '    policy, complete_keys, full_gate = landing_inputs(context, live, root, config)\n'
            '    document, inventory = originals(context, live, root)\n',
        ),
        (
            '    routed = dict(zip(rows, route(list(rows.values()), root)))\n',
            '    routed = dict(zip(rows, route(list(rows.values()), root, policy)))\n',
        ),
        (
            "              'numericalAdmission': copy.deepcopy(admitted), 'joinIdentity': join, 'outsideJudge': list(OUTSIDE)}\n",
            "              'numericalAdmission': copy.deepcopy(admitted), 'joinIdentity': join, 'outsideJudge': list(OUTSIDE),\n"
            "              'landingPolicy': copy.deepcopy(root['landingPolicy'])}\n",
        ),
        (
            "        report['status'] = GATE_SUCCESS if not failed else 'NEITHER'\n",
            "        report['clauseC'] = R.route_aggregates(cells, landing_policy=policy,\n"
            "            policy_sha256=root['landingPolicy']['sha256'], complete_keys=complete_keys, full_union=full_gate)\n"
            "        if report['clauseC']['status'] not in ('WITHIN', 'PENDING_FULL_UNION'):\n"
            "            failed.append(report['clauseC'])\n"
            "        report['status'] = GATE_SUCCESS if not failed else 'NEITHER'\n",
        ),
        (
            "        gate_cells = {key(c): c for c in gate_report['cells']}\n",
            "        if gate_report.get('landingPolicy') != root['landingPolicy'] or \\\n"
            "                gate_report.get('clauseC', {}).get('status') != 'WITHIN':\n"
            "            raise ValueError('Exposure requires the complete gate DL5 aggregates under this policy')\n"
            "        report['clauseC'] = copy.deepcopy(gate_report['clauseC'])\n"
            "        gate_cells = {key(c): c for c in gate_report['cells']}\n",
        ),
        (
            "            'targets': [{'target': t['target'], 'scale': t['scale'], 'status': t['status']} for t in report['targets']],\n",
            "            'clauseC': {'status': report['clauseC']['status'], 'aggregates': [\n"
            "                {k: a[k] for k in ('id', 'kind', 'gate', 'status')}\n"
            "                for a in report['clauseC']['aggregates']]},\n"
            "            'targets': [{'target': t['target'], 'scale': t['scale'], 'status': t['status']} for t in report['targets']],\n",
        ),
    ],
    'judge_rules.py': [
        (
            'from pathlib import Path\n',
            'import json\n'
            'import math\n'
            'import statistics\n'
            'from pathlib import Path\n',
        ),
        (
            'def route_row(row, *, inventory_sha256, reported_keys=(), empty_support_keys=()):\n',
            'def _route_row(row, *, inventory_sha256, reported_keys=(), empty_support_keys=(), landing_policy=None):\n',
        ),
        (
            "    for check in result['checks']:\n",
            '    _apply_landing_policy(result, row, landing_policy)\n'
            "    for check in result['checks']:\n",
        ),
        (
            'def route_rows(rows, **policy):\n'
            '    keys = [_key(row) for row in rows]\n'
            '    if len(keys) != len(set(keys)):\n'
            "        raise ValueError('Duplicate original numeric row key')\n"
            '    return [route_row(row, **policy) for row in rows]\n',
            'def route_rows(rows, *, landing_policy=None, policy_sha256=None, **kwargs):\n'
            '    policy = None if landing_policy is None else authenticate_policy(landing_policy, policy_sha256)\n'
            '    keys = [_key(row) for row in rows]\n'
            '    if len(keys) != len(set(keys)):\n'
            "        raise ValueError('Duplicate original numeric row key')\n"
            '    return [_route_row(row, landing_policy=policy, **kwargs) for row in rows]\n',
        ),
    ],
}

def write():
    for name, (_, text) in expected().items():
        target = HERE/name; target.parent.mkdir(parents=True,exist_ok=True)
        if name in DL5_NEW_FUNCTIONS:
            raise ValueError('DL5 judge ports are maintained explicitly, not regenerated')
        target.write_text(text)

if __name__ == '__main__': write()
