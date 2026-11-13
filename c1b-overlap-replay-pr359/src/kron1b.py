"""All overlap sums S_k = sum_i a_i (D - a_{i+k}), k = -(n-1)..(n-1), from ONE
big-integer product (Kronecker substitution). Shares no code with shifts.c.

A(x) = sum_i a_i x^i, C(x) = sum_j (D - a_j) x^(n-1-j). The coefficient of
x^(n-1-k) in A*C is S_k. Each coefficient is < n*D^2, so with slots of SLOT
bits (2^SLOT > n*D^2) the coefficients can be read back from the product's bytes."""


def all_shifts(a, D):
    n = len(a)
    bound = n * D * D
    slot = 8 * ((bound.bit_length() + 8) // 8)   # whole bytes, at least one spare byte
    w = slot // 8
    A = int.from_bytes(b"".join(x.to_bytes(w, "little") for x in a), "little")
    C = int.from_bytes(b"".join((D - x).to_bytes(w, "little") for x in reversed(a)), "little")
    P = (A * C).to_bytes((2 * n - 1) * w + w, "little")
    coef = [int.from_bytes(P[m * w:(m + 1) * w], "little") for m in range(2 * n - 1)]
    # coef[m] = S_{n-1-m}; return a dict k -> S_k
    return {n - 1 - m: coef[m] for m in range(2 * n - 1)}, slot


def naive(a, D):
    n = len(a)
    return {k: sum(a[i] * (D - a[i + k]) for i in range(n) if 0 <= i + k < n) for k in range(-(n - 1), n)}
