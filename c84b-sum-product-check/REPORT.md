# C_84b row 1.999281*: does not replay as recorded

**Row** (`constants/84b.md`, upper bounds): `$1.999281$ | [Al26], [EPF52] | … optimization of the explicit
constant of [BSSZ2026, §5] giving $c \ge 0.000719$. Unverified.` README cell: `$<2$ (1.999281*)`.

**Finding.** The cited note [Al26] (althofer.de/improved_constant_052.tex) does **not** prove c ≥ 0.000719.
- Its theorem states the "safe" constant c = 0.0007, i.e. max(|A+A|,|AA|) ≤ |A|^{2−0.0007}, and calls 0.000719
  only "the optimized value suggested by the same calculation".
- The forum post [EPF52] (Bloom, 28 May 2026) says "Ingo has already obtained c = 0.000719" and links that same note.

**Check** (`check_84b.py`, mpmath interval arithmetic, taking the note's lemmas and inputs as given: ε = (φ−1)/(φ+1),
C₂ = 857.57, R_K ≤ 103^d, |GG| ≤ 5^{d−1}|G|, the stated bounds for |A|, |AA|, |A+A|, and L > log(5Y+1) + log(2εX+1)):

| setting | saving c | exponent 2 − c |
|---|---|---|
| the note's choice Y = 1415, X = e^1423 (L exact) | 0.00070625 | 1.99929375 |
| same, with L rounded to 1432 as in the note | 0.00070573 | 1.99929427 |
| best over Y ∈ [600, 6000), X = e^x (R_K ≤ 103^d) | 0.00070673 (Y ≈ 1410, x ≈ 1417) | 1.99929327 |
| best, regulator at its limit 101.956… (any b > 101.9560758 works for large d) | 0.00071385 (Y ≈ 1400) | 1.99928615 |

The regulator minimisation in the note checks out: min over s > 1 of ζ(s)Γ(s/2)C₂^{s/2}/(2π^{s/2}) = 101.95607583 at
s = 1.371966384. So even pushed to its limit, the argument gives c < 0.000714, short of 0.000719. The recorded
1.999281 is below everything the cited argument supports.

**What the source supports:** C_84b ≤ 2 − 0.0007 = 1.9993 (the note's theorem). With the parameters optimised and
the regulator constant at its limit, 2 − 0.000713 = 1.999287 is also supported (rounded up).

**Not checked:** the lemmas themselves against [BSSZ2026, §5] (the lattice-doubling lemma is the standard Ruzsa
covering argument and looks right; the product/sum estimates are taken from the note). This is a check of the
recorded number against its cited argument, not a full proof review.

**Suggested correction (for Jeetu / the main session to decide; no PR opened, per the rules):** change the row to
`$1.9993$*` with Comments "the note proves c ≥ 0.0007; the 0.000719 it mentions is not reached by its argument
(its optimum is c ≈ 0.000706 with R_K ≤ 103^d, < 0.000714 in the limit)", and the README cell to `$<2$ (1.9993*)`.
