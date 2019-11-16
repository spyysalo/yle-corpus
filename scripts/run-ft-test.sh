#!/bin/bash

# fastText experiments

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

set -euo pipefail

REPETITIONS=10

FASTTEXT="$HOME/git_checkout/fastText/fasttext"

DATADIR="$SCRIPTDIR/../data"

WORDVECDIR="$SCRIPTDIR/../wordvecs"

TESTSET="$DATADIR/yle-test.txt"

declare -a TRAINSETS=(
    "$DATADIR/1-percent/train.txt"
    "$DATADIR/3-percent/train.txt"
    "$DATADIR/10-percent/train.txt"
    "$DATADIR/32-percent/train.txt"
    "$DATADIR/100-percent/train.txt"
)

declare -a PARAMS=(
    "-minn 3 -maxn 7 -epoch 25"
)

wordvecs="$WORDVECDIR/fasttext-wiki.fi.vec"

for i in $(seq $REPETITIONS); do
    for params in "${PARAMS[@]}"; do
	for wv in $wordvecs; do
	    if [ -z "$wv" ]; then
		wvparams=""   # no pretrained wordvecs
		shortwv=""
	    else
		dim=$(head -n 1 "$wv" | cut -d ' ' -f 2)
		wvparams="-pretrainedVectors $wv -dim $dim"
		shortwv="-pretrainedVectors $(basename $wv) -dim $dim"
	    fi
	    for trainset in "${TRAINSETS[@]}"; do
		model=$(mktemp)
		train=$(basename $(dirname "$trainset"))
		echo "Train on $train, params $params $shortwv (round $i)" >&2
		$FASTTEXT supervised \
			  -verbose 1 \
			  $params \
			  $wvparams \
			  -input "$trainset" \
			  -output "$model"
		test=$(basename "$TESTSET")
		echo "Test on $test, trained $train, params $params $shortwv"\
		     " (round $i)" >&2
		p=$($FASTTEXT test "$model.bin" "$TESTSET" \
			   | egrep 'P@1' | cut -f 2)
		echo "$train"$'\t'"$params"$'\t'"$shortwv"$'\t'"$p"
		rm -rf "$model.bin" "$model.vec"
	    done
	done
    done
done
