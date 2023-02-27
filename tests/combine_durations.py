#!/usr/bin/env python
# Copyright (C) 2012 Anaconda, Inc
# SPDX-License-Identifier: BSD-3-Clause
"""
Script to combine test durations from all runs.

If the tests splits are looking uneven or the test suite has
siginificantly changed, update .test_durations in the root of the
repository and pytest-split may work better.

`gh run list -b <interesting branch>`
`mkdir tests-data; cd tests-data` # will be filled with many artifacts
`gh run download <number of tests CI run>`
`python combine_durations.py`

Then copy `combined_durations.json`.
"""

import json
from pathlib import Path

count = 0
combined = {}
for path in Path(".").glob("*/.test_durations"):
    data = json.loads(path.read_text())
    for key in data:
        if key in combined:
            existing = combined[key]
        else:
            existing = data[key]
        combined[key] = (existing + data[key]) / 2.0
    count += 1

print(f"Read {count} .test_durations")

Path("combined_durations.json").write_text(json.dumps(combined, indent=4, sort_keys=True))