# Yle-corpus

Tools for working with the Yle corpus

Data source: http://urn.fi/urn:nbn:fi:lb-2017070501

Data license: https://korp.csc.fi/download/YLE/fi/LICENSE.txt

# Processing

## Download and unpack source data

Download data from http://urn.fi/urn:nbn:fi:lb-2017070501, save as `ylenews-fi-2011-2018-src.zip`

```
unzip ylenews-fi-2011-2018-src.zip
```

## Select subjects (labels)

Get subject counts

```
python3 subjectcount.py ylenews-fi-2011-2018-src/data/fi/*/*/*.json \
    > subject_counts.tsv
```

(manually select subjects)

Filter to selected subjects, remove overlaps

```
SUBJECTS=18-220090,18-204933,18-220306,18-208149,18-218480,18-215452,18-209306,18-217206,18-91232,18-35286
for f in ylenews-fi-2011-2018-src/data/fi/*/*/*.json; do
    d=$(dirname $f); d=filtered/${d#ylenews-fi-2011-2018-src/data/}
    mkdir -p $d
    python3 filterbytopic.py $SUBJECTS $f > $d/$(basename $f)
done
```

Get counts for filtered

```
python3 subjectcount.py filtered/fi/*/*/*.json > filtered_subject_counts.tsv
```

Counts for selected subjects for filtered

```
sort -rn filtered_subject_counts.tsv \
    | egrep $'\t'$(echo $SUBJECTS | tr ',' '|')$'\t'
```

Counts by year

```
cat filtered/fi/201[1-5]/*/*.json | egrep -A 3 '"topics"' \
    | egrep -A 1 '"id": "('"$(echo $SUBJECTS | tr ',' '|')"')"' \
    | egrep '"title"' | sort | uniq -c | sort -rn
```

(Gives 10K+ for all 10 selected subjects for 2011-2015, 2K+ for all 2016-)

# Prepare data for seleced subjects

Split by subject

```
for s in $(echo $SUBJECTS | tr ',' ' '); do
    for f in filtered/fi/*/*/*.json; do
        d=$(dirname $f); d=split/$s/${d#filtered/}
        mkdir -p $d
        python3 filterbytopic.py $s $f > $d/$(basename $f)
    done
done
```

Extract to TSV and separate by year

```
mkdir extracted
for d in split/*; do
    python3 yletotsv.py -t -T $d/fi/201[1-5]/*/*.json \
        > extracted/early-$(basename $d).tsv
    python3 yletotsv.py -t -T $d/fi/201[6-8]/*/*.json \
        > extracted/late-$(basename $d).tsv
done
```

Split late into train and dev

```
for f in extracted/late-18-*.tsv; do
    b=$(basename $f .tsv); s=${b#late-}
    t=$(cat $f | wc -l)
    head -n $((t/2)) $f > extracted/dev-$s.tsv
    tail -n $((t-t/2)) $f > extracted/test-$s.tsv
done
```

Sample

```
mkdir sampled
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
```

Combine, format for fasttext

```
mkdir data
for t in train dev test; do
    cat sampled/${t}-*.tsv | python3 fixedshuf.py | cut -f 2- \
        | perl -pe 's/^/__label__/' \
        | perl -pe 's/\t/ /' > data/yle-${t}.txt
done
```

## Create subsets of training data

```
for n in 3162 1000 316 100; do
    mkdir sampled-${n}
    for f in extracted/early-*; do
	b=$(basename $f .tsv); s=${b#*-}
	python3 fixedshuf.py $f | head -n $n > sampled-${n}/train-$s.tsv
    done
    cat sampled-${n}/train-*.tsv | python3 fixedshuf.py | cut -f 2- \
        | perl -pe 's/^/__label__/; s/\t/ /' > data/yle-train-${n}.txt
done
```

## Store checksums

```
md5sum data/*.txt > checksums.md5
```

## Experiments

Setup

```
export FASTTEXT=PATH_TO_FASTTEXT
```

Defaults (expect ~87%)

```
$FASTTEXT supervised -input data/yle-train.txt -output yle.model
$FASTTEXT test yle.model.bin data/yle-dev.txt
```

With more epochs and subwords (~92%)

```
$FASTTEXT supervised -input data/yle-train.txt -output yle.model \
    -minn 3 -maxn 5 -epoch 25
$FASTTEXT test yle.model.bin data/yle-dev.txt
```

Defaults, 10% training data (~16%)

```
$FASTTEXT supervised -input data/yle-train-1000.txt -output yle.model
$FASTTEXT test yle.model.bin data/yle-dev.txt
```

More epochs and subwords, 10% training data (66%)

```
$FASTTEXT supervised -input data/yle-train-1000.txt -output yle.model \
    -minn 3 -maxn 5 -epoch 25
$FASTTEXT test yle.model.bin data/yle-dev.txt
```

Defaults, 1% training data (~17%)

```
$FASTTEXT supervised -input data/yle-train-100.txt -output yle.model
$FASTTEXT test yle.model.bin data/yle-dev.txt
```

More epochs and subwords, 1% training data (45%)

```
$FASTTEXT supervised -input data/yle-train-100.txt -output yle.model \
    -minn 3 -maxn 5 -epoch 25
$FASTTEXT test yle.model.bin data/yle-dev.txt
```
