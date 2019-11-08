#!/bin/bash

# Rebuild Yle corpus data from ylenews-fi-2011-2018-src.zip

set -euo pipefail

if [ ! -e "ylenews-fi-2011-2018-src.zip" ]; then
    echo "ylenews-fi-2011-2018-src.zip not found, download from
    http://urn.fi/urn:nbn:fi:lb-2017070501"
    exit 1
fi

echo "Checking md5sum for ylenews-fi-2011-2018-src.zip"
md5sum -c ylenews-fi-2011-2018-src.zip.md5 

if [ -e "ylenews-fi-2011-2018-src" ]; then
    echo "ylenews-fi-2011-2018-src exists, skipping unzip"
else
    unzip "ylenews-fi-2011-2018-src.zip"
fi

SUBJECTS=18-220090,18-204933,18-220306,18-208149,18-218480,18-215452,18-209306,18-217206,18-91232,18-35286
echo "Filtering to $SUBJECTS"
for f in ylenews-fi-2011-2018-src/data/fi/*/*/*.json; do
    d=$(dirname $f); d=filtered/${d#ylenews-fi-2011-2018-src/data/}
    mkdir -p $d
    python3 filterbytopic.py $SUBJECTS $f > $d/$(basename $f)
done

for s in $(echo $SUBJECTS | tr ',' ' '); do
    echo "Filtering to $s"
    for f in filtered/fi/*/*/*.json; do
        d=$(dirname $f); d=split/$s/${d#filtered/}
        mkdir -p $d
        python3 filterbytopic.py $s $f > $d/$(basename $f)
    done
done

echo "Extracting TSV"
mkdir -p extracted
for d in split/*; do
    python3 yletotsv.py -t -T $d/fi/201[1-5]/*/*.json \
        > extracted/early-$(basename $d).tsv
    python3 yletotsv.py -t -T $d/fi/201[6-8]/*/*.json \
        > extracted/late-$(basename $d).tsv
done

echo "Splitting dev and test"
for f in extracted/late-18-*.tsv; do
    b=$(basename $f .tsv); s=${b#late-}
    t=$(cat $f | wc -l)
    head -n $((t/2)) $f > extracted/dev-$s.tsv
    tail -n $((t-t/2)) $f > extracted/test-$s.tsv
done

echo "Sampling"
mkdir -p sampled
for f in extracted/early-*; do
    b=$(basename $f .tsv); s=${b#*-}
    python3 fixedshuf.py $f | head -n 10000 > sampled/train-$s.tsv
done
for t in dev test; do
    for f in extracted/${t}-*; do
        b=$(basename $f .tsv); s=${b#$*-}
        python3 fixedshuf.py $f | head -n 1000 > sampled/$s.tsv
    done
done

echo "Combining"
for t in train dev test; do
    cat sampled/${t}-*.tsv | python3 fixedshuf.py | cut -f 2- \
        | perl -pe 's/^/__label__/' \
        | perl -pe 's/\t/ /' > data/yle-${t}.txt
done

echo "Creating subsets"
for n in 3162 1000 316 100; do
    mkdir -p sampled-${n}
    for f in extracted/early-*; do
	b=$(basename $f .tsv); s=${b#*-}
	python3 fixedshuf.py $f | head -n $n > sampled-${n}/train-$s.tsv
    done
    cat sampled-${n}/train-*.tsv | python3 fixedshuf.py | cut -f 2- \
        | perl -pe 's/^/__label__/; s/\t/ /' > data/yle-train-${n}.txt
done

echo "Validating checksums"
md5sum -c checksums.md5

echo "DONE."
