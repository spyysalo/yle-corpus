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
        try:
            print(l, end='')
        except BrokenPipeError:
            break    # `head` etc. are OK
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
