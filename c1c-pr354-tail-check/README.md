# Where g = T in the #354 piecewise-polynomial C_1c certificate

A small exact check behind a one-line text fix in teorth/optimizationproblems#383 (the C_1c consolidation), following a review comment there.

The [Sag2026] certificate (#354) uses f = (1/s) 1_[-s/2, s/2) + h with s = 2^-120, h = T on [1 - t1, 1 + s/2). Its row said g = T on [1 - t1, 1]. In fact the constant tail starts at 1 - t1 + s/2:

| t | g(t) - T (exact rational, printed as float) |
|---|---|
| 1 - t1 | 4.1726786880e-71 (> 0) |
| 1 - t1 + s/4 | 1.0450044116e-71 (> 0) |
| 1 - t1 + s/2 | 0 exactly |
| 1 | 0 exactly |

The lower bound is unaffected (g >= T still holds at these points). Between 1 - t1 + s/2 and 1 the spike window sees only h = T and the h·h overlap is empty, so g = T exactly there.

`src/g_at.py` is our own code, written from the certificate format in the claimant's README only. Only the JSON was downloaded; the claimant's verifiers were neither read nor run. As a format check it also confirms ∫h = M exactly. It uses Python fractions and runs in under a second.

    ./fetch.sh   # downloads the JSON and checks sha256 8aa13b61…340f
    ./run.sh     # writes results/output.txt

Prepared with Claude Code.
