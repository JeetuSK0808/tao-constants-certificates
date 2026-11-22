"""Exact replay of a C_1c step-function certificate (teorth/optimizationproblems, constants/1c.md rule):
C_1c >= K * min_{0<=k<=K} A_k / S^2,  A_k = sum_i w_i w_{i+k},  S = sum_i w_i.
Reads only K and the integer weights; the stated fraction (from the page row) is compared at the end.
Two implementations that share no code: lags2.c (direct u128 sums) and kronlags.py (one big-integer
Kronecker product). Same code as our #344 replay, generalised to any certificate."""
import json, sys, os, subprocess, time, hashlib
from fractions import Fraction
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from kronlags import all_lags

def direct(w, K, threads=8):
    inp = f"{K} {len(w)}\n" + " ".join(map(str, w)) + "\n"
    out = subprocess.run([os.path.join(HERE, "lags2"), str(threads)], input=inp, capture_output=True, text=True, check=True).stdout
    return [int(x) for x in out.split()]

def trunc(fr, d=20):
    q = fr.numerator * 10**d // fr.denominator; s = str(q).rjust(d + 1, "0"); return s[:-d] + "." + s[-d:] + "..."

path, stated, claim = sys.argv[1], Fraction(sys.argv[2]), Fraction(sys.argv[3])
raw = open(path, "rb").read(); print("certificate sha256", hashlib.sha256(raw).hexdigest())
d = json.loads(raw); K, w = int(d["K"]), [int(x) for x in d["weights_int"]]
assert all(x >= 0 for x in w) and w[0] > 0
S = sum(w); print(f"K = {K}, {len(w)} weights, largest < 2^{max(w).bit_length()}, support [0, {len(w)}/{K})")
t = time.time(); A1 = direct(w, K); t1 = time.time() - t
t = time.time(); A2, slot = all_lags(w, K); t2 = time.time() - t
assert A1 == A2, "the two implementations disagree"
print(f"lags2.c ({t1:.1f}s) and kronlags ({t2:.1f}s, {slot}-bit slots) agree at all {K+1} lags")
m = min(A1); ks = [k for k, x in enumerate(A1) if x == m]; val = Fraction(K * m, S * S)
print(f"min at k = {ks}\nvalue = {val.numerator}/{val.denominator}\n      = {trunc(val)}")
print("equals the stated fraction:", val == stated)
print(f"implies the claim {float(claim)}: {val >= claim}")
if "score_num" in d: print("equals the certificate's own score fields:", val == Fraction(int(d["score_num"]), int(d["score_den"])))
w2 = w[:]; i = max(range(len(w)), key=lambda j: w[j]); w2[i] += 1
A3, _ = all_lags(w2, K); v3 = Fraction(K * min(A3), sum(w2) ** 2)
print(f"red control: w[{i}] += 1 -> value changes: {v3 != val}")
