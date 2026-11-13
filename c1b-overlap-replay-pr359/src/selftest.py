"""Compare shifts.c, kron1b.py and a naive sum on random cases."""
import random, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kron1b import all_shifts, naive
HERE = os.path.dirname(os.path.abspath(__file__))

def run_c(a, D):
    inp = f"{len(a)} {D}\n" + " ".join(map(str, a)) + "\n"
    out = subprocess.run([os.path.join(HERE, "shifts"), "4"], input=inp, capture_output=True, text=True, check=True).stdout
    return {int(k): int(v) for k, v in (l.split() for l in out.splitlines())}

rng = random.Random(359)
cases = 0
for t in range(60):
    n = rng.choice([1, 2, 3, 5, 8, 17, 40, 97])
    D = rng.choice([1, 7, 2**20, 2**48, 2**48 - 1, 2**56])
    if t % 5 == 0:
        a = [rng.choice([0, D]) for _ in range(n)]           # extreme values
    else:
        a = [rng.randint(0, D) for _ in range(n)]
    ref = naive(a, D)
    k1, _ = all_shifts(a, D)
    c = run_c(a, D)
    assert ref == k1 == c, (n, D)
    cases += 1
print(f"selftest: {cases} random cases, shifts.c == kron1b == naive at every shift")
