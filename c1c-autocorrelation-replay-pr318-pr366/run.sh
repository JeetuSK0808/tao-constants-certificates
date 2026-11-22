#!/bin/sh
# Build the C checker, self-test both checkers against a naive sum, then replay both certificates.
# The stated fractions are the ones printed in the two pull requests' rows of constants/1c.md.
set -e
cc -O3 -o src/lags2 src/lags2.c -lpthread
python3 -I src/selftest.py
echo "== #318 [J2026]"
python3 -I src/replay_step.py data/pr318_certificate.json \
  2582127846607416062611587072/6292441470965870058830439361 0.4103538918
echo "== #366 [Esc2026]"
python3 -I src/replay_step.py data/pr366_K98304_0.4103735.json \
  1376728953781146098572851250003968/3354819039892156766926073767410361 0.4103735
