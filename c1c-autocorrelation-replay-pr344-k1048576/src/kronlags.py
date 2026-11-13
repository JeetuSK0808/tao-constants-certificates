"""All lags A_k = sum_i w_i w_{i+k}, k = 0..K, from ONE big-integer product
(Kronecker substitution, slots joined as bytes). Shares no code with lags2.c."""


def all_lags(w, K):
    n = len(w)
    bound = n * max(w) ** 2
    nb = (bound.bit_length() + 8) // 8 + 1
    P = int.from_bytes(b"".join(x.to_bytes(nb, "little") for x in w), "little")            # sum w_i X^i
    R = int.from_bytes(b"".join(x.to_bytes(nb, "little") for x in reversed(w)), "little")  # sum w_i X^(n-1-i)
    raw = (P * R).to_bytes(2 * n * nb, "little")
    # coefficient of X^(n-1-k) in P*R is sum_i w_i w_{i+k}
    return [int.from_bytes(raw[(n - 1 - k) * nb:(n - k) * nb], "little") for k in range(K + 1)], 8 * nb


def naive(w, K):
    n = len(w)
    return [sum(w[i] * w[i + k] for i in range(n - k)) if k < n else 0 for k in range(K + 1)]
