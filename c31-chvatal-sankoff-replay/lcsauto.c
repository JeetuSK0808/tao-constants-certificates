/* Independent replay of the C_31 (binary Chvatal-Sankoff) upper bounds of [J2026].
 *
 * Implements Lueker's automaton M_h (J. ACM 56(3), 2009, Sec. 3; semantics as in his published
 * programs at ics.uci.edu/~lueker/papers/lcs/code/upper/), written from scratch; no code from the
 * claimant's repository was read or used.
 *
 *   build  h table.bin         BFS over reachable non-null states, write successor table
 *   eigen  h table.bin w.txt v.bin maxit   power iteration (Lueker's stopping rule), save v
 *   cert   h table.bin w.txt v.bin          rounding-mode-free certificate: prints max ratio
 *
 * Table format per state s (in BFS order, states numbered from 0), for c = 0, 1:
 *   int8 lo, int8 hi, then (hi-lo+1) uint32 successor numbers (all non-null; checked).
 * w.txt: 2h-1 weights (pad = -(h-1) .. h-1) as hex doubles, each >= the exact weight.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int H;
static uint64_t MASK;

static inline uint64_t pack(uint64_t x, uint64_t y, uint64_t dx, uint64_t dy) {
    return (x << (3 * H)) | (y << (2 * H)) | (dx << H) | dy;
}

/* successor of state s on input T_{c,l}; returns 0 if the automaton rejects, else 1 */
static int step(uint64_t s, int c, int l, uint64_t *out) {
    enum { SENT = -100000 };
    int L[24][24], a[24], b[24];
    uint64_t x = (s >> (3 * H)) & MASK, y = (s >> (2 * H)) & MASK, dx = (s >> H) & MASK, dy = s & MASK;
    int n = 2 * H + 1;
    for (int i = 0; i < n; i++) for (int j = 0; j < n; j++) L[i][j] = SENT;
    for (int i = 1; i <= H; i++) { a[i] = (x >> (H - i)) & 1; b[i] = (y >> (H - i)) & 1; }
    L[H][H] = 1000;
    for (int i = H; i >= 1; i--) L[i - 1][H] = L[i][H] - (int)((dx >> (H - i)) & 1);
    for (int j = H; j >= 1; j--) L[H][j - 1] = L[H][j] - (int)((dy >> (H - j)) & 1);
    int al = H, bl = H;
    if (l > 0) for (int t = 0; t < l; t++) a[++al] = 1 - c;
    if (l < 0) for (int t = 0; t < -l; t++) b[++bl] = 1 - c;
    a[++al] = c; b[++bl] = c;
    for (int j = H + 1; j <= bl; j++) L[0][j] = L[0][j - 1];
    for (int i = H + 1; i <= al; i++) L[i][0] = L[i - 1][0];
    for (int i = 1; i <= al; i++)
        for (int j = 1; j <= bl; j++) {
            if (i <= H && j <= H) continue;
            int d = L[i - 1][j - 1], u = L[i - 1][j], w = L[i][j - 1];
            if (d == SENT || u == SENT || w == SENT) { fprintf(stderr, "read of unset entry\n"); exit(2); }
            L[i][j] = (a[i] == b[j]) ? d + 1 : (u > w ? u : w);
        }
    /* canonical backtrack from (al, bl) must reach (H, H) using exactly one match */
    int i = al, j = bl, m = 0, ok = 0;
    while (i >= H && j >= H) {
        if (L[i][j] == L[i - 1][j]) i--;
        else if (L[i][j] == L[i][j - 1]) j--;
        else if (L[i][j] == L[i - 1][j - 1] + 1) { i--; j--; m++; }
        else { fprintf(stderr, "inconsistent table\n"); exit(2); }
        if (i == H && j == H) { if (m != 1) { fprintf(stderr, "match count %d\n", m); exit(2); } ok = 1; break; }
    }
    if (!ok) return 0;
    uint64_t nx = 0, ny = 0, ndx = 0, ndy = 0;
    for (int t = al - H + 1; t <= al; t++) nx = (nx << 1) | a[t];
    for (int t = bl - H + 1; t <= bl; t++) ny = (ny << 1) | b[t];
    for (int t = al - H + 1; t <= al; t++) {
        int d = L[t][bl] - L[t - 1][bl];
        if (d != 0 && d != 1) { fprintf(stderr, "bad vertical difference %d\n", d); exit(2); }
        ndx = (ndx << 1) | d;
    }
    for (int t = bl - H + 1; t <= bl; t++) {
        int d = L[al][t] - L[al][t - 1];
        if (d != 0 && d != 1) { fprintf(stderr, "bad horizontal difference %d\n", d); exit(2); }
        ndy = (ndy << 1) | d;
    }
    if (nx >> (H - 1)) { nx = MASK - nx; ny = MASK - ny; }   /* complement symmetry */
    *out = pack(nx, ny, ndx, ndy);
    return 1;
}

