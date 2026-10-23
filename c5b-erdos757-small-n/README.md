# Exact small values for Erdős problem #757 (Sidon subsets of (4,5)-sets)

A finite set A of reals is a (4,5)-set if every 4 of its elements determine at least 5 distinct differences.
Let h(A) be the size of its largest Sidon subset and f(n) = min h(A) over (4,5)-sets of size n. Erdős asked
for c* = lim f(n)/n; Ma and Tang (arXiv:2602.23282) proved c* = inf f(n)/n and 9/17 ≤ c* ≤ 4/7
(constant C_5b in the Optimization Constants repository, teorth.github.io/optimizationproblems).

## Result

| n | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 17 | 19 | 21 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f(n) | 4 | 5 | 5 | 6 | 6 | 7 | 7 | 8 | 8 | 9 | 10 | 11 | 12 |

- Upper bound: `certificates/n<N>.txt` is an explicit (4,5)-set of N integers with h = f(N).
- Lower bound: f(n) ≥ n − ⌊(8n − 6)/17⌋ for n ≥ 2, which is the argument of Ma–Tang §5.2 (Henning–Yeo's bound
  17τ ≤ 5n + 3m for linear F₇-free 3-graphs applied to the A.P. hypergraph, with m ≤ n − 2).
  The two bounds agree for every n listed.

None of these beats 4/7. A search over midpoint structures at n = 16, 18, 20, 22, 23, 25, 30, the sizes where
the lower bound still allows a beat, found nothing below ⌈4n/7⌉; this suggests c* = 4/7.

## Verify

Python 3 only, exact integer arithmetic, uses only the definitions (all 4-subsets; a Sidon subset of size h;
no Sidon subset among all (h+1)-subsets):

    ./check_all.sh
    python3 verify.py certificates/n21.txt

## AI use

The search code, the checker and this note were developed with Claude Code (Anthropic) under the direction of
Jeetu SK. Every number above is reproduced by `check_all.sh`.
