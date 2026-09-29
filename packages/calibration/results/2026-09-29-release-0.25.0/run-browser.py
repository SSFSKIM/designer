"""One X6-attested browser command for the 0.25.0 chain, no retry.

    python3 run-browser.py <label> <command...>

The four X6 facts are read immediately before launch: Reduce Transparency and
Increase Contrast 0, `NSGlassTintAmount` 0.5 (Button Shapes 0 is read beside
them, as W36 G2 did), zero foreign capture processes, and at least 60 s of HID
idle. The census is W34 G0's `record-machine.processes()` unchanged — every
Chromium / playwright / compare.ts / capture-web / VitreaReference process that
is not an ancestor of this one.

Changed from W36 G2's runner on this release's instruction: a short idle or a
foreign capture process is WAITED OUT rather than refused, because the user may
be at the Mac and a step is neither failed nor skipped for it. Every poll is
kept in `x6-waits.txt` and the preflight row records how long it waited. A
setting that does not hold is refused at once and never changed. The waits are
capped only so that a chain cannot hang forever; reaching a cap refuses the
launch (exit 3) and the chain halts there.
"""
import datetime, importlib.util, json, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    'machine', HERE.parent / '2026-09-23-w34-g0-contour-bed/record-machine.py')
machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)

SETTINGS = [('com.apple.universalaccess', 'reduceTransparency', 0),
            ('com.apple.universalaccess', 'increaseContrast', 0),
            ('-g', 'NSGlassTintAmount', .5),
            ('com.apple.Accessibility', 'ButtonShapesEnabled', 0)]
IDLE_FLOOR = 60.0
POLL = 5.0
IDLE_CAP = 6 * 3600.0
FOREIGN_CAP = 3600.0


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def append(name, row):
    with (HERE / name).open('a') as f:
        f.write(json.dumps(row, sort_keys=True) + '\n')
        f.flush()
        os.fsync(f.fileno())


def settings():
    values = {}
    for domain, key, _ in SETTINGS:
        values[key] = subprocess.check_output(['defaults', 'read', domain, key], text=True).strip()
    return values


def idle():
    raw = subprocess.check_output(['ioreg', '-c', 'IOHIDSystem'], text=True)
    return int(re.search(r'"HIDIdleTime"\s*=\s*(\d+)', raw)[1]) / 1e9


def preflight(label):
    """Wait until all four facts hold; return the admitted reading, or exit 3."""
    started = time.monotonic()
    started_at = now()
    polls = 0
    idle_wait = foreign_wait = 0.0
    while True:
        polls += 1
        values = settings()
        for domain, key, expected in SETTINGS:
            if float(values[key]) != expected:
                append('browser-runs.txt', dict(at=now(), label=label, settings=values,
                    admitted=False, refusal='X6 setting mismatch: ' + key))
                print(label, 'X6 refused: setting', key, values[key], file=sys.stderr)
                raise SystemExit(3)
        seconds = idle()
        foreign = machine.processes()
        if seconds >= IDLE_FLOOR and not foreign:
            break
        elapsed = time.monotonic() - started
        append('x6-waits.txt', dict(at=now(), label=label, poll=polls, idleSeconds=seconds,
            foreignProcessCount=len(foreign), foreignProcesses=foreign, elapsedSeconds=elapsed))
        if foreign:
            foreign_wait += POLL
        else:
            idle_wait += POLL
        if foreign_wait > FOREIGN_CAP or elapsed > IDLE_CAP:
            append('browser-runs.txt', dict(at=now(), label=label, settings=values,
                idleSeconds=seconds, foreignProcessCount=len(foreign), foreignProcesses=foreign,
                admitted=False, waitedSeconds=elapsed, refusal='X6 wait cap reached'))
            print(label, 'X6 refused: wait cap reached', file=sys.stderr)
            raise SystemExit(3)
        time.sleep(POLL)
    waited = time.monotonic() - started
    row = dict(at=now(), label=label, settings=values, idleSeconds=seconds,
        foreignProcessCount=0, foreignProcesses=[], admitted=True,
        waitStartedAt=started_at, waitedSeconds=round(waited, 3), polls=polls,
        rule='X6: RT 0, IC 0, NSGlassTintAmount 0.5, zero foreign capture processes, '
             'HID idle >= 60 s; waited out, never refused for idle')
    append('browser-runs.txt', row)
    return row


def main():
    label = sys.argv[1]
    command = sys.argv[2:]
    out = HERE / (label + '.txt')
    if out.exists():
        raise RuntimeError('Already attempted; no implicit retry: ' + label)
    preflight(label)
    with out.open('x') as f:
        result = subprocess.run(command, stdout=f, stderr=subprocess.STDOUT, env=os.environ)
    append('browser-runs.txt', dict(label=label, completed=now(), exitCode=result.returncode,
        command=command))
    print(label, 'exit', result.returncode, 'log', out)
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