/* ---- open-addressing hash: key+1 -> state number ---- */
static uint64_t *hk; static uint32_t *hv; static uint64_t hcap;
static inline uint64_t mix(uint64_t k) { k ^= k >> 33; k *= 0xff51afd7ed558ccdULL; k ^= k >> 33; k *= 0xc4ceb9fe1a85ec53ULL; k ^= k >> 33; return k; }
static uint64_t *states; static uint64_t nstates, maxstates;
static uint32_t find_or_add(uint64_t key) {
    uint64_t p = mix(key) & (hcap - 1);
    for (;;) {
        if (hk[p] == 0) {
            if (nstates >= maxstates) { fprintf(stderr, "too many states\n"); exit(3); }
            hk[p] = key + 1; hv[p] = (uint32_t)nstates; states[nstates] = key; return (uint32_t)nstates++;
        }
        if (hk[p] == key + 1) return hv[p];
        p = (p + 1) & (hcap - 1);
    }
}

/* Batch-parallel BFS: successor keys of a batch of queued states are computed by NTB threads,
 * then inserted sequentially in exactly the order of the sequential BFS (same numbering). */
#include <pthread.h>
#define NTB 4
#define BATCH (1 << 18)
static uint64_t *bkeys; static int8_t *bok; static uint64_t bstart, bcount;
static void *bwork(void *arg) {
    long t = (long)arg; int P = 2 * (2 * H - 1);
    for (uint64_t i = t; i < bcount; i += NTB) {
        uint64_t s = states[bstart + i];
        for (int c = 0; c < 2; c++) for (int l = -(H - 1); l <= H - 1; l++) {
            int k = c * (2 * H - 1) + (l + H - 1);
            bok[i * P + k] = (int8_t)step(s, c, l, &bkeys[i * P + k]);
        }
    }
    return NULL;
}
static int build(const char *path) {
    hcap = (uint64_t)1 << (H <= 8 ? 24 : H == 9 ? 27 : 30);
    maxstates = H <= 9 ? ((uint64_t)1 << 27) : 700000000ULL;
    hk = calloc(hcap, 8); hv = malloc(hcap * 4); states = malloc(maxstates * 8);
    int P = 2 * (2 * H - 1);
    bkeys = malloc((size_t)BATCH * P * 8); bok = malloc((size_t)BATCH * P);
    if (!hk || !hv || !states || !bkeys || !bok) { fprintf(stderr, "oom\n"); return 1; }
    FILE *f = fopen(path, "wb"); setvbuf(f, NULL, _IOFBF, 1 << 24);
    find_or_add(pack(0, 0, MASK, MASK));
    uint64_t ntrans = 0, q = 0, nextlog = 1 << 24;
    while (q < nstates) {
        bstart = q; bcount = nstates - q; if (bcount > BATCH) bcount = BATCH;
        pthread_t th[NTB];
        for (long t = 0; t < NTB; t++) pthread_create(&th[t], NULL, bwork, (void *)t);
        for (int t = 0; t < NTB; t++) pthread_join(th[t], NULL);
        for (uint64_t i = 0; i < bcount; i++) {
            for (int c = 0; c < 2; c++) {
                uint32_t succ[24]; int lo = 99, hi = -99;
                for (int l = -(H - 1); l <= H - 1; l++) {
                    int k = c * (2 * H - 1) + (l + H - 1);
                    if (bok[i * P + k]) { succ[l + H] = find_or_add(bkeys[i * P + k]); if (l < lo) lo = l; if (l > hi) hi = l; }
                }
                if (lo > hi) { fprintf(stderr, "state with no successor\n"); return 1; }
                for (int l = lo; l <= hi; l++) if (!bok[i * P + c * (2 * H - 1) + (l + H - 1)]) { fprintf(stderr, "padding set not an interval\n"); return 1; }
                int8_t b2[2] = { (int8_t)lo, (int8_t)hi }; fwrite(b2, 1, 2, f);
                fwrite(&succ[lo + H], 4, hi - lo + 1, f); ntrans += hi - lo + 1;
            }
        }
        q += bcount;
        if (q >= nextlog) { fprintf(stderr, "  processed %llu, discovered %llu\n", (unsigned long long)q, (unsigned long long)nstates); nextlog += 1 << 24; }
    }
    fclose(f);
    printf("h=%d states=%llu transitions=%llu\n", H, (unsigned long long)nstates, (unsigned long long)ntrans);
    return 0;
}

