#!/usr/bin/env python3

import sys
import json


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('file', nargs='+', metavar='JSON')
    return ap


def get_subjects(fn, options):
    with open(fn) as f:
        data = json.load(f)
    for document in data['data']:
        if 'subjects' not in document:
            print('no subjects for {}, skipping ...'.format(document['id']),
                  file=sys.stderr)
            continue
        for subject in document['subjects']:
            print('{}\t{}'.format(subject['id'], subject['title']['fi']))
    

def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        get_subjects(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
