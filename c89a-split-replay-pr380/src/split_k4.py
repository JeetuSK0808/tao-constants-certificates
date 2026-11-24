# Independent exact replay of PR #380 (C_89 <= 0.0301388757*), written from the README's statement of the
# construction only (verify_c89_exact.py was neither read nor run).
#
# Construction: base R (m x m integers over D), every block i split into halves sigma = +-1 of equal weight,
#   W'((i,s),(j,t)) = (R_ij + s*t*d_ij) / D,  d symmetric, d_ii = 0.
# Averaging the six edge factors over independent uniform signs s_1..s_4, only edge sets with even degree at
# every vertex survive: the empty set, the 4 triangles and the 3 four-cycles of K_4. With B = D - R (blue gets -d):
#   N3 = 4 * sum_{a,b,c} d_ab d_bc d_ca (T^R_abc - T^B_abc),  T^X_abc = sum_x X_ax X_bx X_cx
#   N4 = 3 * sum_{a,b,c,e} d_ab d_bc d_ce d_ea (R_ac R_be + B_ac B_be)
#   c4(W') = c4(R) + (N3 + N4) / (m^4 D^6).
# N3 and N4 are computed modulo primes p < 1.5e6 with float64 matrix products (exact while m p^2 < 2^53),
# then combined by CRT; one extra prime is a check.
import sys, gzip, json, time
from fractions import Fraction
import numpy as np

def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True

_ps = [q for q in range(1499999, 1400000, -2) if is_prime(q)][:10]
PRIMES, CHECK = _ps[:9], _ps[9]          # 9 CRT primes (product ~2^184) + 1 check prime, all < 1.5e6

def n3_n4_mod(R, B, Dm, nbrs, p):
    """Return (N3 mod p, N4 mod p). R, B: int64 m x m; Dm: int64 m x m symmetric d; nbrs[a]: indices b with d_ab != 0."""
    fR = (R % p).astype(np.float64); fB = (B % p).astype(np.float64); fd = (Dm % p).astype(np.float64)
    n3 = 0; n4 = 0
    for a in range(R.shape[0]):
        N = nbrs[a]
        if len(N) == 0: continue
        da = fd[a, N]                                            # d_ab, b in N
        # triangles through a: sum_{b,c in N} d_ab d_ac d_bc (T^R - T^B)[b,c]
        wt = np.mod(np.mod(np.outer(da, da), p) * fd[np.ix_(N, N)], p)       # d_ab d_ac d_bc
        TR = np.mod(np.mod(fR[N, :] * fR[a, :], p) @ fR[N, :].T, p)        # sum_x R_bx R_ax R_cx
        TB = np.mod(np.mod(fB[N, :] * fB[a, :], p) @ fB[N, :].T, p)
        n3 += int(np.mod(wt * np.mod(TR - TB, p), p).sum())
        # four-cycles a-b-c-e-a: X[c,b] = d_ab d_bc ; sum_c X_ac-weight * (X R_NN X^T)_cc
        X = np.mod(fd[:, N] * da, p)                              # m x |N|
        QR = np.mod(np.mod(X @ fR[np.ix_(N, N)], p) * X, p).sum(axis=1) % p   # sum_{b,e} X[c,b] R_be X[c,e]
        QB = np.mod(np.mod(X @ fB[np.ix_(N, N)], p) * X, p).sum(axis=1) % p
        n4 += int((np.mod(fR[a, :] * QR, p) + np.mod(fB[a, :] * QB, p)).sum())
        n3 %= p; n4 %= p
    return (4 * n3) % p, (3 * n4) % p

def crt(res, mods):
    M = 1
    for q in mods: M *= q
    x = 0
    for r, q in zip(res, mods):
        Mi = M // q; x += r * Mi * pow(Mi, -1, q)
    x %= M
    return x - M if x > M // 2 else x

def exact_N(R, B, Dm, nbrs, primes, check):
    r3, r4 = [], []
    for p in primes + [check]:
        t0 = time.time(); a, b = n3_n4_mod(R, B, Dm, nbrs, p); r3.append(a); r4.append(b)
        print(f"  p={p}: N3={a} N4={b} ({time.time()-t0:.0f}s)", flush=True)
    N3 = crt(r3[:-1], primes); N4 = crt(r4[:-1], primes)
    ok = (N3 % check == r3[-1]) and (N4 % check == r4[-1])
    return N3, N4, ok

def brute_c4(R, d, D):
    """Monochromatic K4 density of the split graphon by direct enumeration over (2m)^4 vertex tuples."""
    m = R.shape[0]; V = [(i, s) for i in range(m) for s in (1, -1)]
    W = {(u, v): Fraction(int(R[u[0], v[0]]) + u[1] * v[1] * int(d[u[0], v[0]]), D) for u in V for v in V}
    tot = Fraction(0)
    import itertools
    for q in itertools.product(V, repeat=4):
        red = Fraction(1); blue = Fraction(1)
        for i, j in itertools.combinations(range(4), 2):
            w = W[(q[i], q[j])]; red *= w; blue *= (1 - w)
        tot += red + blue
    return tot / len(V) ** 4

