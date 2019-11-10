# Yle corpus

Tools for working with the Yle corpus

Data source: http://urn.fi/urn:nbn:fi:lb-2017070501

Data license: https://korp.csc.fi/download/YLE/fi/LICENSE.txt

# Quickstart

The corpus licese does not permit redistribution. The balanced
ten-class version can be recreated from source as follows:

* Download data from http://urn.fi/urn:nbn:fi:lb-2017070501, save as `ylenews-fi-2011-2018-src.zip`

* Run `BUILD-DATA.sh`

(This takes a while.)

# Processing details

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
cat filtered/fi/201[6-8]/*/*.json | egrep -A 3 '"topics"' \
    | egrep -A 1 '"id": "('"$(echo $SUBJECTS | tr ',' '|')"')"' \
    | egrep '"title"' | sort | uniq -c | sort -rn
```

(Gives 10K+ for all 10 selected subjects for 2011-2015, 2K+ for all 2016-)

# Prepare data for selected subjects

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

## Create truncated versions of data

(Truncates lines to max 256 basic tokens, affects approx. 1/3 of examples)

mkdir trunc-data
for f in data/*.txt; do
    python3 scripts/truncate.py 256 "$f" > trunc-data/$(basename "$f")
done

## Create symlinks with consistent naming (for convenience)

```
for s in data trunc-data; do
    mkdir $s/{100,32,10,3,1}-percent
    for d in $s/{100,32,10,3,1}-percent; do
        ( 
            cd $d;
            ln -s ../yle-dev.txt dev.txt;
            ln -s ../yle-test.txt test.txt
        )
    done
    (cd $s/1-percent; ln -s ../yle-train-100.txt train.txt)
    (cd $s/3-percent; ln -s ../yle-train-316.txt train.txt)
    (cd $s/10-percent; ln -s ../yle-train-1000.txt train.txt)
    (cd $s/32-percent; ln -s ../yle-train-3162.txt train.txt)
    (cd $s/100-percent; ln -s ../yle-train.txt train.txt)
done
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

Defaults, 10% training data (~15%)

```
$FASTTEXT supervised -input data/yle-train-1000.txt -output yle.model
$FASTTEXT test yle.model.bin data/yle-dev.txt
```

More epochs and subwords, 10% training data (~65%)

```
$FASTTEXT supervised -input data/yle-train-1000.txt -output yle.model \
    -minn 3 -maxn 5 -epoch 25
$FASTTEXT test yle.model.bin data/yle-dev.txt
```

Defaults, 1% training data (~18%)

```
$FASTTEXT supervised -input data/yle-train-100.txt -output yle.model
$FASTTEXT test yle.model.bin data/yle-dev.txt
```

More epochs and subwords, 1% training data (~50%)

```
$FASTTEXT supervised -input data/yle-train-100.txt -output yle.model \
    -minn 3 -maxn 5 -epoch 25
$FASTTEXT test yle.model.bin data/yle-dev.txt
```
