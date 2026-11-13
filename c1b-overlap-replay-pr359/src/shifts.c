/* Exact overlap sums for the Erdos minimum overlap step-function rule.
   Input (stdin): n D a_0 ... a_{n-1}, integers with 0 <= a_i <= D < 2^63.
   For every shift k in -(n-1)..(n-1) prints
     k  S_k   where S_k = sum over i with 0<=i<n, 0<=i+k<n of a_i * (D - a_{i+k}).
   Each product is < 2^126 only if D < 2^63; we also require n*D^2 < 2^127
   so every partial sum fits in unsigned __int128 (checked below). */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
typedef unsigned __int128 u128;
static long n; static uint64_t D, *a, *c; static u128 *S; static int T = 8;
static void *work(void *arg) {
  long t = (long)arg;
  for (long j = t; j < 2 * n - 1; j += T) {
    long k = j - (n - 1);
    long lo = k < 0 ? -k : 0, hi = k < 0 ? n : n - k;   /* i in [lo, hi) */
    u128 s = 0;
    for (long i = lo; i < hi; i++) s += (u128)a[i] * c[i + k];
    S[j] = s;
  }
  return NULL;
}
static void pr(u128 x) {
  char s[50]; int p = 49; s[p] = 0;
  if (x == 0) s[--p] = '0';
  while (x) { s[--p] = '0' + (int)(x % 10); x /= 10; }
  fputs(s + p, stdout);
}
int main(int argc, char **argv) {
  if (argc > 1) T = atoi(argv[1]);
  unsigned long long DD;
  if (scanf("%ld %llu", &n, &DD) != 2 || n < 1) return 1;
  D = DD;
  if (D >> 63) { fprintf(stderr, "D too large\n"); return 3; }
  /* n * D^2 < 2^127 ? */
  u128 D2 = (u128)D * D; if (D2 >> 126 || D2 > (((u128)1 << 127) / (u128)n)) { fprintf(stderr, "overflow risk\n"); return 4; }
  a = malloc(8 * n); c = malloc(8 * n); S = calloc(2 * n - 1, 16);
  for (long i = 0; i < n; i++) {
    unsigned long long w; if (scanf("%llu", &w) != 1) return 2;
    if (w > D) { fprintf(stderr, "a_%ld > D\n", i); return 5; }
    a[i] = w; c[i] = D - w;
  }
  pthread_t th[256]; if (T > 256) T = 256;
  for (long t = 0; t < T; t++) pthread_create(&th[t], NULL, work, (void *)t);
  for (int t = 0; t < T; t++) pthread_join(th[t], NULL);
  for (long j = 0; j < 2 * n - 1; j++) { printf("%ld ", j - (n - 1)); pr(S[j]); putchar('\n'); }
  return 0;
}
