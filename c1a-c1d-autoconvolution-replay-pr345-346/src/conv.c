/* Exact autoconvolution c_m = sum_{i+j=m} v_i v_j, m = 0..2n-2, for signed
   integers |v_i| <= 2^56. Each v is split as v = a*2^28 + b with
   a = floor(v / 2^28) (|a| <= 2^28) and 0 <= b < 2^28, so every partial product
   fits in int64 and each partial sum (at most n <= 2^20 terms) fits in int128.
   Prints, per m: m AA AB BB with c_m = AA*2^56 + AB*2^28 + BB. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
typedef __int128 i128;
static long n; static int T = 8;
static int64_t *a, *b; static i128 *AA, *AB, *BB;
static void *work(void *arg) {
  long t = (long)arg;
  for (long m = t; m <= 2 * n - 2; m += T) {
    long lo = m - (n - 1) > 0 ? m - (n - 1) : 0;
    i128 aa = 0, ab = 0, bb = 0;
    long i = lo;
    for (; 2 * i < m; i++) {            /* pairs i < j = m - i, counted twice */
      long j = m - i;
      aa += (i128)(a[i] * a[j]);
      ab += (i128)(a[i] * b[j]) + (i128)(b[i] * a[j]);
      bb += (i128)(b[i] * b[j]);
    }
    aa *= 2; ab *= 2; bb *= 2;
    if (2 * i == m) {                   /* diagonal i = j */
      aa += (i128)(a[i] * a[i]); ab += 2 * (i128)(a[i] * b[i]); bb += (i128)(b[i] * b[i]);
    }
    AA[m] = aa; AB[m] = ab; BB[m] = bb;
  }
  return NULL;
}
static void pr(i128 x) {
  char s[60]; int p = 59; s[p] = 0; int neg = x < 0;
  unsigned __int128 u = neg ? -(unsigned __int128)x : (unsigned __int128)x;
  if (u == 0) s[--p] = '0';
  while (u) { s[--p] = '0' + (int)(u % 10); u /= 10; }
  if (neg) s[--p] = '-';
  fputs(s + p, stdout);
}
int main(int argc, char **argv) {
  if (argc > 1) T = atoi(argv[1]);
  if (scanf("%ld", &n) != 1 || n < 1 || n > (1L << 20)) return 1;
  a = malloc(8 * n); b = malloc(8 * n);
  for (long i = 0; i < n; i++) {
    long long v; if (scanf("%lld", &v) != 1) return 2;
    if (v > (1LL << 56) || v < -(1LL << 56)) { fprintf(stderr, "|v_%ld| > 2^56\n", i); return 3; }
    a[i] = v >> 28;                      /* arithmetic shift = floor division */
    b[i] = v - a[i] * (1LL << 28);       /* 0 <= b < 2^28 */
  }
  AA = calloc(2 * n - 1, 16); AB = calloc(2 * n - 1, 16); BB = calloc(2 * n - 1, 16);
  pthread_t th[256]; if (T > 256) T = 256;
  for (long t = 0; t < T; t++) pthread_create(&th[t], NULL, work, (void *)t);
  for (int t = 0; t < T; t++) pthread_join(th[t], NULL);
  for (long m = 0; m <= 2 * n - 2; m++) {
    printf("%ld ", m); pr(AA[m]); putchar(' '); pr(AB[m]); putchar(' '); pr(BB[m]); putchar('\n');
  }
  return 0;
}
