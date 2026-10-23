#!/usr/bin/env python3
"""Weights and final bound for the C_31 replay, in exact rational / 60-digit decimal arithmetic.

  certify.py weights h z_decimal out.txt   -> 2h-1 hex doubles, each >= the exact weight
  certify.py bound   h z_decimal maxratio_hex ops
      lambda_cert = maxratio * (1 - 2^-53)^-ops  (exact), then
      gamma_2 <= 2 log(2z) / log(lambda_cert), evaluated at 60 digits and rounded up.
z is the double nearest to z_decimal, as in the claim.
"""
import math
import sys
from decimal import Decimal, getcontext, ROUND_CEILING
from fractions import Fraction

getcontext().prec = 60


def up_double(q):
    """smallest double >= the positive rational q"""
    d = float(q)
    while Fraction(d) < q:
        d = math.nextafter(d, math.inf)
    return d


def weights(h, z):
    w = {}
    for l in range(-(h - 1), h):
        k = abs(l)
        q = z ** (k + 2) if k < h - 1 else z ** (h + 1) / (1 - z)
        w[l] = up_double(q)
    return [w[l] for l in range(-(h - 1), h)]


def dec(q):
    return Decimal(q.numerator) / Decimal(q.denominator)


def main():
    mode, h = sys.argv[1], int(sys.argv[2])
    zd = float(sys.argv[3]); z = Fraction(zd)
    if mode == "weights":
        with open(sys.argv[4], "w") as fh:
            for x in weights(h, z):
                fh.write(x.hex() + "\n")
        return
    rmax = Fraction(float.fromhex(sys.argv[4])); ops = int(sys.argv[5])
    lam = rmax / (1 - Fraction(1, 2 ** 53)) ** ops
    num = 2 * dec(2 * z).ln()
    den = dec(lam).ln()
    g = num / den
    # 60-digit evaluation error is far below 1e-40; add a 1e-40 margin, then round up to 6 decimals
    g_up = (g + Decimal("1e-40")).quantize(Decimal("0.000001"), rounding=ROUND_CEILING)
    print(f"h={h} z={zd!r} lambda_cert={float(lam)!r} (<= {dec(lam):.18f})")
    print(f"gamma_2 <= {g:.15f}...  ->  certified gamma_2 <= {g_up}")


if __name__ == "__main__":
    main()
