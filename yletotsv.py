#!/usr/bin/env python3

import sys
import json


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('-T', '--topics', default=False, action='store_true',
                    help='output topics instead of subjects')
    ap.add_argument('-t', '--text-labels', default=False, action='store_true',
                    help='output text labels (NOTE: non-unique)')
    ap.add_argument('file', nargs='+', metavar='JSON')
    return ap


def get_labels(document, options):
    if not options.topics:
        if 'subjects' not in document:
            return []
        else:
            data = document['subjects']
    else:
        if 'topics' not in document:
            return []
        else:
            data = document['topics']
    labels = []
    for d in data:
        if not options.text_labels:
            labels.append(d['id'])
        elif 'title' not in d:
            print('missing title for {}, skipping'.format(['id']),
                  file=sys.stderr)
        elif isinstance(d['title'], str):
            labels.append(d['title'].replace(' ', '_'))            
        elif d['title'].get('fi', None) is None:
            print('missing title.fi for {}, skipping'.format(d['id']),
                  file=sys.stderr)
        else:
            labels.append(d['title']['fi'].replace(' ', '_'))
    return labels


def get_content(document, options):
    if 'content' not in document:
        return []
    content = []
    for c in document['content']:
        if c['type'] in ('heading', 'text'):
            content.append(c['text'])
    return content


def normalize_space(text):
    return ' '.join(text.split())


def convert_to_tsv(fn, options):
    with open(fn) as f:
        data = json.load(f)
    for document in data['data']:
        if 'id' not in document:
            print('missing id for document, skipping...', file=sys.stderr)
            continue
        id_ = document['id']
        labels = get_labels(document, options)
        if not labels:
            print('no labels for {}, skipping ...'.format(id_),
                  file=sys.stderr)
            continue
        content = get_content(document, options)
        if not content:
            print('no content for {}, skipping ...'.format(id_),
                  file=sys.stderr)
            continue        
        print('{}\t{}\t{}'.format(id_, ' '.join(labels),
                                  normalize_space(' '.join(content))))


def main(argv):
    args = argparser().parse_args(argv[1:])
    for fn in args.file:
        convert_to_tsv(fn, args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
