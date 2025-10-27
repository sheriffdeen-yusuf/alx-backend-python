#!/usr/bin/env python3
"""
Annotate the function parameters
"""
from typing import Iterable, Sequence, List, Tuple


def element_length(lst: Iterable[Sequence]) -> List[Tuple[Sequence, int]]:
    """
    returns appropirate types
    """
    return [(i, len(i)) for i in lst]