static double W[24];
static void read_weights(const char *p) {
    FILE *f = fopen(p, "r");
    for (int l = -(H - 1); l <= H - 1; l++) if (fscanf(f, "%la", &W[l + H]) != 1) { fprintf(stderr, "weights\n"); exit(1); }
    fclose(f);
}

/* ---- table access: mmap + per-thread state ranges ---- */
#include <pthread.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#define NT 4
static const uint8_t *TB; static size_t TBLEN;
static uint64_t NST; static uint64_t RS[NT + 1]; static size_t RO[NT + 1];

static void map_table(const char *path) {
    int fd = open(path, O_RDONLY); struct stat st; fstat(fd, &st); TBLEN = st.st_size;
    TB = mmap(NULL, TBLEN, PROT_READ, MAP_PRIVATE, fd, 0);
    if (TB == MAP_FAILED) { perror("mmap"); exit(1); }
    madvise((void *)TB, TBLEN, MADV_SEQUENTIAL);
    size_t o = 0; uint64_t n = 0;
    while (o < TBLEN) { for (int c = 0; c < 2; c++) { int8_t lo = (int8_t)TB[o], hi = (int8_t)TB[o + 1]; o += 2 + 4 * (size_t)(hi - lo + 1); } n++; }
    if (o != TBLEN) { fprintf(stderr, "table length mismatch\n"); exit(1); }
    NST = n;
    o = 0; n = 0; int k = 1; RS[0] = 0; RO[0] = 0;
    while (o < TBLEN) {
        if (k < NT && n == NST * k / NT) { RS[k] = n; RO[k] = o; k++; }
        for (int c = 0; c < 2; c++) { int8_t lo = (int8_t)TB[o], hi = (int8_t)TB[o + 1]; o += 2 + 4 * (size_t)(hi - lo + 1); }
        n++;
    }
    while (k <= NT) { RS[k] = NST; RO[k] = TBLEN; k++; }
}

