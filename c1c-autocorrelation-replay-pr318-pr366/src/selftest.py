"""lags2.c vs kronlags.py vs naive, on random cases shaped like the two certificates:
n = K + extra integer weights (extra up to 64), with weights up to 2^50 and some zero cells."""
import random, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kronlags import all_lags, naive
HERE = os.path.dirname(os.path.abspath(__file__))

def direct(w, K):
    inp = f"{K} {len(w)}\n" + " ".join(map(str, w)) + "\n"
    out = subprocess.run([os.path.join(HERE, "lags2"), "4"], input=inp, capture_output=True, text=True, check=True).stdout
    return [int(x) for x in out.split()]

rng = random.Random(318366)
for t in range(80):
    K = rng.choice([1, 2, 5, 16, 63, 96, 200])
    n = K + rng.randint(1, 65)
    w = [rng.randint(1, 2**50)] + [rng.choice([0, rng.randint(0, 2**rng.choice([8, 40, 50]))]) for _ in range(n - 1)]
    ref = naive(w, K); k1, _ = all_lags(w, K); c = direct(w, K)
    assert ref == k1 == c, t
print("selftest: 80 random cases, lags2.c == kronlags == naive at every lag k = 0..K")
