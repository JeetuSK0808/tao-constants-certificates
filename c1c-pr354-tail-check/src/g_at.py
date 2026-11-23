"""Exact g(t) = int f(x) f(x+t) dx for the #354 piecewise-polynomial certificate.

Own code, written from the format in the certificate README only:
f = (1/s) 1_[-s/2, s/2) + h,  h(x) = sum_k c_k (x - lo)^k on each piece [lo, hi).
"""
import json, sys
from fractions import Fraction as F
from math import comb

d = json.load(open(sys.argv[1]))
s, T, t1, M = (F(d[k]) for k in ("s", "T", "t1", "M"))
P = [(F(a), F(b), [F(c) for c in cs]) for a, b, cs in d["pieces"]]


def shift(c, a):
    """coefficients in x of sum_k c_k (x - a)^k"""
    out = [F(0)] * len(c)
    for k, ck in enumerate(c):
        if ck:
            for j in range(k + 1):
                out[j] += ck * comb(k, j) * (-a) ** (k - j)
    return out


def mul(p, q):
    r = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        if a:
            for j, b in enumerate(q):
                r[i + j] += a * b
    return r


def integ(p, u, v):
    return sum(c * (v ** (k + 1) - u ** (k + 1)) / (k + 1) for k, c in enumerate(p))


X = [(a, b, shift(c, a)) for a, b, c in P]          # h on [a,b) as a polynomial in x


def int_h(u, v):
    return sum(integ(p, max(u, a), min(v, b)) for a, b, p in X if max(u, a) < min(v, b))


def g(t):
    val = max(F(0), s - abs(t)) / s ** 2                          # spike * spike
    val += int_h(t - s / 2, t + s / 2) / s                        # spike(x) h(x+t)
    val += int_h(-t - s / 2, -t + s / 2) / s                      # h(x) spike(x+t)
    for a, b, p in X:                                             # h(x) h(x+t)
        for a2, b2, p2 in X:
            u, v = max(a, a2 - t), min(b, b2 - t)
            if u < v:
                q = [F(0)] * len(p2)
                for k, c in enumerate(p2):                        # p2(x + t)
                    for j in range(k + 1):
                        q[j] += c * comb(k, j) * t ** (k - j)
                val += integ(mul(p, q), u, v)
    return val


print("pieces:", [(float(a), float(b - a)) for a, b, _ in X][-2:], " last hi - 1 == s/2:", X[-1][1] - 1 == s / 2)
print("int h == M:", int_h(F(-1), F(2)) == M, " (so int f = 1 + M)")
for name, t in [("1-t1", 1 - t1), ("1-t1+s/4", 1 - t1 + s / 4), ("1-t1+s/2", 1 - t1 + s / 2),
                ("1", F(1)), ("0.5", F(1, 2))]:
    e = g(t) - T
    print(f"g({name}) - T = {float(e):.10e}  exact zero: {e == 0}  sign: {(e > 0) - (e < 0)}")
