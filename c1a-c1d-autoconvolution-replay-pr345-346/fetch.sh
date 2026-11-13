#!/bin/sh
# Fetch the certificates of teorth/optimizationproblems#346 (C_1a) and #345 (C_1d) at the pinned commit and check their hashes.
set -e
mkdir -p data
U=https://raw.githubusercontent.com/arhancanli/quantavane-replays/cc2c67deb49fb09bcdc1947d0ad0b6ee2b9106b5/improvements
curl -fsSL -o data/c1a_upper_n262144_v2.json $U/c1a/c1a_upper_n262144_v2.json
curl -fsSL -o data/c1d_upper_n163840_v2.json $U/c1d/c1d_upper_n163840_v2.json
cat > data/SHA256SUMS <<'SUMS'
cfbf05a1245394c910a54cafcbe692704332d5467d6466d58e0312444a82bff6  data/c1a_upper_n262144_v2.json
253d0ca68f060eedc6fd24e3afc6b1ce477cb6a97e25d80453e4616362153a82  data/c1d_upper_n163840_v2.json
SUMS
shasum -a 256 -c data/SHA256SUMS
