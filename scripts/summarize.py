#!/usr/bin/env python3

import sys
import numpy as np

from collections import defaultdict


def main(argv):
    if len(argv) != 2:
        print('Usage: summarize.py RESULTS', file=sys.stderr)
        return 1
    results_by_params = defaultdict(list)
    param_order = []
    with open(argv[1]) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip()
            fields = l.split('\t')
            params, result = '\t'.join(fields[:-1]), float(fields[-1])
            results_by_params[params].append(result)
            if params not in param_order:
                param_order.append(params)
    for params in param_order:
        results = results_by_params[params]
        print('{}\t{:.2%}\tstd {:.2%}\t({} values)'.format(
            params, np.mean(results), np.std(results), len(results)))
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
