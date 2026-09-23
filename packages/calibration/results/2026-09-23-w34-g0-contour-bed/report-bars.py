#!/usr/bin/env python3.12
"""G1 report: calibration/validation only, no holdout payload deserialisation."""
import argparse
import json
import archive
from wave import default_wave


def report(reader,protocol='normal'):
    cells=sorted({r['cell'] for r in reader.report_inventory()
                  if r['cell'].split('/',1)[1] in reader.allowed})
    return [archive.repeat_bar(reader,cell,protocol) for cell in cells]


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('archive_root')
    ap.add_argument('--protocol',choices=['normal','long'],default='normal');args=ap.parse_args()
    reader=default_wave().reader(args.archive_root)
    print(json.dumps(report(reader,args.protocol),indent=2))


if __name__=='__main__':main()
