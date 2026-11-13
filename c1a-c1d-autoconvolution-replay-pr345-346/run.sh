#!/bin/sh
# Build the C checker, self-test both checkers against a naive sum, then replay both certificates.
set -e
cc -O3 -o src/conv src/conv.c -lpthread
python3 -I src/selftest.py
python3 -I src/replay.py data/c1d_upper_n163840_v2.json
python3 -I src/replay.py data/c1a_upper_n262144_v2.json
