#!/usr/bin/env python3.12
"""Read the W43 sitting's machine and binary facts (charter clause 4; X6 as carried).

Derived from W42 G0's record-machine.py (itself W39's and W34's), never edited in place. The side
bundle is still W39's (`~/vitrea-w39/side`, dev.vitrea.reference-apple.w39), used with no rebuild
(X4'). Missing commands, settings and bundles are recorded as missing, never defaulted. What W43
changes is the foreign-process census, after W42 G1's stops 4 and 5 (c9a §5.195 §2; the two
census entries in tech-debt-tracker.md):

- **By executable, not by command line.** W42 matched a regex against every process's whole
  command line, so a `pgrep` pattern, a shell holding one, and a test stub whose arguments name the
  harness's bundle all counted. A process now counts by what it IS: its executable image
  (libproc's `proc_pidpath`, the resolved binary the kernel runs; ps's argv[0] only where the image
  is unreadable). A Chromium, Google Chrome (any helper, Chrome for Testing, the crashpad handler
  inside a browser bundle), headless shell or `VitreaReference` executable counts wherever it
  lives. Playwright and the calibration's capture scripts have no executable of their own: they
  are node scripts, so for a node-family interpreter only, its ENTRY script is matched, by path
  component or exact file name (`compare.ts`, `capture-web`, a `playwright*` package or CLI),
  never by substring. The entry script is the first non-option argument of the kernel's exact
  argv, the values of options that take one skipped (`entry_point`); every later argument is the
  program's data (the review's P2: `node benign.js …/playwright-core/cli.js` is not Playwright).
- **The launching chain is excluded.** The orchestrator detaches with setsid, so the shell that
  launched it is not an ancestor of anything that reads the census (stop 4). At launch it records
  that chain (`launcher-chain`: pid and start time of the launching process and its ancestors) and
  passes the file in `VITREA_LAUNCHER_CHAIN`; a row is excluded only if both its pid and its start
  time match, so a reused pid is still counted.

`universal-control` is the pre-sitting check the fourth W42 G1 tracker entry asked for. It reports
what this machine lets a process read, and names what it cannot (stops 1 and 2: input arrived
over Universal Control once with the feature reported off).
"""
import ctypes
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
# What counts, by executable file name (the image's basename) ...
FOREIGN_EXECUTABLES = re.compile(r'^(Chromium|Google Chrome)\b|Chrome Helper|headless[-_ ]shell|^VitreaReference$')
# ... or by a bundle anywhere on the image's path (a browser's helpers and its crashpad handler).
FOREIGN_BUNDLES = re.compile(r'^(Chromium|Google Chrome[^/]*)\.app$')
# The interpreters whose script arguments are read, and what a script argument counts by.
INTERPRETERS = re.compile(r'^(node|nodejs|tsx|bun|deno)(\d+(\.\d+)*)?$')
SCRIPT_NAMES = {'compare.ts', 'capture-web', 'capture-web.ts', 'capture-web.js', 'capture-web.mjs'}
SCRIPT_PACKAGES = re.compile(r'^(@playwright|playwright(-core|-cli|-mcp)?|ms-playwright)$')
SCRIPT_CLI = re.compile(r'^playwright(-core|-cli|-mcp)?(\.(js|mjs|cjs))?$')
LAUNCHER_CHAIN_ENV = 'VITREA_LAUNCHER_CHAIN'
PROC_PIDPATHINFO_MAXSIZE = 4096


def read(*args):
    result = subprocess.run([str(a) for a in args], capture_output=True, text=True)
    return dict(command=[str(a) for a in args], exitCode=result.returncode,
                stdout=result.stdout.strip(), stderr=result.stderr.strip())


# --------------------------------------------------------------------------- census

_LIBPROC = None


def image_path(pid):
    """The executable image the kernel runs for `pid` (libproc), or None if unreadable."""
    global _LIBPROC
    try:
        if _LIBPROC is None:
            _LIBPROC = ctypes.CDLL('/usr/lib/libproc.dylib', use_errno=True)
        buf = ctypes.create_string_buffer(PROC_PIDPATHINFO_MAXSIZE)
        n = _LIBPROC.proc_pidpath(int(pid), buf, PROC_PIDPATHINFO_MAXSIZE)
        return buf.value.decode(errors='replace') if n > 0 else None
    except OSError:
        return None


