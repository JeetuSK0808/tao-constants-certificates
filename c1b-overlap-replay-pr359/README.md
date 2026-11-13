# Independent replay of the C_1b upper bound of teorth/optimizationproblems#359

Target: $C_{1b} \le 0.3808585498$* (A. Canli, pull request #359, certificate `c1b_upper_n114688.json` at
arhancanli/quantavane-replays @ `b47cbc4`, SHA-256 `e285b485…9ca5`).

Rule replayed (constants/1b.md, Erdős minimum overlap): $f = a_i/D$ on the $n$ equal cells of $[-1,1]$, $g = 1-f$
on $[-1,1]$, both zero outside, with integers $0 \le a_i \le D$ and $\sum_i a_i = nD/2$ (so $\int f = 1$). For two
step functions on the same grid, $x \mapsto \int f(t) g(x+t)\,dt$ is linear between multiples of $2/n$, so

$$C_{1b} \le \frac{2}{n D^2} \max_{|k| < n} S_k, \qquad S_k = \sum_i a_i (D - a_{i+k}).$$

## Independence

Only the certificate's JSON was downloaded. The claimant's `check_1b.py` and `ntt_check_1b.py` were neither read
nor run, and nothing of theirs is reused beyond $n$, $D$, the $a_i$ and the stated fraction (compared at the end).
Two implementations, sharing no code with each other:

- `src/shifts.c` sums every shift directly in unsigned 128-bit integers (each product is below $D^2 = 2^{96}$, each sum
  below $n D^2 < 2^{113}$; it refuses inputs where $n D^2 \ge 2^{127}$).
- `src/kron1b.py` gets all shifts from one big-integer product (Kronecker substitution, 120-bit slots).
- `src/selftest.py`: both agree with a naive sum at every shift on 60 random cases ($n \le 97$, $D$ up to $2^{56}$,
  including all-0/all-$D$ patterns).

## Result (`results/replay_output.txt`)

- $n = 114688$, $D = 2^{48}$; box $0 \le a_i \le D$ and mass $\sum a_i = nD/2$ hold exactly.
- The two implementations agree at all 229,375 shifts.
- Maximum at $k = \pm 11464$ only; the next largest shift is lower by $1.29 \cdot 10^{-12}$.
- Value $= 1730339319993979413608789703258449/4543259751217974174964184288067584 = 0.380858549751663117147\ldots$,
  exactly the certificate's fraction. It implies $0.3808585498$ and not $0.3808585497$.
- Below the page's [A2026] exact value $0.38085855031642856010\ldots$ by $5.648 \cdot 10^{-10}$, and below [EA2026]
  ($0.38085857485785830914\ldots$) by $2.511 \cdot 10^{-8}$.
- Controls: raising one cell by 1 changes the value; moving $10^9$ units between two cells (mass kept) gives a value
  that no longer implies the claim; raising every cell by 1% gives $0.3814634\ldots$.

Re-derive: `./fetch.sh && ./run.sh` (Python 3.9+ standard library and a C compiler; about 10 seconds on a laptop).

Prepared with Claude Code (Anthropic), under J. SK's direction. No connection with the claimant beyond the
optimizationproblems threads.
