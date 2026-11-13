"""Exact autoconvolution c_m = sum_{i+j=m} v_i v_j of signed integers from ONE
big-integer squaring (Kronecker substitution). Shares no code with conv.c.

Shift to non-negative u_i = v_i + C (C = 0 if all v_i >= 0, else C = -min v).
Then (u*u)_m = c_m + 2C W_m + C^2 N_m, where W_m = sum of v_i over the window
i in [max(0, m-n+1), min(m, n-1)] and N_m is the window size."""


def autoconv(v):
    n = len(v)
    C = max(0, -min(v))
    u = [x + C for x in v]
    top = max(u)
    bound = n * top * top
    w = (bound.bit_length() + 8) // 8 + 1          # bytes per slot, with spare room
    U = int.from_bytes(b"".join(x.to_bytes(w, "little") for x in u), "little")
    P = (U * U).to_bytes((2 * n) * w, "little")
    uu = [int.from_bytes(P[m * w:(m + 1) * w], "little") for m in range(2 * n - 1)]
    if C == 0:
        return uu, 8 * w
    pre = [0]
    for x in v:
        pre.append(pre[-1] + x)
    out = []
    for m in range(2 * n - 1):
        lo, hi = max(0, m - n + 1), min(m, n - 1)
        W = pre[hi + 1] - pre[lo]
        out.append(uu[m] - 2 * C * W - C * C * (hi - lo + 1))
    return out, 8 * w


def naive(v):
    n = len(v)
    return [sum(v[i] * v[m - i] for i in range(max(0, m - n + 1), min(m, n - 1) + 1)) for m in range(2 * n - 1)]
