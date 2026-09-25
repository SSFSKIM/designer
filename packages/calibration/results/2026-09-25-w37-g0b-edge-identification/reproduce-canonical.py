"""Recompute G0's E1 and placement numbers without rewriting those records."""
import json
from common import HERE,G0,edge,oldcanonical
checks=[]
original_save=edge.save
def compare(path,value):
    assert value==json.loads(path.read_text()),path.name
    checks.append(dict(file=path.name,records=len(value),exact=True))
try:
    edge.save=compare
    oldcanonical.main()
finally:edge.save=original_save
edge.save(HERE/'g0-canonical-reproduction.json',checks)
