#!/bin/sh
# Downloads only the witness of #380 (sunil123456897/lean-dag-rsi @ 477024cffe4b) and checks its hash.
# The base step graphon is [SK2026], already in this repository (../c89-k4-ramsey-multiplicity).
set -e
mkdir -p data
curl -sSL -o data/c89_7680_delta_D20.npz https://raw.githubusercontent.com/sunil123456897/lean-dag-rsi/477024cffe4b2e28c6b310e879e38617d969f3ef/c89_certificate_package/c89_7680_delta_D20.npz
echo "44c6ba584681d8c9214c764d581d14f7e42a9815cbb3d0b05345bd742757ae2f  data/c89_7680_delta_D20.npz" | shasum -a 256 -c
echo "82c28f7761f8392df6ed1728b5eefdc4ef388b266fc2beb1a2f0a54f7dd2631a  ../c89-k4-ramsey-multiplicity/c89_stepgraphon_D20.json.gz" | shasum -a 256 -c
