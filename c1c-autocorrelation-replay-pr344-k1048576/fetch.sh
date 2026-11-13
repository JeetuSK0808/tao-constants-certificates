#!/bin/sh
# Fetch the current certificate of teorth/optimizationproblems#344 (K = 2^20) at the pinned commit and check its hash.
set -e
mkdir -p data
curl -fsSL -o data/c1c_lower_K1048576.json \
  https://raw.githubusercontent.com/arhancanli/quantavane-replays/101c945bed626dd60ab86e1d449a420478a89d4c/improvements/c1c/c1c_lower_K1048576.json
echo "fc69d772d8dbd7ddbaab994e44164bed1b9eeca3cfb6d972732d677226362352  data/c1c_lower_K1048576.json" | shasum -a 256 -c -
