"""Independent exact replay of teorth/optimizationproblems#359 (C_1b <= 0.3808585498).
Reads ONLY the certificate's data (n, D, a, and the stated fraction to compare
against). Rule, from constants/1b.md: f = a_i/D on n equal cells of [-1,1],
g = 1 - f on [-1,1], both zero outside. For two step functions on the same grid,
x -> int f(t) g(x+t) dt is linear between multiples of 2/n, so its sup is
(2/n) max_k S_k / D^2 with S_k = sum_i a_i (D - a_{i+k})."""
import json, sys, os, subprocess, time, hashlib
from fractions import Fraction
from decimal import Decimal, getcontext
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kron1b import all_shifts
HERE = os.path.dirname(os.path.abspath(__file__))
getcontext().prec = 40

def run_c(n, D, a, threads=8):
    inp = f"{n} {D}\n" + " ".join(map(str, a)) + "\n"
    out = subprocess.run([os.path.join(HERE, "shifts"), str(threads)], input=inp,
                         capture_output=True, text=True, check=True).stdout
    return {int(k): int(v) for k, v in (l.split() for l in out.splitlines())}

def dec(fr, d=20):
    return str((Decimal(fr.numerator) / Decimal(fr.denominator)).quantize(Decimal(10) ** -d))

def value(S, n, D):
    M = max(S.values())
    return Fraction(2 * M, n * D * D), M

path = sys.argv[1]
raw = open(path, "rb").read()
print("certificate sha256", hashlib.sha256(raw).hexdigest())
d = json.loads(raw)
n, D, a = int(d["n"]), int(d["D"]), [int(x) for x in d["a"]]
assert len(a) == n, "length"
assert all(0 <= x <= D for x in a), "box 0 <= a_i <= D"
assert 2 * sum(a) == n * D, "mass: sum a_i = n D / 2 exactly"
print(f"n = {n}, D = {D} = 2^{D.bit_length()-1}, box and mass exact (sum a_i = nD/2)")

t = time.time(); Sc = run_c(n, D, a); tc = time.time() - t
t = time.time(); Sk, slot = all_shifts(a, D); tk = time.time() - t
assert Sc == Sk, "C and Kronecker disagree"
print(f"shifts.c ({tc:.1f}s) and kron1b ({tk:.1f}s, {slot}-bit slots) agree at all {len(Sc)} shifts")

val, M = value(Sc, n, D)
arg = sorted(k for k, s in Sc.items() if s == M)
second = max(s for s in Sc.values() if s != M)
print(f"max S_k = {M} at k = {arg}")
print(f"next largest shift lower by {dec(Fraction(2*(M-second), n*D*D), 25)} (in value)")
print(f"value = {val.numerator}/{val.denominator}")
print(f"      = {dec(val, 20)}")
stated = Fraction(int(d["score_num"]), int(d["score_den"]))
print("equals the certificate's stated fraction:", val == stated)
claim = Fraction(d["claim"])
print(f"implies the claim {d['claim']}: {val <= claim};  would imply 0.3808585497: {val <= Fraction('0.3808585497')}")
A2026_lo = Fraction("0.38085855031642856010")   # page's exact value for [A2026] (truncated, so a lower bound)
EA2026_lo = Fraction("0.38085857485785830914")
print(f"below [A2026] exact 0.38085855031642856010... by {dec(A2026_lo - val, 25)}")
print(f"below [EA2026] exact 0.38085857485785830914... by {dec(EA2026_lo - val, 25)}")

# red controls (C only)
i0 = max(range(n), key=lambda i: a[i] if a[i] < D else -1)
b = a[:]; b[i0] += 1
v1, _ = value(run_c(n, D, b), n, D)
print(f"control 1: a[{i0}] += 1 -> value changes: {v1 != val} ({dec(v1, 20)})")
j0 = next(i for i in range(n) if 0 < a[i] < D - 10**9)
k0 = next(i for i in range(n - 1, -1, -1) if a[i] > 10**9 and i != j0)
b = a[:]; delta = 10**9; b[j0] += delta; b[k0] -= delta   # mass-preserving move
v2, _ = value(run_c(n, D, b), n, D)
print(f"control 2: move {delta} units from cell {k0} to cell {j0} (mass kept) -> value {dec(v2, 20)}, still implies claim: {v2 <= claim}")
b = [min(D, x + x // 100) for x in a]
v3, _ = value(run_c(n, D, b), n, D)
print(f"control 3: every a_i raised 1% (mass broken, not checked here) -> value {dec(v3, 20)}, implies claim: {v3 <= claim}")
