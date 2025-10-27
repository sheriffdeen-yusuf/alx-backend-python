#!/usr/bin/env python3
"""
Write coroutine called async_comprehension that takes no arguments
"""
from typing import List
from importlib import import_module as a


async_generator = a('0-async_generator').async_generator


async def async_comprehension() -> List[float]:
    """
    Create 10 numbers list from a 10 number list generator
    """
    return [num async for num in async_generator()]
