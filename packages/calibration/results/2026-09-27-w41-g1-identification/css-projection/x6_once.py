"""One fresh observation only. No browser launch or ownership grant."""
import importlib.util
import json
from pathlib import Path
import sys

path=Path(__file__).resolve().parent.parent/'x6/observe.py'
spec=importlib.util.spec_from_file_location('css_x6',path)
x6=importlib.util.module_from_spec(spec);spec.loader.exec_module(x6)
record=x6.observe()
with Path(sys.argv[1]).open('x') as stream:
    json.dump(record,stream,indent=2,sort_keys=True);stream.write('\n')
print(json.dumps(record['verdict'],sort_keys=True))
raise SystemExit(0 if record['verdict']['passes'] else 1)
