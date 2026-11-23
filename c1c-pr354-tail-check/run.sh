#!/bin/sh
set -e
python3 -I src/g_at.py data/pwcert.json | tee results/output.txt
