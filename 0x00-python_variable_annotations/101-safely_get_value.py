#!/usr/bin/env python3
"""
Add type annotations to parameters
"""
from typing import Mapping, Any, Union, TypeVar


T = TypeVar('T')
Def = Union[T, None]
Ret = Union[Any, T]


def safely_get_value(dct: Mapping, key: Any, default: Def) -> Ret:
    """
    return type annotations
    """
    if key in dct:
        return dct[key]
    else:
        return default