def process_argv(pid):
    """The process's exact argv (sysctl KERN_PROCARGS2: argc, the exec path, then argv NUL-separated),
    or None where the kernel will not show it (another user's process)."""
    try:
        libc = ctypes.CDLL('/usr/lib/libc.dylib', use_errno=True)
        mib = (ctypes.c_int * 3)(1, 49, int(pid))           # CTL_KERN, KERN_PROCARGS2
        size = ctypes.c_size_t(0)
        if libc.sysctl(mib, 3, None, ctypes.byref(size), None, 0) != 0 or size.value < 4:
            return None
        buf = ctypes.create_string_buffer(size.value)
        if libc.sysctl(mib, 3, buf, ctypes.byref(size), None, 0) != 0:
            return None
        raw = buf.raw[:size.value]
        argc = int.from_bytes(raw[:4], 'little')
        rest = raw[4:]
        rest = rest[rest.index(b'\0'):].lstrip(b'\0')     # past the exec path and its padding
        argv = [a.decode(errors='replace') for a in rest.split(b'\0')[:argc]]
        return argv if len(argv) == argc else None
    except (OSError, ValueError):
        return None


def process_table():
    """Every process: pid, ppid, start (ps lstart, C locale), executable image and argv.

    For a node-family interpreter the argv is the kernel's own (`process_argv`), because its entry
    script is read from it and a path may hold a space; elsewhere ps's `args` split on whitespace
    is kept for the record only, since nothing is matched against it.
    """
    out = subprocess.run(['ps', '-axww', '-o', 'pid=,ppid=,lstart=,args='], capture_output=True, text=True,
                         env={**os.environ, 'LC_ALL': 'C'}).stdout
    rows = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 8 or not parts[0].isdigit() or not parts[1].isdigit():
            continue
        pid, ppid, start, argv = int(parts[0]), int(parts[1]), ' '.join(parts[2:7]), parts[7:]
        exe = image_path(pid) or argv[0]
        if INTERPRETERS.match(Path(exe).name):
            argv = process_argv(pid) or argv
        rows.append(dict(pid=pid, ppid=ppid, start=start, executable=exe, argv=argv))
    return rows


# Node's options that take their value as the NEXT argument (the `--opt=value` form is one token),
# and the ones whose value is the program itself, so no file is the entry point.
NODE_VALUE_OPTIONS = {'-r', '--require', '--import', '--loader', '--experimental-loader', '-C', '--conditions',
                      '--input-type', '--env-file', '--env-file-if-exists', '--title', '--inspect-port',
                      '--debug-port', '--openssl-config', '--icu-data-dir', '--redirect-warnings', '--diagnostic-dir',
                      '--report-dir', '--report-directory', '--report-filename', '--report-signal',
                      '--secure-heap', '--secure-heap-min', '--disable-warning', '--watch-path', '--test-reporter',
                      '--test-reporter-destination', '--test-name-pattern', '--test-skip-pattern',
                      '--experimental-config-file', '--run', '--stack-trace-limit', '--max-http-header-size'}
NODE_INLINE_OPTIONS = {'-e', '--eval', '-p', '--print'}
RUNNER_SUBCOMMANDS = {'bun': {'run', 'x', 'test'}, 'deno': {'run', 'test', 'task'}}


def entry_point(argv):
    """The interpreter's entry script: its first non-option argument, the values of options that
    take one skipped (`--require r.js`, `--import x.mjs`, ...), the argument after `--` taken as
    the script. None for an inline program (`-e`, `-p`) or no script at all. Every later argument
    is the program's DATA, never matched (the review's P2)."""
    if not argv:
        return None
    args = list(argv[1:])
    family = re.match(r'^[a-z]+', Path(argv[0]).name)
    if family and args and args[0] in RUNNER_SUBCOMMANDS.get(family[0], ()):
        args = args[1:]
    i = 0
    while i < len(args):
        a = args[i]
        if a == '--':
            return args[i + 1] if i + 1 < len(args) else None
        if a in NODE_INLINE_OPTIONS:
            return None
        if a.startswith('-') and a != '-':
            i += 2 if a in NODE_VALUE_OPTIONS else 1
            continue
        return a
    return None


