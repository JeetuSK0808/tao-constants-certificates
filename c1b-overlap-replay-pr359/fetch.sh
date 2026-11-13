#!/bin/sh
# Fetch the certificate of teorth/optimizationproblems#359 at the pinned commit and check its hash.
set -e
mkdir -p data
curl -fsSL -o data/c1b_upper_n114688.json \
  https://raw.githubusercontent.com/arhancanli/quantavane-replays/b47cbc4553a1d4ef4225794cfe6622c58e942756/improvements/c1b/c1b_upper_n114688.json
echo "e285b485a1f8f28e86bd3a906effbe930f968b553de6044f501d2bf92f5a9ca5  data/c1b_upper_n114688.json" | shasum -a 256 -c -
