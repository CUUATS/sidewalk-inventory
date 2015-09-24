"""
Utilities for the Sidewalk Inventory and Assessment.
"""

import sys
from math import floor


def display_progress(iterable, label, label_length=20, bar_length=50,
                     bar_character='#'):
    """
    Display a progress bar while iterating over the iterable.
    """

    pct = None
    total = len(iterable)
    for i, item in enumerate(iterable, start=1):
        yield item
        new_pct = int(floor(100*float(i)/total))
        if new_pct != pct:
            pct = new_pct
            chars = int(floor(bar_length*float(pct)/100))
            bar_text = '\r{label: <{llen}} [{bar: <{blen}}] {pct}%'.format(
                label=label, llen=label_length, bar=bar_character * chars,
                blen=bar_length, pct=pct)
            sys.stdout.write(bar_text)
            sys.stdout.flush()
    sys.stdout.write('\n')
