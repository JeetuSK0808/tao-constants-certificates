#!/bin/sh
# Build the C checker, self-test both checkers against a naive sum, then replay the certificate.
set -e
cc -O3 -o src/shifts src/shifts.c -lpthread
python3 -I src/selftest.py
python3 -I src/replay.py data/c1b_upper_n114688.json
