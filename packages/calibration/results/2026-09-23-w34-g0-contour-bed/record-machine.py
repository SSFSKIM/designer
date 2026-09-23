#!/usr/bin/env python3
"""Read the native gate's machine and binary facts (§5.174, clauses 2–3).

This widens W33 G2's ancestor-excluding process census. It observes once rather
than asserting the browser's sixty-second interval: G0 launches no browser.
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
DEV = Path('/Applications/Xcode.app/Contents/Developer')


def read(*args):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    return dict(command=[str(a) for a in args], exitCode=result.returncode,
                stdout=result.stdout.strip(), stderr=result.stderr.strip())


def processes():
    output = read('ps', '-axo', 'pid=,ppid=,command=')
    rows = [line.strip().split(None, 2) for line in output['stdout'].splitlines()]
    parents = {int(p): int(pp) for p, pp, _ in rows}
    ancestors = set()
    pid = os.getpid()
    while pid and pid not in ancestors:
        ancestors.add(pid)
        pid = parents.get(pid, 0)
    return [line for line in rows if int(line[0]) not in ancestors and
            re.search(r'Chromium|playwright|compare\.ts|capture-web|VitreaReference', line[2])]


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
    record = dict(schema=1, gate='W34 G0; §5.174 clauses 2–3', phase=sys.argv[1],
        recordedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        os=read('sw_vers'), settings=settings, display=read('/opt/homebrew/bin/displayplacer', 'list'),
        displayColourContext=read('system_profiler', 'SPDisplaysDataType', '-json'),
        toolchain=dict(xcode=read(DEV / 'usr/bin/xcodebuild', '-version'),
            swift=read(DEV / 'Toolchains/XcodeDefault.xctoolchain/usr/bin/swiftc', '--version'),
            sdk=read('/usr/libexec/PlistBuddy', '-c', 'Print :Version',
                     DEV / 'Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/SDKSettings.plist')),
        python=read('python3.12', '-c', 'import PIL, numpy; print(PIL.__version__, numpy.__version__)'),
        granted=bundle(MAIN / 'apps/reference-apple/build/VitreaReference.app'),
        side=bundle(Path.home() / 'vitrea-w34/side/VitreaReference.app'),
        foreignProcessCount=len(foreign), foreignProcesses=foreign,
        idleScope='Instantaneous process census, not a browser idle attestation.')
    print(json.dumps(record, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
