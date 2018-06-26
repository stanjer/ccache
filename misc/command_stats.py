#!/usr/bin/env python

import os
import pprint
from collections import Counter
try:
    from text_histogram import histogram
except ImportError:
    histogram = None

CCACHE_DIR = os.getenv('CCACHE_DIR') or \
             os.path.join(os.getenv('HOME'), '.ccache')

compilers = []
commands = []
inputs = []
outputs = []

for root, dirs, files in os.walk(CCACHE_DIR):
    for file in files:
        base, ext = os.path.splitext(file)
        if ext != '.command':
            continue
        path = os.path.join(root, file)
        command, input, output = open(path).readlines()

        compiler, args = command.split(' ', 1)
        compilers.append(compiler)
        commands.append(command.strip())
        inputs.append(input.strip())
        outputs.append(output.strip())

print "Compilers:"
pprint.pprint(Counter(compilers).most_common())
print "Top Ten Inputs:"
counter_inputs = Counter(inputs)
pprint.pprint(counter_inputs.most_common(10))
if histogram:
    histogram(counter_inputs.values(), 0, len(commands))
print "Top Ten Outputs:"
counter_outputs = Counter(outputs)
pprint.pprint(counter_outputs.most_common(10))
if histogram:
    histogram(counter_outputs.values(), 0, len(commands))
