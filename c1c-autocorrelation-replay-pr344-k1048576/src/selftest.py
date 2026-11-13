"""lags2.c (tail only, spike added separately) vs kronlags.py vs naive, on random cases
shaped like the certificate: a large spike at cell 0, a zero run, then a profile."""
import random, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kronlags import all_lags, naive
HERE = os.path.dirname(os.path.abspath(__file__))

def direct(w, K):
    """lags2.c on the weights with the spike zeroed, then the spike's terms added exactly."""
    w0 = w[0]; tail = [0] + w[1:]
    inp = f"{K} {len(w)}\n" + " ".join(map(str, tail)) + "\n"
    out = subprocess.run([os.path.join(HERE, "lags2"), "4"], input=inp, capture_output=True, text=True, check=True).stdout
    A = [int(x) for x in out.split()]
    A[0] += w0 * w0
    for k in range(1, K + 1):
        if k < len(w): A[k] += w0 * w[k]
    return A

rng = random.Random(344)
for t in range(60):
    n = rng.choice([2, 3, 5, 9, 30, 77, 120])
    K = n - 1
    z = rng.randint(0, n - 1)
    w = [rng.randint(0, 2**60)] + [0] * (z - 1 if z > 0 else 0)
    w += [rng.choice([0, rng.randint(0, 2**42)]) for _ in range(n - len(w))]
    w = w[:n]
    ref = naive(w, K); k1, _ = all_lags(w, K); c = direct(w, K)
    assert ref == k1 == c, t
print("selftest: 60 random spike+profile cases, lags2.c(+spike) == kronlags == naive at every lag")
