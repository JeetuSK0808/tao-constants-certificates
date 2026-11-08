import sys, json, hashlib, subprocess, time
from fractions import Fraction
sys.path.insert(0, sys.argv[2])
from kron import all_lags
path = sys.argv[1]
raw = open(path, 'rb').read()
print('sha256', hashlib.sha256(raw).hexdigest())
d = json.loads(raw)
K, w = d['K'], d['weights_int']
n = len(w)
assert all(isinstance(x, int) and x >= 0 for x in w), 'weights must be non-negative integers'
print(f'K={K} n={n} max weight={max(w)} (2^56-8? {max(w)==2**56-8}) zero tail={sum(1 for x in w[-64:] if x==0)}/64')
S = sum(w)
def score(A):
    m = min(A); ks = [k for k, v in enumerate(A) if v == m]
    return Fraction(K * m, S * S), ks
t = time.time()
inp = f'{K} {n}\n' + ' '.join(map(str, w)) + '\n'
res = subprocess.run([sys.argv[2] + '/lags'], input=inp.encode(), capture_output=True, check=True).stdout.decode().split('\n')
A1 = []
for line in res[:K + 1]:
    aa, ab, bb = map(int, line.split())
    A1.append((aa << 56) + (ab << 28) + bb)
print(f'C direct: {time.time()-t:.1f}s')
t = time.time()
A2 = all_lags(w, K)
print(f'Kronecker: {time.time()-t:.1f}s')
assert len(A1) == len(A2) == K + 1
diff = sum(1 for x, y in zip(A1, A2) if x != y)
print('lags that differ between the two implementations:', diff)
assert max(A2).bit_length() < 136
F, ks = score(A1)
print('exact value', F.numerator, '/', F.denominator, '=', f'{F.numerator*10**20//F.denominator}e-20')
print('argmin lags', ks)
Fs = Fraction(int(d['score_num']), int(d['score_den']))
print('equals the certificate fraction:', F == Fs, '| reduced:', Fs.numerator == int(d['score_num']))
claim = Fraction(d['claim'])
print('implies claim', d['claim'], ':', F >= claim, '| one unit higher (', claim + Fraction(1, 10**10), ') implied:', F >= claim + Fraction(1, 10**10))
for name, v in [('#270 stated', Fraction(640823574552569898220412928, 1561614482809354047911104009)),
                ('#318 stated', Fraction(2582127846607416062611587072, 6292441470965870058830439361)),
                ('page best 0.4103333 [Kos2026]', Fraction(134648548624804778248790016, 328144294688458468928334649))]:
    print(f'  above {name}: {F > v} (by {float(F - v):.4e})')
# red controls
w2 = list(w); i = n // 3; w2[i] += 1
A3 = all_lags(w2, K)
S2 = sum(w2); m3 = min(A3)
print('control: one weight +1 changes the value:', Fraction(K * m3, S2 * S2) != F)
w3 = list(w); j = max(range(n), key=lambda t: w[t]); w3[j] = w3[j] * 101 // 100
A4 = all_lags(w3, K); S3 = sum(w3)
F3 = Fraction(K * min(A4), S3 * S3)
print('control: largest weight +1% changes the value:', F3 != F, '| still implies claim:', F3 >= claim)
