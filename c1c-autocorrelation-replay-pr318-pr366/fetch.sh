#!/bin/sh
# Fetch the certificates of teorth/optimizationproblems #318 and #366 at their pinned commits and check the hashes.
set -e
mkdir -p data
curl -fsSL -o data/pr318_certificate.json \
  https://raw.githubusercontent.com/Julsgaard/c1c-certificate/91e47b1aa03020fb4f9219ad16f2f8cfcec9cd1d/cert/certificate.json
curl -fsSL -o data/pr366_K98304_0.4103735.json \
  https://raw.githubusercontent.com/intervalplace/frontier/c0bcdfb7c36fa20db3d3e32ac13963d790e6a33c/c1c-barnard-steinerberger/K98304_0.4103735.json
shasum -a 256 -c SHA256SUMS.txt
