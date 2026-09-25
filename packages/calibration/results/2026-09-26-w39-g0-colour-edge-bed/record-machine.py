#!/usr/bin/env python3
"""Read the W39 sitting's machine and binary facts (c9a §5.184; charter clause 5).

Derived from W34 G0's record-machine.py, never edited in place. What changed: the
side bundle is W39's (`~/vitrea-w39/side`, identifier dev.vitrea.reference-apple.w39),
and the gate label names W39. The census excludes this process's own ancestors,
as W34's did, so the sitting that asks is not counted as a foreign capture
process. It observes once; the independent sixty-second idle is read-session's.
Missing commands, settings and bundles are recorded as missing, never defaulted.
"""
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

MAIN = Path('/Users/new/Developer/GitHub/designer')
SIDE = Path.home() / 'vitrea-w39/side/VitreaReference.app'
DEV = Path('/Applications/Xcode.app/Contents/Developer')
FOREIGN = r'Chromium|playwright|compare\.ts|capture-web|VitreaReference'


def read(*args):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    return dict(command=[str(a) for a in args], exitCode=result.returncode,
                stdout=result.stdout.strip(), stderr=result.stderr.strip())


def processes():
    output = read('ps', '-axo', 'pid=,ppid=,command=')
    rows = [line.strip().split(None, 2) for line in output['stdout'].splitlines()]
    rows = [r for r in rows if len(r) == 3]
    parents = {int(p): int(pp) for p, pp, _ in rows}
    ancestors = set()
    pid = os.getpid()
    while pid and pid not in ancestors:
        ancestors.add(pid)
        pid = parents.get(pid, 0)
    return [line for line in rows if int(line[0]) not in ancestors and re.search(FOREIGN, line[2])]


def bundle(app):
    binary = app / 'Contents/MacOS/VitreaReference'
    if not binary.is_file():
        return dict(path=str(app), present=False)
    return dict(path=str(app), present=True,
                binarySha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                binaryModifiedAt=datetime.datetime.fromtimestamp(
                    binary.stat().st_mtime, datetime.timezone.utc).isoformat(),
                identifier=read('/usr/libexec/PlistBuddy', '-c', 'Print :CFBundleIdentifier',
                                app / 'Contents/Info.plist'),
                signature=read('codesign', '-dvvv', app),
                designatedRequirement=read('codesign', '-d', '-r-', app),
                buildVersion=read(DEV / 'Toolchains/XcodeDefault.xctoolchain/usr/bin/vtool',
                                  '-show-build', binary))


def main():
    foreign = processes()
    settings = {key: read('defaults', 'read', domain, key) for domain, key in [
        ('com.apple.universalaccess', 'reduceTransparency'),
        ('com.apple.universalaccess', 'increaseContrast'),
        ('-g', 'NSGlassTintAmount'), ('com.apple.Accessibility', 'ButtonShapesEnabled')]}
    record = dict(schema=1, gate='W39 G0/G1; c9a §5.184, charter clause 5', phase=sys.argv[1],
        recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        os=read('sw_vers'), settings=settings, display=read('/opt/homebrew/bin/displayplacer', 'list'),
        displayColourContext=read('system_profiler', 'SPDisplaysDataType', '-json'),
        toolchain=dict(xcode=read(DEV / 'usr/bin/xcodebuild', '-version'),
            swift=read(DEV / 'Toolchains/XcodeDefault.xctoolchain/usr/bin/swiftc', '--version'),
            sdk=read('/usr/libexec/PlistBuddy', '-c', 'Print :Version',
                     DEV / 'Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/SDKSettings.plist')),
        python=read('python3.12', '-c', 'import PIL, numpy; print(PIL.__version__, numpy.__version__)'),
        granted=bundle(MAIN / 'apps/reference-apple/build/VitreaReference.app'),
        side=bundle(SIDE),
        foreignProcessCount=len(foreign), foreignProcesses=foreign,
        idleScope='Instantaneous process census, not an idle attestation; read-session is.')
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
