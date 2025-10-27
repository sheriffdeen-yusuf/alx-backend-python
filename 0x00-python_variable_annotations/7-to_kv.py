#!/usr/bin/env python3
"""
Type function taking a str and int of float to return tuple
"""
from typing import Union, Tuple


def to_kv(k: str, v: Union[int, float]) -> Tuple[str, float]:
    """
    returns a tuple
    """
    return (k, v*v)
