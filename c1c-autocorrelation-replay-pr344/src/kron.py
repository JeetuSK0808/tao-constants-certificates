"""All lags A_k = sum_i w_i w_{i+k} at once, by Kronecker substitution: pack the
weights into one integer with B-bit slots, multiply by the reversed packing, and
read A_k off slot n-1-k. Written independently of any other checker."""
def all_lags(w, K, B=136):
    n = len(w)
    P = 0
    for x in reversed(w):          # P = sum w_i 2^(B i)
        P = (P << B) | x
    R = 0
    for x in w:                    # R = sum w_i 2^(B (n-1-i))
        R = (R << B) | x
    Q = P * R
    nb = B // 8
    raw = Q.to_bytes((2 * n) * nb, 'little')
    out = []
    for k in range(K + 1):
        j = n - 1 - k
        out.append(int.from_bytes(raw[j * nb:(j + 1) * nb], 'little'))
    return out
