# Independent replay of the C₃₁ upper bounds of [J2026]

Target rows (teorth/optimizationproblems, `constants/31a.md`, both asterisked):

| claim | h | z | λ(z) ≤ | bound |
|---|---|---|---|---|
| [J2026] | 9 | 0.3298 | 0.364708361184292 | γ₂ ≤ 0.825101 |
| [J2026] | 10 | 0.3376 | 0.385532705434511 | γ₂ ≤ 0.824120 |

Method: Lueker's automaton M_h (J. ACM 56(3), 2009, §3). If A_z v ≤ λ v for a positive vector v, then
γ₂ ≤ 2 log(2z) / log λ (Theorem 3.3 of Lueker, after Dančík–Paterson).

## Independence

`lcsauto.c` was written from scratch. The automaton's semantics come from Lueker's published programs
(ics.uci.edu/~lueker/papers/lcs/code/upper/: `DPTable.java`, `State.java`, `StateTable.java`, `GenFn.java`), the
original author's reference implementation, read as a specification. **No file of the claimant's repository
(leandrejack-afk/chvatal-sankoff-bound) was read or run except its README and its `certificates/*.out` and weight
files**, which were only used to see the claimed numbers. The vector v is our own: no eigenvector from the claimant
is used, and any positive v gives a valid certificate.

What differs from the claimant's pipeline (as described in their README): our own state packing, hash and BFS
builder; our own table format; our own power iteration; certification **without** changing the rounding mode
(round to nearest, then the exact inflation (1 − 2⁻⁵³)^−(4h+1), which covers the ≤ 2(2h−1) products and sums and the
division per state); weights rounded up from exact rationals; and the final log quotient in 60-digit decimal
arithmetic.

## Checks

- **State counts reproduce Lueker's Table II exactly** for h = 2, …, 8: 7, 98, 1020, 10160, 89960, 780368, 6419109.
  At h = 8 there are 91,508,397 accepted transitions.
- **Lueker's h = 8 bound reproduced:** λ(0.3209) = 0.341832258734487, certified γ₂ ≤ 0.826280.
- **The parallel builder is byte-identical to the sequential one** at h = 8.
- **The DP never reads an unset entry:** sentinel-initialised table, aborts otherwise. All differences are 0/1, every
  canonical backtrack uses exactly one match, and every state's accepted paddings form an interval.
- h = 9: 51,425,006 states (as claimed), 790,078,170 accepted transitions (51,425,006 × 34 = 1,748,450,204 inputs
  tried, the claimant's figure), min vᵢ = 0.00728 (no underflow).
- h = 10: 400,253,317 states (as claimed), 6,574,257,580 accepted transitions; the power iteration was stopped at
  iteration 130, once the max ratio was below 0.38553279. The threshold for 0.824120 is 0.3855328021, and the next
  iterate's max ratio is never larger. Min vᵢ = 0.0036. Our λ_cert is a little above the claimant's 0.385532705
  (we stopped earlier), and it still certifies 0.824120.
- Vectors are stored as float32 (exact doubles; any positive vector certifies); sums are in double.

## Results

| h | z | states | our λ_cert | γ₂ ≤ (exact) | certified | claim |
|---|---|---|---|---|---|---|
| 8 | 0.3209 | 6,419,109 | 0.341832258732947 | 0.8262791785922… | 0.826280 | Lueker 0.826280 |
| 9 | 0.3298 | 51,425,006 | 0.364708361184292 | 0.8251002729380… | **0.825101** | 0.825101 ✓ |
| 10 | 0.3376 | 400,253,317 | 0.385532782589023 | 0.8241199562929… | **0.824120** | 0.824120 ✓ |

## Reproduce

Needs a C compiler and Python 3. h = 10 needs about 16 GB of RAM to build and about 30 GB of disk.

```bash
cc -O2 -ffp-contract=off -o lcsauto lcsauto.c -lm -lpthread
```

```bash
./run.sh 9 0.3298
```

```bash
./run.sh 10 0.3376 0.38553279
```

`run.sh` builds the table, writes upward-rounded weights (`certify.py weights`), runs the power iteration
(Lueker's stopping rule max/min ratio ≤ 1 + 10⁻¹⁰, or the optional target λ), certifies (`lcsauto cert`) and evaluates the bound
(`certify.py bound`). Outputs go to `data/`.

AI use: written with Claude Code (Anthropic) under the direction of Jeetu SK.
