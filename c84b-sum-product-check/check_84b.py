"""Check of the explicit constant in Althoefer's note on [BSSZ2026, Sec. 5] (C_84b), with mpmath interval arithmetic.

Inputs from the note: eps = (phi-1)/(phi+1), C2 = 857.57, regulator R_K <= 103^d, |GG| <= 5^(d-1)|G|,
|A| >= (B X Y)^d with B = eps/(103 sqrt C2), |AA| <= (515/Y)^d |A|^2,
|A+A| <= (M1 e^Y/(X Y^2) + M2/(X^2 Y^2))^d |A|^2, |A| <= exp(L d) with L > log(5Y+1) + log(2 eps X + 1).
Saving: c = -log(q)/L with q = max(515/Y, M1 e^Y/(X Y^2) + M2/(X^2 Y^2)).
"""
from mpmath import mp, iv, mpf, zeta, gamma, pi, sqrt, log, exp, findroot, diff
mp.dps = 40; iv.dps = 40

C2 = mpf('857.57')
f = lambda s: zeta(s) * gamma(s / 2) / (2 * pi ** (s / 2)) * C2 ** (s / 2)
s0 = findroot(lambda s: diff(f, s), 1.37)
print(f"regulator: min_s f(s) at s={mp.nstr(s0, 12)}, value {mp.nstr(f(s0), 12)}  (note: 1.371966384, 101.9560759)")
# the value at any fixed s > 1 gives a valid bound; 40-digit evaluation, the margin to 103 is ~1%
fs = f(s0)
print(f"  value at s0: {mp.nstr(fs, 20)} < 103: {fs < 103}")

phiI = (1 + iv.sqrt(5)) / 2; epsI = (phiI - 1) / (phiI + 1)
import sys
RREG = iv.mpf(sys.argv[1]) if len(sys.argv) > 1 else iv.mpf(103)   # regulator base: R_K <= RREG^d
M2I = RREG ** 2 * iv.mpf('857.57') / epsI ** 2; M1I = 4 * (1 + epsI) * M2I


def c_of(Y, x):
    """saving for X = exp(x) (x real; floor(X) changes nothing at this precision), L = log(5Y+1)+log(2 eps X+1)."""
    Y = iv.mpf(Y); X = iv.exp(iv.mpf(x))
    q1 = 5 * RREG / Y
    q2 = M1I * iv.exp(Y) / (X * Y ** 2) + M2I / (X ** 2 * Y ** 2)
    L = iv.log(5 * Y + 1) + iv.log(2 * epsI * X + 1)
    qb = max(q1.b, q2.b)
    return -iv.log(iv.mpf(qb)) / L, q1, q2, L


c, q1, q2, L = c_of(1415, 1423)
print(f"note's choice Y=1415, X=e^1423: 515/Y={mp.nstr(q1.b,10)}, additive={mp.nstr(q2.b,10)}, L={mp.nstr(L.b,10)}")
print(f"  certified saving c >= {mp.nstr(c.a, 10)}  (note states 0.0007 with L rounded up to 1432: {mp.nstr(-log(mpf('0.364'))/1432,10)})")

best = (0, None)
for Y in range(600, 6000, 10):
    # balance the two factors: x = Y + log(M1/(515 Y)) roughly, scan around it
    import math; x0 = Y + math.log(float(M1I.b) / (515 * Y))
    for dx in [k * 0.1 for k in range(-20, 21)]:
        cc = c_of(Y, x0 + dx)[0].a
        if cc > best[0]: best = (cc, (Y, x0 + dx))
print(f"best saving over Y in [600,6000), X=e^x: c = {mp.nstr(best[0], 10)} at Y={best[1][0]}, x={best[1][1]:.2f}")
print(f"  => exponent 2 - c = {mp.nstr(2 - best[0], 10)}; table row 1.999281 needs c >= 0.000719")
