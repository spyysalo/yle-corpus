#!/usr/bin/env python3

import sys
import json

from collections import Counter
from itertools import combinations


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser() 
    ap.add_argument('ids', metavar='ID,ID[,ID...]')
    ap.add_argument('file', nargs='+', metavar='JSON')
    return ap


def count_subjects(fn, count, options):
    with open(fn) as f:
        data = json.load(f)
    for document in data['data']:
        if 'subjects' not in document:
            print('no subjects for {}, skipping ...'.format(document['id']),
                  file=sys.stderr)
            continue
        matches = []
        for subject in document['subjects']:
            id_, title = subject['id'], subject['title']['fi']
            if id_ in options.ids:
                matches.append((id_, title))
        for m1, m2 in combinations(sorted(matches), 2):
            count[(m1, m2)] += 1
    return count
    

def main(argv):
    args = argparser().parse_args(argv[1:])
    args.ids = set(args.ids.split(','))
    count = Counter()
    for fn in args.file:
        count_subjects(fn, count, args)
    for (m1, m2), total in count.items():
        (id1, title1), (id2, title2) = m1, m2
        print('{}\t{}\t{}\t{}\t{}'.format(total, id1, title1, id2, title2))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
