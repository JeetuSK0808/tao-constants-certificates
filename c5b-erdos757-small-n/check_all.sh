#!/bin/sh
# Re-check every small-n certificate with the independent checker and compare with the
# Henning-Yeo lower bound f(n) >= n - floor((8n-6)/17) (Ma-Tang's argument, valid for n >= 2).
cd "$(dirname "$0")"
for f in $(ls certificates/n*.txt | sort -V); do
  n=$(basename "$f" .txt | tr -d n)
  out=$(python3 verify.py "$f")
  ok=$(echo "$out" | grep -c "PASS")
  h=$(echo "$out" | sed -n 's/^largest Sidon subset h(A) = \([0-9]*\).*/\1/p')
  lo=$(( n - (8*n-6)/17 ))
  if [ "$ok" = 1 ] && [ "$h" = "$lo" ]; then s="f($n) = $h (exact)"; else s="f($n) <= $h, >= $lo"; fi
  echo "n=$n  (4,5): $([ "$ok" = 1 ] && echo PASS || echo FAIL)  h=$h  HY lower=$lo  ->  $s"
done
