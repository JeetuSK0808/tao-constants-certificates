"""Compare conv.c, kronconv.py and a naive sum on random signed and unsigned cases."""
import random, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kronconv import autoconv, naive
HERE = os.path.dirname(os.path.abspath(__file__))

def run_c(v):
    inp = f"{len(v)}\n" + " ".join(map(str, v)) + "\n"
    out = subprocess.run([os.path.join(HERE, "conv"), "4"], input=inp, capture_output=True, text=True, check=True).stdout
    res = []
    for line in out.splitlines():
        m, aa, ab, bb = map(int, line.split())
        assert m == len(res)
        res.append((aa << 56) + (ab << 28) + bb)
    return res

rng = random.Random(345346)
L = 2**56
for t in range(80):
    n = rng.choice([1, 2, 3, 4, 7, 16, 33, 64, 101])
    kind = t % 4
    if kind == 0:   v = [rng.randint(0, L) for _ in range(n)]
    elif kind == 1: v = [rng.randint(-L, L) for _ in range(n)]
    elif kind == 2: v = [rng.choice([-L, L, 0, -1, 1, L - 1, -L + 1]) for _ in range(n)]
    else:           v = [rng.randint(-1000, 1000) for _ in range(n)]
    ref = naive(v)
    k, _ = autoconv(v)
    c = run_c(v)
    assert ref == k == c, (t, n)
print("selftest: 80 random cases (non-negative, signed, extreme +-2^56), conv.c == kronconv == naive at every knot")
