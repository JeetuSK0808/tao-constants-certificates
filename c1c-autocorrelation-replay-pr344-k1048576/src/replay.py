"""Independent exact replay of teorth/optimizationproblems#344's current certificate
(C_1c >= 0.4103780000, K = 2^20). Reads ONLY the certificate's data (K, weights)
plus the stated fraction and claim, compared at the end. Rule (constants/1c.md):
C_1c >= K min_{0<=k<=K} A_k / S^2, A_k = sum_i w_i w_{i+k}, S = sum_i w_i
(the autocorrelation of an equal-step function is linear between multiples of 1/K)."""
import json, sys, os, subprocess, time, hashlib
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kronlags import all_lags
HERE = os.path.dirname(os.path.abspath(__file__))

def direct(w, K, threads=8):
    w0 = w[0]; tail = [0] + w[1:]
    inp = f"{K} {len(w)}\n" + " ".join(map(str, tail)) + "\n"
    out = subprocess.run([os.path.join(HERE, "lags2"), str(threads)], input=inp,
                         capture_output=True, text=True, check=True).stdout
    A = [int(x) for x in out.split()]
    A[0] += w0 * w0
    for k in range(1, K + 1):
        if k < len(w): A[k] += w0 * w[k]
    return A

def trunc(fr, d=20):
    q = fr.numerator * 10**d // fr.denominator
    s = str(q).rjust(d + 1, "0"); return s[:-d] + "." + s[-d:] + "..."

path = sys.argv[1]
raw = open(path, "rb").read()
print("certificate sha256", hashlib.sha256(raw).hexdigest())
d = json.loads(raw)
K, w = int(d["K"]), [int(x) for x in d["weights_int"]]
n = len(w)
assert all(x >= 0 for x in w)
S = sum(w)
nz = [i for i, x in enumerate(w) if x]
print(f"K = {K}, {n} weights, w_0 = {w[0]} (2^60 - 128: {w[0] == 2**60 - 128}), share of mass {float(Fraction(w[0], S)):.4f}, "
      f"zero for 1 <= i < {nz[1]}, other weights < 2^{max(w[1:]).bit_length()}")
t = time.time(); A1 = direct(w, K); t1 = time.time() - t
t = time.time(); A2, slot = all_lags(w, K); t2 = time.time() - t
assert A1 == A2, "the two implementations disagree"
print(f"lags2.c+spike ({t1:.0f}s) and kronlags ({t2:.0f}s, {slot}-bit slots) agree at all {K+1} lags")
m = min(A1); ks = [k for k, x in enumerate(A1) if x == m]
val = Fraction(K * m, S * S)
print(f"min at k = {ks}")
print(f"value = {val.numerator}/{val.denominator}")
print(f"      = {trunc(val)}")
print("equals the certificate's stated fraction:", val == Fraction(int(d["score_num"]), int(d["score_den"])))
claim = Fraction(d["claim"])
print(f"implies the claim {d['claim']}: {val >= claim};  would imply 0.4103780001: {val >= Fraction('0.4103780001')}")
flat = sum(1 for k in range(nz[1], K + 1) if Fraction(K * (A1[k] - m), S * S) <= Fraction(17, 10**14))
print(f"lags in [{nz[1]}, {K}] within 1.7e-13 of the minimum: {flat} of {K + 1 - nz[1]}")
low = min(A1[:nz[1]])
print(f"smallest lag below {nz[1]}: {float(Fraction(K * low, S * S)):.10f}")
for name, r in [("#344's morning certificate 0.4103774129 (printed)", "0.4103774129"),
                ("#354 (SeanSagait) 0.4103772 (printed)", "0.4103772"),
                ("#270 (vidigoat) 0.4103608339 (printed)", "0.4103608339"),
                ("page best 0.4103333 [Kos2026]", "0.4103333")]:
    print(f"  above {name} by {float(val - Fraction(r)):.4e}")
# red controls
w2 = w[:]; i = nz[len(nz) // 2]; w2[i] += 1
A3, _ = all_lags(w2, K); v3 = Fraction(K * min(A3), sum(w2) ** 2)
print(f"control 1: w[{i}] += 1 -> value changes: {v3 != val}")
w3 = w[:]; w3[0] = w3[0] * 101 // 100
A4, _ = all_lags(w3, K); v4 = Fraction(K * min(A4), sum(w3) ** 2)
print(f"control 2: spike w_0 raised 1% -> value {trunc(v4, 12)}, still implies the claim: {v4 >= claim}")