def foreign_reason(row):
    """Why this process is a foreign capture process, or None. Executables first; for a node-family
    interpreter, its entry script and nothing after it."""
    exe = row['executable'] or ''
    name = Path(exe).name
    if FOREIGN_EXECUTABLES.search(name):
        return f'executable {name}'
    bundle = next((c for c in Path(exe).parts if FOREIGN_BUNDLES.match(c)), None)
    if bundle:
        return f'inside {bundle}'
    if any(SCRIPT_PACKAGES.match(c) for c in Path(exe).parts):
        return f'executable under {exe}'
    if INTERPRETERS.match(name):
        script = entry_point([exe, *row['argv'][1:]])
        if script is None:
            return None
        path = Path(script)
        if path.name in SCRIPT_NAMES or SCRIPT_CLI.match(path.name):
            return f'{name} script {path.name}'
        package = next((c for c in path.parts[:-1] if SCRIPT_PACKAGES.match(c)), None)
        if package:
            return f'{name} script in {package}'
    return None


def ancestors(rows, pid):
    parents = {r['pid']: r['ppid'] for r in rows}
    chain = set()
    while pid and pid not in chain:
        chain.add(pid)
        pid = parents.get(pid, 0)
    return chain


def launcher_chain_entries(path):
    """The (pid, start) pairs the orchestrator recorded at launch, or [] when none was recorded."""
    if not path:
        return []
    record = json.loads(Path(path).read_text())
    return [(int(e['pid']), e['start']) for e in record['chain']]


def census(rows=None, me=None, chain_file=None):
    """(foreign rows, excluded launcher-chain rows). Own ancestors are never counted, as W42's; a
    launcher-chain row is excluded only where both pid and start time match the record."""
    rows = process_table() if rows is None else rows
    mine = ancestors(rows, os.getpid() if me is None else me)
    chain = set(launcher_chain_entries(chain_file if chain_file is not None else os.environ.get(LAUNCHER_CHAIN_ENV)))
    foreign, excluded = [], []
    for r in rows:
        if r['pid'] in mine:
            continue
        why = foreign_reason(r)
        if why is None:
            continue
        entry = dict(pid=r['pid'], ppid=r['ppid'], start=r['start'], executable=r['executable'],
                     args=' '.join(r['argv'])[:400], why=why)
        (excluded if (r['pid'], r['start']) in chain else foreign).append(entry)
    return foreign, excluded


def native_processes(rows=None, binary=None):
    """Every running harness: an executable named VitreaReference (or exactly `binary`), by image."""
    rows = process_table() if rows is None else rows
    want = None if binary is None else str(Path(binary).resolve())
    return [dict(pid=r['pid'], start=r['start'], executable=r['executable']) for r in rows
            if Path(r['executable'] or '').name == 'VitreaReference'
            or (want is not None and r['executable'] == want)]


def launcher_chain(pid=None, rows=None):
    """The chain from `pid` (default: this process's parent, the launching shell) to launchd's child."""
    rows = process_table() if rows is None else rows
    by_pid = {r['pid']: r for r in rows}
    pid = os.getppid() if pid is None else pid
    chain, seen = [], set()
    while pid > 1 and pid in by_pid and pid not in seen:
        seen.add(pid)
        r = by_pid[pid]
        chain.append(dict(pid=r['pid'], ppid=r['ppid'], start=r['start'], executable=r['executable'],
                          args=' '.join(r['argv'])[:400]))
        pid = r['ppid']
    return dict(schema='w43-launcher-chain-1', recordedAt=now(), chain=chain)


# ---------------------------------------------------------------- universal control

