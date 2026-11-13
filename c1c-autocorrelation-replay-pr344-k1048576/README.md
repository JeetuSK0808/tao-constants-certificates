# Independent replay of the current C_1c lower bound of teorth/optimizationproblems#344 (K = 2^20)

Target: $C_{1c} \ge 0.4103780000$* (A. Canli, pull request #344 as updated on 10 Nov, certificate
`c1c_lower_K1048576.json` at arhancanli/quantavane-replays @ `101c945`, SHA-256 `fc69d772…2352`). The earlier
$K = 98304$ certificate of the same pull request is replayed in `../c1c-autocorrelation-replay-pr344/`.

Rule replayed (constants/1c.md): $C_{1c} \ge K \min_{0 \le k \le K} A_k / S^2$, where $A_k = \sum_i w_i w_{i+k}$ and
$S = \sum_i w_i$, for $f = \sum_i w_i 1_{[i/K,(i+1)/K)}$ with integer $w_i \ge 0$. The autocorrelation of an
equal-step function is linear between multiples of $1/K$.

## Independence

Only the certificate's JSON was downloaded. The claimant's `check.py` and `ntt_check.py` were neither read nor run.
There are two implementations, and they share no code with each other:

- `src/lags2.c` sums every lag directly in unsigned 128-bit integers, skipping the zero runs. It refuses input unless
  $n (\max w)^2 < 2^{127}$. The one large spike $w_0 = 2^{60} - 128$ is held out of the C input, and its terms
  $w_0^2$ and $w_0 w_k$ are added exactly in Python. All other weights are below $2^{42}$.
- `src/kronlags.py` gets all lags, spike included, from one big-integer product (Kronecker substitution, 152-bit slots).
- `src/selftest.py`: both agree with a naive sum at every lag on 60 random cases shaped like the certificate (a spike
  up to $2^{60}$, a zero run, then a profile).

## Result (`results/replay_output.txt`)

- $K = 1048576$, with 1,048,577 weights. The spike holds 40.14% of the mass, $w_i = 0$ for $1 \le i < 167980$, and the
  rest is the profile.
- The two implementations agree at all 1,048,577 lags.
- $K \min_k A_k / S^2 = 3385460305559548364109249137976803328/8249614514518895716878560524318391809
  = 0.41037800003882762970\ldots$. This is exactly the certificate's fraction, and the minimum is attained only at $k = 179183$.
- All 880,597 lags in $[167980, K]$ are within $1.7 \cdot 10^{-13}$ of the minimum. The lags below 167980 are at least
  $0.4103782842$.
- The value implies $0.4103780000$, and not $0.4103780001$. It is above the morning certificate's $0.4103774129$ (by
  $5.871 \cdot 10^{-7}$), #354's $0.4103772$ (by $8.000 \cdot 10^{-7}$) and the page's $0.4103333$ (by $4.470 \cdot 10^{-5}$).
- Controls: raising one weight by 1 changes the value. Raising the spike by 1% gives a value that no longer implies the claim.

Re-derive: `./fetch.sh && ./run.sh` (Python 3.9+ standard library and a C compiler; about 8 minutes on a laptop,
most of it the big-integer product and the controls).

Prepared with Claude Code (Anthropic), under J. SK's direction. No connection with the claimant beyond the
optimizationproblems threads.
