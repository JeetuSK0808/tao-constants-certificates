#!/bin/sh
# Fetch the certificate of teorth/optimizationproblems#344 at the pinned commit and check its hash.
set -e
mkdir -p data
curl -fsSL -o data/c1c_lower_K98304.json \
  https://raw.githubusercontent.com/arhancanli/quantavane-replays/c40060ff2d03ed022d970ef25047e70c23a54ad3/improvements/c1c/c1c_lower_K98304.json
echo "17c7640aa37dab9fab0f8fd438b881319d7a2b527eec918da0a84ecdc3919d35  data/c1c_lower_K98304.json" | shasum -a 256 -c -
