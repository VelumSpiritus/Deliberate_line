"""Run the paper's supporting calculations against pinned inputs with networking disabled.

Run: python -X utf8 reproduce_support.py
Writes SUPPORTING_RESULTS.json only when every calculation succeeds.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
SCRIPTS = [
    'common_return_accounting.py', 'premium_accounting.py', 'predict.py', 'ensemble.py',
    'party_invariance.py', 'within_country.py',
    'veritocratic_rate.py', 'string_correlates.py', 'reach_umbrella.py',
    'labor_cost.py', 'war_funds.py', 'two_regimes.py', 'window_math.py',
    'took_the_gross.py', 'breadth_law.py', 'deflation.py', 'inequality_maturity.py',
]
WRAPPER = '''import runpy, socket, sys
def offline(*args, **kwargs):
    raise RuntimeError("Offline reproduction attempted a network connection")
socket.socket.connect = offline
socket.socket.connect_ex = offline
socket.create_connection = offline
runpy.run_path(sys.argv[1], run_name="__main__")
'''


def main():
    results = []
    for name in SCRIPTS:
        p = subprocess.run([sys.executable, '-X', 'utf8', '-c', WRAPPER, name],
                           cwd=HERE, capture_output=True, encoding='utf-8', timeout=180)
        print(f'{name}: exit {p.returncode}', flush=True)
        if p.returncode:
            print(p.stdout + p.stderr)
            raise SystemExit(p.returncode)
        results.append({'script': name, 'stdout': p.stdout, 'stderr': p.stderr})
    inputs = sorted((HERE/'data').rglob('*'))
    hashes = {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in inputs if p.is_file()}
    scripts = {name: hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in SCRIPTS}
    payload = {'schema': 'supporting-results-v1', 'network': 'disabled',
               'input_sha256': hashes, 'script_sha256': scripts, 'results': results}
    (HERE/'SUPPORTING_RESULTS.json').write_text(json.dumps(payload, indent=2,
                                                  ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')
    print('Wrote SUPPORTING_RESULTS.json', flush=True)


if __name__ == '__main__':
    main()
