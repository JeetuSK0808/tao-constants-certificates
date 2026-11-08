import sys, random, subprocess
sys.path.insert(0, sys.argv[1]); from kron import all_lags
random.seed(7)
for trial in range(40):
    n = random.randint(1, 300); K = random.randint(0, n - 1)
    top = random.choice([2**8, 2**40, 2**56 - 1])
    w = [random.choice([0, top - 1, random.randrange(top)]) for _ in range(n)]
    naive = [sum(w[i] * w[i + k] for i in range(n - k)) for k in range(K + 1)]
    out = subprocess.run([sys.argv[1] + '/lags'], input=f'{K} {n}\n{" ".join(map(str,w))}\n'.encode(), capture_output=True, check=True).stdout.decode().split()
    c = [(int(out[3*k]) << 56) + (int(out[3*k+1]) << 28) + int(out[3*k+2]) for k in range(K + 1)]
    assert c == naive, ('C', trial); assert all_lags(w, K) == naive, ('kron', trial)
print('selftest: 40 random cases (weights up to 2^56-1), C direct and Kronecker both equal the naive sum at every lag')
