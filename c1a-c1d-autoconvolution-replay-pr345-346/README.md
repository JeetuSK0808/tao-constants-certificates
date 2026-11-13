# Independent replay of the C_1a and C_1d upper bounds of teorth/optimizationproblems#346 and #345

Targets (A. Canli, certificates at arhancanli/quantavane-replays @ `cc2c67d`, as updated on 10 Nov):

- #346: $C_{1a} \le 1.5027427280$*, `improvements/c1a/c1a_upper_n262144_v2.json`, SHA-256 `cfbf05a1…bff6`.
- #345: $C_{1d} \le 1.4546733414$*, `improvements/c1d/c1d_upper_n163840_v2.json`, SHA-256 `253d0ca6…3a82`.

Rule replayed (constants/1a.md and 1d.md): $f = v_i$ on $n$ equal cells of $[-1/4,1/4]$, $h = 1/(2n)$. The
autoconvolution $f*f$ is piecewise linear with knots at multiples of $h$. At a knot it equals $h\sum_{i+j=m} v_i v_j$,
and $\int f = h \sum_i v_i$. So

$$\max_t \lvert f*f \rvert / (\textstyle\int f)^2 = 2n \max_m \lvert c_m \rvert / S^2, \qquad c = v*v,\ S = \sum_i v_i.$$

For $C_{1a}$ the replay also checks $v_i \ge 0$. For $C_{1d}$ the values are signed.

## Independence

Only the certificates' JSON was downloaded. The claimant's `check.py` and `ntt_check_conv.py` were neither read nor
run. Nothing of theirs is reused beyond $n$, the $v_i$, and the stated fraction and claim, which are compared at the
end. There are two implementations, and they share no code with each other:

- `src/conv.c` sums every knot directly. Each value is split as $v = a 2^{28} + b$ with $a = \lfloor v/2^{28} \rfloor$
  and $0 \le b < 2^{28}$. That way every partial product fits in 64 bits and each partial sum fits in signed 128
  bits. The program refuses $\lvert v_i \rvert > 2^{56}$.
- `src/kronconv.py` gets every knot from one big-integer squaring (Kronecker substitution). Signed values are shifted
  to $u = v + C \ge 0$, and the exact correction $2C\,W_m + C^2 N_m$ is subtracted afterwards.
- `src/selftest.py` checks that both agree with a naive sum at every knot on 80 random cases. The cases cover
  non-negative values, signed values, and values at the extremes $\pm 2^{56}$.

## Result (`results/replay_output.txt`)

| PR | data | value (exact) | max at | implies |
|---|---|---|---|---|
| #346 | $n = 262144$, $0 \le v_i \le 2^{56}$ | $29131355358281158426614181216278902472704/19385457547511099408999611434350080635225 = 1.50274272798999968357\ldots$ | $m = 303135$ only | $1.5027427280$, not $\ldots279$ |
| #345 | $n = 163840$, $-2.7 \cdot 10^{16} \le v_i \le 2^{56}$ | $838861227937471890002426104328885370880/576666392427609677715360509915372739121 = 1.45467334138563686456\ldots$ | $m = 52929$ only | $1.4546733414$, not $\ldots413$ |

- Both values are exactly the certificates' fractions. The two implementations agree at all 524,287 and all 327,679 knots.
- #346 is below #270's exact value by $6.065 \cdot 10^{-9}$ and below [A2026] by $7.587 \cdot 10^{-7}$.
- #345 is below #270's exact value by $4.382 \cdot 10^{-9}$, below #312 by $5.432 \cdot 10^{-5}$ and below [SCIEL2026]
  by $3.18 \cdot 10^{-3}$.
- Controls: lowering one value by 1 changes the value. Cutting the largest value by 1% gives a value that no longer
  implies the claim.

Re-derive: `./fetch.sh && ./run.sh` (Python 3.9+ standard library and a C compiler; under a minute on a laptop).

Prepared with Claude Code (Anthropic), under J. SK's direction. No connection with the claimant beyond the
optimizationproblems threads.
