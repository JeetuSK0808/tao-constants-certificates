/* Exact autocorrelation A_k = sum_i w_i w_{i+k}, k = 0..K, for non-negative
   integer weights w_i < 2^56. Each weight is split as w = a*2^28 + b, so every
   partial product is < 2^56 and each partial sum fits easily in __int128.
   Prints, per lag, the three partial sums aa, ab+ba, bb in decimal. */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <pthread.h>
typedef unsigned __int128 u128;
static int n, K, T = 6;
static uint64_t *a, *b;
static u128 *AA, *AB, *BB;
static void *work(void *arg) {
  long t = (long)arg;
  for (int k = t; k <= K; k += T) {
    u128 aa = 0, ab = 0, bb = 0;
    for (int i = 0; i + k < n; i++) {
      aa += (u128)(a[i] * a[i + k]);
      ab += (u128)(a[i] * b[i + k]) + (u128)(b[i] * a[i + k]);
      bb += (u128)(b[i] * b[i + k]);
    }
    AA[k] = aa; AB[k] = ab; BB[k] = bb;
  }
  return NULL;
}
static void pr(u128 x) {
  char s[50]; int p = 49; s[p] = 0;
  if (x == 0) s[--p] = '0';
  while (x) { s[--p] = '0' + (int)(x % 10); x /= 10; }
  fputs(s + p, stdout);
}
int main(void) {
  if (scanf("%d %d", &K, &n) != 2) return 1;
  a = malloc(8 * n); b = malloc(8 * n);
  for (int i = 0; i < n; i++) {
    unsigned long long w; if (scanf("%llu", &w) != 1) return 2;
    if (w >> 56) { fprintf(stderr, "weight %d too large\n", i); return 3; }
    a[i] = w >> 28; b[i] = w & ((1ULL << 28) - 1);
  }
  AA = calloc(K + 1, 16); AB = calloc(K + 1, 16); BB = calloc(K + 1, 16);
  pthread_t th[64];
  for (long t = 0; t < T; t++) pthread_create(&th[t], NULL, work, (void *)t);
  for (int t = 0; t < T; t++) pthread_join(th[t], NULL);
  for (int k = 0; k <= K; k++) { pr(AA[k]); putchar(' '); pr(AB[k]); putchar(' '); pr(BB[k]); putchar('\n'); }
  return 0;
}