def brute_base(R, D):
    m = R.shape[0]; tot = Fraction(0)
    import itertools
    for q in itertools.product(range(m), repeat=4):
        red = Fraction(1); blue = Fraction(1)
        for i, j in itertools.combinations(range(4), 2):
            w = Fraction(int(R[q[i], q[j]]), D); red *= w; blue *= (1 - w)
        tot += red + blue
    return tot / m ** 4

def selftest(trials=12, seed=5):
    rng = np.random.default_rng(seed); bad = 0
    for t in range(trials):
        m = int(rng.integers(2, 5)); D = 64
        R = rng.integers(0, D + 1, size=(m, m)); R = np.triu(R) + np.triu(R, 1).T
        cap = np.minimum(R, D - R); d = np.zeros((m, m), dtype=np.int64)
        for i in range(m):
            for j in range(i + 1, m):
                if rng.random() < 0.8 and cap[i, j] > 0: d[i, j] = d[j, i] = int(rng.integers(-cap[i, j], cap[i, j] + 1))
        R = R.astype(np.int64); B = D - R
        nbrs = [np.nonzero(d[a])[0] for a in range(m)]
        r3, r4 = zip(*[n3_n4_mod(R, B, d, nbrs, p) for p in PRIMES])
        N3 = crt(r3, PRIMES); N4 = crt(r4, PRIMES)
        lhs = brute_c4(R, d, D); rhs = brute_base(R, D) + Fraction(N3 + N4, m ** 4 * D ** 6)
        bad += lhs != rhs
    return bad

if __name__ == "__main__":
    assert all(is_prime(q) for q in PRIMES + [CHECK]) and len(set(PRIMES + [CHECK])) == 10
    assert 3840 * max(PRIMES + [CHECK]) ** 2 < 2 ** 53
    print("self-test (split graphon by brute force over all (2m)^4 tuples vs base + (N3+N4)):",
          "mismatches =", selftest(), flush=True)
    if len(sys.argv) < 3: sys.exit(0)
    base_path, wit_path = sys.argv[1], sys.argv[2]
    g = json.load(gzip.open(base_path)); Dn = g["edge_probability_denominator"]
    R = np.array(g["red_probability_numerators"], dtype=np.int64); m = R.shape[0]
    assert Dn == 2 ** 20 and R.shape == (m, m) and (R == R.T).all() and R.min() >= 0 and R.max() <= Dn
    assert len(g["block_weights"]) == m and len(set(map(str, g["block_weights"]))) == 1, "equal block weights"
    z = np.load(wit_path, allow_pickle=False)
    eu, ev, dv = z["eu"].astype(np.int64), z["ev"].astype(np.int64), z["d_int"].astype(np.int64)
    assert int(z["D_out"]) == Dn and len(eu) == len(ev) == len(dv)
    assert (eu < ev).all() and (eu >= 0).all() and (ev < m).all(), "pairs must be i<j (so d_ii = 0)"
    assert len(set(zip(eu.tolist(), ev.tolist()))) == len(eu), "duplicate pair"
    Dm = np.zeros((m, m), dtype=np.int64); Dm[eu, ev] = dv; Dm[ev, eu] = dv
    lo = R - np.abs(Dm); hi = R + np.abs(Dm)
    print(f"m={m}, nonzero d pairs={int((dv != 0).sum())} of {len(dv)}, feasibility 0<=R+-d<=D: {bool(lo.min() >= 0 and hi.max() <= Dn)}", flush=True)
    assert lo.min() >= 0 and hi.max() <= Dn
    nbrs = [np.nonzero(Dm[a])[0] for a in range(m)]
    print("max degree of d-graph:", max(len(x) for x in nbrs), flush=True)
    B = Dn - R
    N3, N4, ok = exact_N(R, B, Dm, nbrs, PRIMES, CHECK)
    base = Fraction(27220838459434583306277336063848530765605851167, 903180180540490237232196590042258640992206848000)
    new = base + Fraction(N3 + N4, m ** 4 * Dn ** 6)
    claim = Fraction(544416702963479534354424655876570459894446711323, 18063603610809804744643931800845172819844136960000)
    print("check prime agrees:", ok)
    print("N3 =", N3); print("N4 =", N4)
    print("new c4 =", new, "=", f"{float(new):.20f}")
    print("equals the PR's stated fraction:", new == claim)
    print("new c4 <= 0.0301388757:", new <= Fraction(301388757, 10 ** 10), " below SK2026:", new < base)
    # controls
    if "--controls" in sys.argv:
        print("controls:", flush=True)
        print("  printed bound one unit lower (0.0301388756) holds?", new <= Fraction(301388756, 10 ** 10))
        k = int(np.argmax(np.abs(dv))); u, v = int(eu[k]), int(ev[k])
        D2 = Dm.copy(); D2[u, v] -= int(np.sign(D2[u, v])); D2[v, u] = D2[u, v]
        a3, a4 = n3_n4_mod(R, B, D2, [np.nonzero(D2[a])[0] for a in range(m)], PRIMES[0])
        print(f"  d_{u},{v} moved by one unit changes N3+N4 mod p0:", (a3 + a4) % PRIMES[0] != (N3 + N4) % PRIMES[0])
