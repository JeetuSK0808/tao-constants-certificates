# Independent replay of the C_89 upper bound of teorth/optimizationproblems#380

Target: $C_{89} \le 0.0301388757$* (Ivan Staroselets, pull request #380). The witness is `c89_7680_delta_D20.npz` at
sunil123456897/lean-dag-rsi @ `477024cffe4b`, SHA-256 `44c6ba58…ae2f`, on top of the [SK2026] base
`c89_stepgraphon_D20.json.gz` (`../c89-k4-ramsey-multiplicity`, SHA-256 `82c28f77…631a`).

Construction, as stated in the claimant's README: every one of the 3840 equal-weight blocks $i$ of the base
(red probability $R_{ij}/2^{20}$) is split into halves $(i,\pm)$ of equal weight, with
$W((i,\sigma),(j,\tau)) = (R_{ij} + \sigma\tau\,d_{ij})/2^{20}$, $d$ symmetric, $d_{ii} = 0$.

## Method (derived here, not taken from the claimant's code)

Write the monochromatic-$K_4$ density of the split graphon as an average over the four base blocks and four
independent uniform signs $\sigma_1,\dots,\sigma_4$. Expanding the six edge factors $R_e + \sigma_i\sigma_j d_e$
(and $B_e - \sigma_i\sigma_j d_e$ for blue, $B = 2^{20} - R$), a term survives the average over signs only if its
set of $d$-edges has even degree at every vertex. In $K_4$ those sets are the empty set, the 4 triangles and the
3 four-cycles. So, with $m = 3840$ and $D = 2^{20}$,

$$c_4(W') = c_4(R) + \frac{N_3 + N_4}{m^4 D^6},\qquad
N_3 = 4\sum_{a,b,c} d_{ab}d_{bc}d_{ca}\,(T^R_{abc} - T^B_{abc}),\quad T^X_{abc} = \sum_x X_{ax}X_{bx}X_{cx},$$
$$N_4 = 3\sum_{a,b,c,e} d_{ab}d_{bc}d_{ce}d_{ea}\,(R_{ac}R_{be} + B_{ac}B_{be}).$$

`src/split_k4.py` computes $N_3$ and $N_4$ around each block $a$ (its $d$-neighbourhood has at most 144 blocks)
modulo 9 primes below $1.5 \cdot 10^6$, where float64 matrix products are exact because $m p^2 < 2^{53}$, combines them by CRT,
and checks a tenth prime. $c_4(R)$ is the exact [SK2026] value. Our own `exact_eval.py` computed it over every block,
and A. Canli and C. Toledo replayed it independently (teorth/optimizationproblems#255, #276).

## Independence

Only the witness `.npz`, the README and the result file were downloaded. `verify_c89_exact.py` was neither read nor
run. The formula above was derived independently. Before the real run, a self-test compares it with brute-force
enumeration of all $(2m)^4$ vertex tuples of the split graphon (exact fractions) on 12 random small cases:
0 mismatches.

## Result (`results/output.txt`)

- 221,460 pairs $i<j$ (so $d_{ii} = 0$), no duplicates, all with $d \ne 0$; $0 \le R_{ij} \pm d_{ij} \le 2^{20}$ holds for every pair.
- $N_3 = -1399283324392161754041842816623728081781248$ and $N_4 = 339679930283823800995436414137045356788976$,
  identical to the claimant's. The check prime agrees.
- $c_4 = 544416702963479534354424655876570459894446711323/18063603610809804744643931800845172819844136960000
  = 0.030138875647032255146857957744\ldots$, exactly the stated fraction. It is $3.666 \cdot 10^{-9}$ below [SK2026] and
  $5.30 \cdot 10^{-11}$ below the printed $0.0301388757$.
- Controls: the printed bound one unit lower ($0.0301388756$) does not hold, and moving the largest $d_{ij}$ by one
  unit changes $N_3 + N_4$.

About 21 minutes on 4 threads (Apple M5 Pro), at about 2 minutes per prime.

```
./fetch.sh   # witness from the claimant's commit; base from this repository; hashes checked
./run.sh     # needs numpy
```

Conflict of interest: the replayer is the author of [SK2026], which is both the base of this construction and the
bound it improves. Written with Claude Code (Anthropic).
