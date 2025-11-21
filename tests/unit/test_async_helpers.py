import asyncio

import pytest

from src.utils.async_helpers import run_async


def test_run_async_no_loop():
    """When no event loop is running, run_async should execute the coroutine and return its result."""
    async def sample():
        return 42
    result = run_async(sample())
    assert result == 42

@pytest.mark.asyncio
async def test_run_async_with_running_loop():
    """When an event loop is already running, run_async should execute the coroutine in a thread and return its result."""
    async def sample():
        await asyncio.sleep(0.01)
        return "async-result"
    # Inside an async test, there is a running loop.
    result = run_async(sample())
    assert result == "async-result"
