# Independent replay of the C_1c lower bound of teorth/optimizationproblems#344

Target: $C_{1c} \ge 0.4103598711$* (A. Canli, pull request #344, certificate `c1c_lower_K98304.json` at
arhancanli/quantavane-replays @ `c40060f`, SHA-256 `17c7640a…9d35`).

Rule replayed (the page's exact rule for step functions): $C_{1c} \ge K \min_{0 \le k \le K} A_k / S^2$ with
$A_k = \sum_i w_i w_{i+k}$ and $S = \sum_i w_i$, for $f = \sum_i w_i 1_{[i/K,(i+1)/K)}$ with integer $w_i \ge 0$. The
autocorrelation of an equal-step function is linear between multiples of $1/K$, so the minimum over $t \in [0,1]$ is
attained at some $t = k/K$.

## Independence

Only the certificate's JSON was downloaded. The claimant's `check.py` was neither read nor run, and nothing of
theirs is reused beyond the weights and the claimed fraction. Two implementations, sharing no code with each other:

- `src/lags.c` sums every lag directly. Each weight is split as $w = a 2^{28} + b$, so every partial product is below
  $2^{56}$ and each partial sum fits in 128 bits. It is exact for any weight below $2^{56}$ and refuses larger ones.
- `src/kron.py` gets all lags from one big-integer product (Kronecker substitution, 136-bit slots).
- `src/selftest.py`: both agree with a naive sum at every lag on 40 random cases, with weights up to $2^{56}-1$.

## Result (`results/replay_output.txt`)

- 98,368 non-negative integer weights, $K = 98304$, largest weight $2^{56} - 8$.
- The two implementations agree at all 98,305 lags.
- $K \min_k A_k / S^2 = 11005597691381428229825143056897540096/26819380902505338613619516881482225625
  = 0.41035987114651620459\ldots$, exactly the certificate's fraction. The minimum is attained only at $k = 98304$.
- It implies $0.4103598711$, and not $0.4103598712$. It is above the stated values of #270 (by $2.199 \cdot 10^{-7}$),
  #318 (by $5.979 \cdot 10^{-6}$) and the page's $0.4103333$ [Kos2026] (by $2.652 \cdot 10^{-5}$).
- Controls: raising one weight by 1 changes the value, and raising the largest weight by 1% changes it to one that no
  longer implies the claim.

Re-derive: `./fetch.sh && ./run.sh` (Python 3.9+ standard library and a C compiler; about 4 minutes on a laptop,
most of it the big-integer product).

Prepared with Claude Code (Anthropic), under J. SK's direction. No connection with the claimant.