def universal_control(rows=None, read=read):
    """What can be read about Universal Control before a sitting, and what cannot.

    Read: the `UniversalControl` agent's process; the `Disable` key in its currentHost domain;
    Bluetooth's controller state; the awdl0 peer-to-peer interface; Wi-Fi power; Handoff's two
    currentHost flags. The input path is REACHABLE when the agent runs and Bluetooth and awdl0
    are up: those carry the discovery and the input stream. None of these says whether a peer
    device is near and linked, or whether the agent forwards input with the feature off (W42 G1
    stop 2 saw input arrive with it reported off); the watchdog during every launch is what sees
    input that does arrive.
    """
    rows = process_table() if rows is None else rows
    agent = [dict(pid=r['pid'], start=r['start'], executable=r['executable']) for r in rows
             if Path(r['executable'] or '').name == 'UniversalControl']
    disable = read('defaults', '-currentHost', 'read', 'com.apple.universalcontrol', 'Disable')
    bluetooth = read('system_profiler', 'SPBluetoothDataType', '-json')
    try:
        props = json.loads(bluetooth['stdout'])['SPBluetoothDataType'][0].get('controller_properties', {})
        bt_state = props.get('controller_state')
    except (ValueError, KeyError, IndexError, TypeError):
        bt_state = None
    awdl = read('ifconfig', 'awdl0')
    flags = re.search(r'flags=\w+<([^>]*)>', awdl['stdout'])
    awdl_flags = flags[1].split(',') if flags else None
    ports = read('networksetup', '-listallhardwareports')
    wifi_device = re.search(r'Hardware Port: Wi-Fi\nDevice: (\S+)', ports['stdout'])
    wifi = read('networksetup', '-getairportpower', wifi_device[1]) if wifi_device else None
    handoff = {k: read('defaults', '-currentHost', 'read', 'com.apple.coreservices.useractivityd', k)
               for k in ('ActivityAdvertisingAllowed', 'ActivityReceivingAllowed')}
    setting = disable['stdout'] if disable['exitCode'] == 0 else None
    bt_on = None if bt_state is None else bt_state == 'attrib_on'
    awdl_up = None if awdl_flags is None else ('UP' in awdl_flags and 'RUNNING' in awdl_flags)
    wifi_on = None if wifi is None or wifi['exitCode'] != 0 else wifi['stdout'].rstrip().endswith('On')
    reachable = bool(agent) and bt_on is True and awdl_up is True
    return dict(
        schema='w43-universal-control-1', recordedAt=now(),
        agentActive=bool(agent), agent=agent,
        disableSetting=setting, disabledBySetting=setting == '1',
        bluetoothControllerState=bt_state, awdlFlags=awdl_flags, wifiPower=None if wifi is None else wifi['stdout'],
        handoff={k: (v['stdout'] if v['exitCode'] == 0 else None) for k, v in handoff.items()},
        inputPathReachable=reachable,
        verdict=('the agent runs and its input path (Bluetooth, awdl0) is up: input from a linked device can reach '
                 'this Mac' if reachable else 'the agent or its input path is down: input over Universal Control '
                 'cannot arrive'),
        cannotDetect=['whether a peer device is near and linked right now',
                      'whether the agent forwards input while the setting reads off (W42 G1 stop 2)',
                      'whether the Disable key is where macOS 27 keeps the toggle: an absent key is not a reading of '
                      'the toggle, and confirming it needs System Settings, which no check here may touch'],
        reads=dict(disable=disable, awdl=awdl, wifi=wifi, handoff=handoff,
                   bluetoothExit=bluetooth['exitCode']),
        wifiOn=wifi_on)


# ------------------------------------------------------------------ the machine read

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


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


def machine(phase):
    foreign, excluded = census()
    settings = {key: read('defaults', 'read', domain, key) for domain, key in [
        ('com.apple.universalaccess', 'reduceTransparency'),
        ('com.apple.universalaccess', 'increaseContrast'),
        ('-g', 'NSGlassTintAmount'), ('com.apple.Accessibility', 'ButtonShapesEnabled')]}
    return dict(schema=1, gate='W43; charter clause 4, X6, X42', phase=phase, recordedAt=now(),
        os=read('sw_vers'), settings=settings, display=read('/opt/homebrew/bin/displayplacer', 'list'),
        displayColourContext=read('system_profiler', 'SPDisplaysDataType', '-json'),
        toolchain=dict(xcode=read(DEV / 'usr/bin/xcodebuild', '-version'),
            swift=read(DEV / 'Toolchains/XcodeDefault.xctoolchain/usr/bin/swiftc', '--version'),
            sdk=read('/usr/libexec/PlistBuddy', '-c', 'Print :Version',
                     DEV / 'Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk/SDKSettings.plist')),
        python=read('python3.12', '-c', 'import PIL, numpy; print(PIL.__version__, numpy.__version__)'),
        granted=bundle(MAIN / 'apps/reference-apple/build/VitreaReference.app'),
        side=bundle(SIDE),
        foreignProcessCount=len(foreign), foreignProcesses=foreign, excludedLauncherChain=excluded,
        censusRule='by executable image; node-family script arguments by path component or file name; own '
                   'ancestors and the recorded launcher chain (pid and start time) excluded',
        idleScope='Instantaneous process census, not an idle attestation; read-session is.')


def main():
    if len(sys.argv) != 2:
        raise SystemExit('usage: record-machine.py <phase> | launcher-chain | universal-control | census')
    what = sys.argv[1]
    if what == 'launcher-chain':
        value = launcher_chain()
    elif what == 'universal-control':
        value = universal_control()
    elif what == 'census':
        foreign, excluded = census()
        value = dict(foreignProcessCount=len(foreign), foreignProcesses=foreign, excludedLauncherChain=excluded)
    else:
        value = machine(what)
    print(json.dumps(value, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
