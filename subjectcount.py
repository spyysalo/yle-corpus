#!/usr/bin/env python3

import sys
import json

from collections import Counter


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
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
        for subject in document['subjects']:
            id_, title = subject['id'], subject['title']['fi']
            count[(id_, title)] += 1
    return count
    

def main(argv):
    args = argparser().parse_args(argv[1:])
    count = Counter()
    for fn in args.file:
        count_subjects(fn, count, args)
    for (id_, title), total in count.items():
        print('{}\t{}\t{}'.format(total, id_, title))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
