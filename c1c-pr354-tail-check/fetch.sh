#!/bin/sh
# Downloads only the certificate JSON of #354 (SeanSagait/c1c-autocorrelation-certificate @ 308005a40a6d) and checks its hash.
set -e
mkdir -p data
curl -sSL -o data/pwcert.json https://raw.githubusercontent.com/SeanSagait/c1c-autocorrelation-certificate/308005a40a6d/pwcert_p20_dps40_S120.json
echo "8aa13b614c8a4751dca0a2dde7ad556b09d9b9f225e824b0774ee22d7518340f  data/pwcert.json" | shasum -a 256 -c
