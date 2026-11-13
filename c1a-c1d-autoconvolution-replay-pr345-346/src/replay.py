"""Independent exact replay of the step-function upper bounds of
teorth/optimizationproblems#346 (C_1a) and #345 (C_1d).
Reads ONLY the certificate's data (n, v_int) plus the stated fraction and claim,
which are compared at the end. Rule (constants/1a.md, 1d.md): f = v_i on n equal
cells of [-1/4,1/4], h = 1/(2n). f*f is piecewise linear with knots at multiples
of h, (f*f) at a knot is h * sum_{i+j=m} v_i v_j, and int f = h * sum v_i, so
  max_t |f*f| / (int f)^2 = 2n max_m |c_m| / S^2,  c = v*v, S = sum v_i."""
import json, sys, os, subprocess, time, hashlib
from fractions import Fraction
from decimal import Decimal, getcontext
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kronconv import autoconv
HERE = os.path.dirname(os.path.abspath(__file__))
getcontext().prec = 50

def run_c(v, threads=8):
    inp = f"{len(v)}\n" + " ".join(map(str, v)) + "\n"
    out = subprocess.run([os.path.join(HERE, "conv"), str(threads)], input=inp,
                         capture_output=True, text=True, check=True).stdout
    res = []
    for line in out.splitlines():
        m, aa, ab, bb = map(int, line.split())
        res.append((aa << 56) + (ab << 28) + bb)
    return res

def trunc(fr, d=20):
    q = abs(fr.numerator) * 10**d // fr.denominator
    s = str(q).rjust(d + 1, "0")
    return ("-" if fr < 0 else "") + s[:-d] + "." + s[-d:] + "..."

def ratio(c, n, S):
    M = max(abs(x) for x in c)
    return Fraction(2 * n * M, S * S), M

RECORDS = {
    "C_1a": [("[A2026] page best, exact", "1.50274348670958337974"),
             ("#270 (vidigoat, 10 Nov), exact", "116537598371962553887369519059399403896832/77549933019818026777245548252121251545225"),
             ("#346's 8 Nov certificate", "1.5027427375")],
    "C_1d": [("page best unstarred [CERT2026]", "1.4630715826075594"),
             ("[SCIEL2026] starred", "1.457854884921989"),
             ("#312 (Julsgaard)", "1.454727664528751"),
             ("#270 (vidigoat, 10 Nov), exact", "646233848324886328286774558720/444246710235775351931155445761"),
             ("#345's 9 Nov certificate", "1.454673347420953")],
}

path = sys.argv[1]
raw = open(path, "rb").read()
print("==", os.path.basename(path), "sha256", hashlib.sha256(raw).hexdigest())
d = json.loads(raw)
const, n, v = d["constant"], int(d["n"]), [int(x) for x in d["v_int"]]
assert len(v) == n
assert all(abs(x) <= 2**56 for x in v)
if const == "C_1a":
    assert min(v) >= 0, "C_1a needs f >= 0"
S = sum(v); assert S > 0
print(f"{const}: n = {n} cells on [-1/4,1/4], values in [{min(v)}, {max(v)}], S = {S}")

t = time.time(); cc = run_c(v); tc = time.time() - t
t = time.time(); ck, slot = autoconv(v); tk = time.time() - t
assert cc == ck, "C and Kronecker disagree"
print(f"conv.c ({tc:.0f}s) and kronconv ({tk:.0f}s, {slot}-bit slots) agree at all {len(cc)} knots")
val, M = ratio(cc, n, S)
arg = [m for m, x in enumerate(cc) if abs(x) == M]
second = max(abs(x) for x in cc if abs(x) != M)
print(f"max |c_m| at m = {arg} (sum index i+j = m); next largest knot lower by {float(Fraction(2*n*(M-second), S*S)):.4g} in value")
print(f"value = {val.numerator}/{val.denominator}")
print(f"      = {trunc(val, 20)}")
stated = Fraction(int(d["score_num"]), int(d["score_den"]))
print("equals the certificate's stated fraction:", val == stated)
claim = Fraction(d["claim"])
last = Fraction(d["claim"]) - Fraction(1, 10**(len(d["claim"].split(".")[1])))
print(f"implies the claim {d['claim']}: {val <= claim};  would imply {float(last):.10f}: {val <= last}")
for name, r in RECORDS[const]:
    rv = Fraction(r)
    print(f"  below {name} by {float(rv - val):.4e}")
# red controls
i0 = max(range(n), key=lambda i: abs(v[i]))
w = v[:]; w[i0] -= 1
v1, _ = ratio(run_c(w), n, sum(w))
print(f"control 1: v[{i0}] -= 1 -> value changes: {v1 != val} ({trunc(v1, 20)})")
w = v[:]; w[i0] = w[i0] - w[i0] // 100
v2, _ = ratio(run_c(w), n, sum(w))
print(f"control 2: largest |v| cut by 1% -> value {trunc(v2, 12)}, implies claim: {v2 <= claim}")
