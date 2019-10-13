#!/usr/bin/env python3

import sys
import json

from collections import Counter
from itertools import combinations


def pretty_dumps(data):
    return json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser() 
    ap.add_argument('-k', '--keep-overlaps', default=False, action='store_true',
                    help='keep documents matching multiple IDs')
    ap.add_argument('-o', '--output-dir', default=None,
                    help='output directory (default STDOUT)')
    ap.add_argument('ids', metavar='ID,ID[,ID...]')
    ap.add_argument('file', nargs='+', metavar='JSON')
    return ap


def filter_by_topics(data, fn, options):
    filtered = { 'data': [] }
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
        if not matches:
            continue
        if len(matches) > 1 and not options.keep_overlaps:
            continue
        # mark matched topics
        document['topics'] = []
        for id_, title in matches:
            document['topics'].append({ 'id': id_, 'title': title })
        filtered['data'].append(document)
    # copy metadata
    for k in data:
        if k != 'data':
            filtered[k] = data[k]
    return filtered
    

def main(argv):
    args = argparser().parse_args(argv[1:])
    args.ids = set(args.ids.split(','))
    for fn in args.file:
        with open(fn) as f:
            data = json.load(f)
        data = filter_by_topics(data, fn, args)
        if args.output_dir is None:
            print(pretty_dumps(data))
        else:
            raise NotImplementedError()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
