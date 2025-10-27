#!/usr/bin/env python3
"""
Write a measure_runtime coroutine that will execute
async_comprehension four times in parallel using asyncio.gather
"""
from importlib import import_module as a
import asyncio
import time


async_comprehension = a('1-async_comprehension').async_comprehension


async def measure_runtime() -> float:
    """
    execute async_comprehension 4x in parallel using asyncio.gather
    """
    start = time.time()
    await asyncio.gather(*(async_comprehension() for _ in range(4)))
    return time.time() - start