/* vectors are stored as float32 (any positive vector gives a valid certificate); sums are in double */
typedef struct { int t; const float *v; float *vn; double mx, mn, vm; } Job;
static void *work(void *arg) {
    Job *J = arg; size_t o = RO[J->t]; double mx = 0, mn = INFINITY, vm = 0;
    for (uint64_t s = RS[J->t]; s < RS[J->t + 1]; s++) {
        double sum = 0;
        for (int c = 0; c < 2; c++) {
            int lo = (int8_t)TB[o], hi = (int8_t)TB[o + 1]; o += 2;
            for (int l = lo; l <= hi; l++) { uint32_t q; memcpy(&q, TB + o, 4); o += 4; sum += W[l + H] * (double)J->v[q]; }
        }
        J->vn[s] = (float)sum;
        double r = sum / (double)J->v[s];
        if (r > mx) mx = r; if (r < mn) mn = r; if (sum > vm) vm = sum;
    }
    J->mx = mx; J->mn = mn; J->vm = vm; return NULL;
}
static void apply(const float *v, float *vn, double *rmax, double *rmin, double *vmax) {
    pthread_t th[NT]; Job J[NT];
    for (int t = 0; t < NT; t++) { J[t].t = t; J[t].v = v; J[t].vn = vn; pthread_create(&th[t], NULL, work, &J[t]); }
    double mx = 0, mn = INFINITY, vm = 0;
    for (int t = 0; t < NT; t++) { pthread_join(th[t], NULL); if (J[t].mx > mx) mx = J[t].mx; if (J[t].mn < mn) mn = J[t].mn; if (J[t].vm > vm) vm = J[t].vm; }
    *rmax = mx; *rmin = mn; *vmax = vm;
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: see header\n"); return 1; }
    H = atoi(argv[2]); MASK = ((uint64_t)1 << H) - 1;
    if (!strcmp(argv[1], "build")) return build(argv[3]);
    map_table(argv[3]);
    uint64_t n = NST;
    read_weights(argv[4]);
    float *v = malloc(n * 4), *vn = malloc(n * 4);
    if (!strcmp(argv[1], "eigen")) {
        /* eigen h table w v.f32 maxit [target_lambda [resume.f32]]: stops at Lueker's rule, or as soon as the
         * max ratio is <= target (the next iterate's max ratio is no larger, by Collatz-Wielandt monotonicity) */
        int maxit = atoi(argv[6]);
        double target = argc > 7 ? atof(argv[7]) : 0;
        if (argc > 8) { FILE *ri = fopen(argv[8], "rb"); if (!ri || fread(v, 4, n, ri) != n) { fprintf(stderr, "resume\n"); return 1; } fclose(ri); }
        else for (uint64_t s = 0; s < n; s++) v[s] = 1.0f;
        double rmax = 0, rmin = 0, vmax;
        char tmp[1024]; snprintf(tmp, sizeof tmp, "%s.tmp", argv[5]);
        for (int it = 1; it <= maxit; it++) {
            apply(v, vn, &rmax, &rmin, &vmax);
            for (uint64_t s = 0; s < n; s++) v[s] = (float)((double)vn[s] / vmax);
            int done = (rmax / rmin <= 1 + 1e-10) || (target > 0 && rmax <= target);
            fprintf(stderr, "it=%d ratio in [%.15f, %.15f]\n", it, rmin, rmax);
            if (it % 10 == 0 || done) { FILE *o = fopen(tmp, "wb"); fwrite(v, 4, n, o); fclose(o); rename(tmp, argv[5]); }
            if (done) break;
        }
        printf("states=%llu lambda_est=%.15f\n", (unsigned long long)n, rmax);
        return 0;
    }
    if (!strcmp(argv[1], "cert")) {
        FILE *vi = fopen(argv[5], "rb"); if (fread(v, 4, n, vi) != n) { fprintf(stderr, "v\n"); return 1; } fclose(vi);
        for (uint64_t s = 0; s < n; s++) if (!(v[s] > 0) || !isfinite(v[s])) { fprintf(stderr, "v not positive\n"); return 1; }
        double rmax, rmin, vmax;
        apply(v, vn, &rmax, &rmin, &vmax);
        /* round-to-nearest; at most 2(2h-1) products+sums and one division per state, so
         * true ratio <= rmax * (1 - 2^-53)^-(4h+1); applied exactly in certify.py */
        printf("states=%llu maxratio_rn=%a (%.17g) ops=%d\n", (unsigned long long)n, rmax, rmax, 4 * H + 1);
        return 0;
    }
    return 1;
}
