#!/bin/sh
# Needs numpy. About 21 minutes on 4 threads (Apple M5 Pro); see results/output.txt.
set -e
python3 -I -u src/split_k4.py ../c89-k4-ramsey-multiplicity/c89_stepgraphon_D20.json.gz data/c89_7680_delta_D20.npz --controls | tee results/output.txt
