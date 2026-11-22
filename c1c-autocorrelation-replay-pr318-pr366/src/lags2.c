/* Exact autocorrelation A_k = sum_i w_i w_{i+k}, k = 0..K, for non-negative
   integer weights, summed directly in unsigned 128-bit integers. Refuses input
   unless n * (max w)^2 < 2^127, so no sum can overflow. Zero runs at either end
   are skipped (they contribute nothing). Prints A_k in decimal, one per line. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
typedef unsigned __int128 u128;
static long n, K, lo, hi; static int T = 8;
static uint64_t *w; static u128 *A;
static void *work(void *arg) {
  long t = (long)arg;
  for (long k = t; k <= K; k += T) {
    u128 s = 0;
    for (long i = lo; i + k <= hi; i++) s += (u128)w[i] * w[i + k];
    A[k] = s;
  }
  return NULL;
}
static void pr(u128 x) {
  char s[50]; int p = 49; s[p] = 0;
  if (x == 0) s[--p] = '0';
  while (x) { s[--p] = '0' + (int)(x % 10); x /= 10; }
  fputs(s + p, stdout);
}
static int bits(u128 x) { int b = 0; while (x) { b++; x >>= 1; } return b; }
int main(int argc, char **argv) {
  if (argc > 1) T = atoi(argv[1]);
  if (scanf("%ld %ld", &K, &n) != 2 || n < 1) return 1;
  w = malloc(8 * n); uint64_t mx = 0;
  for (long i = 0; i < n; i++) {
    unsigned long long x; if (scanf("%llu", &x) != 1) return 2;
    w[i] = x; if (x > mx) mx = x;
  }
  if (bits((u128)mx * mx) + bits((u128)n) >= 127) { fprintf(stderr, "overflow risk\n"); return 3; }
  lo = 0; while (lo < n && w[lo] == 0) lo++;
  hi = n - 1; while (hi >= 0 && w[hi] == 0) hi--;
  A = calloc(K + 1, 16);
  pthread_t th[256]; if (T > 256) T = 256;
  for (long t = 0; t < T; t++) pthread_create(&th[t], NULL, work, (void *)t);
  for (int t = 0; t < T; t++) pthread_join(th[t], NULL);
  for (long k = 0; k <= K; k++) { pr(A[k]); putchar('\n'); }
  return 0;
}
