#!/bin/sh
# Build the C checker, self-test both checkers against a naive sum, then replay the certificate.
set -e
cc -O3 -o src/lags src/lags.c
python3 -I src/selftest.py src
python3 -I src/replay.py data/c1c_lower_K98304.json src
