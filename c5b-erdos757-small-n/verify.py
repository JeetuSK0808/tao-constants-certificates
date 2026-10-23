#!/usr/bin/env python3
"""Independent exact checker for an upper bound on C_5b (Erdos problem #757).

Input: a file of distinct integers (whitespace separated).  Uses only the definitions:
  * (4,5)-set: every 4-element subset has at least 5 distinct pairwise absolute differences;
  * Sidon set: all sums x + y with x <= y are distinct;
  * h(A): the largest Sidon subset.
It checks all C(n,4) four-subsets, exhibits a Sidon subset of size h, and checks that no subset
of size h + 1 is Sidon (enough, since Sidon is closed under taking subsets).  Pure Python
integers, no floating point, no shared code with the search.

By Ma-Tang (arXiv:2602.23282, Theorem 1.5) c* = inf_n f(n)/n, so a (4,5)-set A gives
C_5b <= h(A)/|A|.

usage: python3 verify.py certificate.txt
"""
import sys
from fractions import Fraction
from itertools import combinations


def is_45_set(A):
    for B in combinations(A, 4):
        d = {abs(x - y) for x, y in combinations(B, 2)}
        if len(d) < 5:
            return False, B
    return True, None


def is_sidon(S):
    sums = set()
    for i, x in enumerate(S):
        for y in S[i:]:
            if x + y in sums:
                return False
            sums.add(x + y)
    return True


def largest_sidon(A):
    """Exact h(A): grow k until no k-subset is Sidon."""
    best = None
    k = 1
    while True:
        found = next((S for S in combinations(A, k) if is_sidon(S)), None)
        if found is None:
            return k - 1, best
        best, k = found, k + 1


def main():
    A = [int(t) for t in open(sys.argv[1]).read().split()]
    n = len(A)
    assert len(set(A)) == n, "elements must be distinct"
    A = sorted(A)
    ok, bad = is_45_set(A)
    print(f"n = {n}, elements in [{A[0]}, {A[-1]}]")
    print(f"(4,5)-property over all {n*(n-1)*(n-2)*(n-3)//24} four-subsets: {'PASS' if ok else 'FAIL ' + str(bad)}")
    if not ok:
        sys.exit(1)
    h, S = largest_sidon(A)
    print(f"largest Sidon subset h(A) = {h}, e.g. {list(S)}")
    print(f"checked: no Sidon subset of size {h + 1} among all C({n},{h + 1}) subsets")
    r = Fraction(h, n)
    print(f"bound: C_5b <= h(A)/|A| = {r} = {float(r):.6f}  (previous best 4/7 = {4/7:.6f})")
    print("IMPROVES 4/7" if r < Fraction(4, 7) else "does not improve 4/7")


if __name__ == "__main__":
    main()
