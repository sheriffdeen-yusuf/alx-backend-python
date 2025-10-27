#!/usr/bin/env python3
"""
Type function with the callable type
"""
from typing import Callable


def make_multiplier(multiplier: float) -> Callable[[float], float]:
    """
    returns float multiplied by multiplier
    """
    return lambda x: x * multiplier
