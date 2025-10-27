#!/usr/bin/env python3
"""
Type function with list of different types
"""
from typing import List, Union


def sum_mixed_list(mxd_lst: List[Union[int, float]]) -> float:
    """
    returns float sum from list of int and float
    """
    return sum(mxd_lst)
