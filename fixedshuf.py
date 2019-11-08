#!/usr/bin/env python3

# Minimal python implementation of shuf with fixed seed.

import sys
import fileinput
import random


SEED = 0


def main(argv):
    lines = []
    for l in fileinput.input(argv[1:]):
        lines.append(l)
    random.Random(SEED).shuffle(lines)
    for l in lines:
        # Pipeline workarounds for https://bugs.python.org/issue24864
        try:
            print(l, end='')
        except (BrokenPipeError, ValueError):
            try:
                sys.stdout.close()
            except:
                pass
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
