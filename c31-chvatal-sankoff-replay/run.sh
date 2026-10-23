#!/bin/zsh
# usage: run.sh h z [target_lambda [resume.f32]]   (build, power iteration, certificate, bound)
set -e
h=$1; z=$2; cd "$(dirname $0)"; mkdir -p data
[ -f data/t$h.bin ] || ./lcsauto build $h data/t$h.bin > data/build$h.txt 2> data/build$h.log
python3 certify.py weights $h $z data/w$h.txt
./lcsauto eigen $h data/t$h.bin data/w$h.txt data/v$h.f32 100000 ${3:-0} ${4:-} 2>> data/eig$h.log > data/eigout$h.txt
./lcsauto cert $h data/t$h.bin data/w$h.txt data/v$h.f32 > data/cert$h.txt
python3 certify.py bound $h $z $(sed -E 's/.*maxratio_rn=([^ ]+).*/\1/' data/cert$h.txt) $(sed -E 's/.*ops=([0-9]+).*/\1/' data/cert$h.txt) > data/bound$h.txt
cat data/build$h.txt data/cert$h.txt data/bound$h.txt
