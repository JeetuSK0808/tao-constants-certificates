# Independent replays of the C_1c lower bounds of teorth/optimizationproblems #318 and #366

Written for the consolidated C_1c pull request, which brings #318, #344, #354 and #366 together.

Targets:
- #318, [J2026], K. Julsgaard: $C_{1c} \ge 0.4103538918$*, with certificate `cert/certificate.json` at
  Julsgaard/c1c-certificate @ `91e47b1` (SHA-256 `fe113…2d2`).
- #366, [Esc2026], M. H. Julner / intervalplace: $C_{1c} \ge 0.4103735$*, with certificate `K98304_0.4103735.json`
  at intervalplace/frontier @ `c0bcdfb` (SHA-256 `ff375…9ead`; this matches the claimant's SHA256SUMS).

#344's certificates are replayed in `../c1c-autocorrelation-replay-pr344/` and `../c1c-autocorrelation-replay-pr344-k1048576/`.
#354 is an exact piecewise-polynomial construction, not a step function, so this replay does not apply to it.

Rule replayed (constants/1c.md): $C_{1c} \ge K \min_{0 \le k \le K} A_k / S^2$, where $A_k = \sum_i w_i w_{i+k}$ and
$S = \sum_i w_i$, for $f = \sum_i w_i 1_{[i/K,(i+1)/K)}$ with integer $w_i \ge 0$.

## Independence

Only the two certificates' JSON files were downloaded. The claimants' checkers (`check_flint.py` and
`verify_kronecker.py` for #318, `verify.py` for #366) were neither read nor run. The two implementations used here
share no code with each other, and they are the ones from our #344 replay, with the spike special case removed:

- `src/lags2.c` sums every lag directly in unsigned 128-bit integers. It refuses input unless $n (\max w)^2 < 2^{127}$.
- `src/kronlags.py` gets all lags from one big-integer product (Kronecker substitution).
- `src/selftest.py` checks that both agree with a naive sum at every lag, on 80 random cases shaped like the certificates.

## Result (`results/replay_output.txt`)

| | #318 [J2026] | #366 [Esc2026] |
|---|---|---|
| K, weights | 98304, 98368 (largest < 2^41) | 98304, 98368 (largest < 2^50) |
| the two implementations | agree at all 98,305 lags | agree at all 98,305 lags |
| $K \min_k A_k / S^2$ | 2582127846607416062611587072/6292441470965870058830439361 = 0.41035389181157810991… | 1376728953781146098572851250003968/3354819039892156766926073767410361 = 0.41037353651879897149… |
| minimum attained at | k = 47318 only | k = 15880 only |
| equals the row's stated fraction | yes | yes (also the certificate's own score fields) |
| implies the claim | 0.4103538918: yes | 0.4103735: yes |
| control: largest weight + 1 | value changes | value changes |

Re-derive: `./fetch.sh && ./run.sh`. This needs Python 3.9+ (standard library only) and a C compiler, and takes
about 30 seconds on a laptop.

Prepared with Claude Code (Anthropic), under J. SK's direction. There is no connection with the claimants beyond the
optimizationproblems threads.
