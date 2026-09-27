"""W41 X6 fresh four-fact gate; uses W39's ancestor-excluding process census."""
import datetime
import importlib.util
import json
from pathlib import Path
import re
import sys
import time

HERE = Path(__file__).resolve().parent
MACHINE = HERE.parents[1] / '2026-09-26-w39-g0-colour-edge-bed/record-machine.py'
spec = importlib.util.spec_from_file_location('w39_machine', MACHINE)
machine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(machine)


def verdict(record):
    settings = record['settings']
    facts = {key: settings[key]['exitCode'] == 0 and settings[key]['stdout'] == value
             for key, value in [('reduceTransparency', '0'), ('increaseContrast', '0'),
                                ('NSGlassTintAmount', '0.5')]}
    idle = record['idle']
    match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', idle['stdout'])
    seconds = int(match[1]) / 1e9 if match and idle['exitCode'] == 0 else None
    facts['foreignProcessCountZero'] = len(record['foreignProcesses']) == 0
    facts['idleAtLeast60Seconds'] = seconds is not None and seconds >= 60
    return {'passes': all(facts.values()), 'facts': facts, 'idleSeconds': seconds,
            'refusals': [key for key, passes in facts.items() if not passes]}


def observe():
    settings = {key: machine.read('defaults', 'read', domain, key) for domain, key in [
        ('com.apple.universalaccess', 'reduceTransparency'),
        ('com.apple.universalaccess', 'increaseContrast'), ('-g', 'NSGlassTintAmount')]}
    record = {'recordedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'settings': settings, 'foreignProcesses': machine.processes(),
              'idle': machine.read('ioreg', '-c', 'IOHIDSystem', '-d', '4')}
    record['foreignProcessCount'] = len(record['foreignProcesses'])
    record['verdict'] = verdict(record)
    return record


def main():
    # This explicitly requested three-hour X6 observation is not an agent-completion poll.
    # Passing ends this observer; a launcher must obtain its own fresh pre-process check.
    output = Path(sys.argv[1])
    started = time.monotonic()
    deadline = started + 3 * 60 * 60
    count = 0
    with output.open('x') as stream:
        while True:
            record = observe()
            stream.write(json.dumps(record, sort_keys=True) + '\n')
            stream.flush()
            count += 1
            print(record['recordedAt'], 'PASS' if record['verdict']['passes'] else 'REFUSED',
                  record['foreignProcessCount'], record['verdict']['idleSeconds'], flush=True)
            if record['verdict']['passes']:
                outcome = 'ready-needs-fresh-prelaunch-check'
                break
            if time.monotonic() >= deadline:
                outcome = 'bounded-wait-expired'
                break
            time.sleep(min(30, max(0, deadline - time.monotonic())))
    summary = {'outcome': outcome, 'observations': count,
               'elapsedSeconds': time.monotonic() - started,
               'endedAt': datetime.datetime.now(datetime.timezone.utc).isoformat()}
    with output.with_suffix('.summary.json').open('x') as stream:
        json.dump(summary, stream, indent=2)
        stream.write('\n')
    print(json.dumps(summary), flush=True)


if __name__ == '__main__': main()
