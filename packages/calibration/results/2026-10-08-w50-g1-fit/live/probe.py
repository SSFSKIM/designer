"""Standalone source-only LIVE transport probe; the parent composes it into its root probe.

No LIVE batch, exposure config, result, image, native export, browser or GPU is consulted.
CURRENT3's helper exercises paired transports and immutable native authority metadata using
synthetic arrays; no current execution/recovery, role report or archive index is opened.
"""
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
router = types.ModuleType('w50_live_transport_probe')
router.__file__ = str(HERE/'router.py')
exec(compile(Path(router.__file__).read_bytes(), router.__file__, 'exec', dont_inherit=True),
     router.__dict__)
if router.source_probe() != {'status': 'SOURCE_ONLY'}:
    raise ValueError('LIVE capture probe did not remain source-only')
