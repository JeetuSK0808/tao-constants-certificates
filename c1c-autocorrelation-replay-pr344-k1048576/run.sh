#!/bin/sh
# Build the C checker, self-test both checkers against a naive sum, then replay the certificate.
set -e
cc -O3 -o src/lags2 src/lags2.c -lpthread
python3 -I src/selftest.py
python3 -I src/replay.py data/c1c_lower_K1048576.json
