"""
Async helpers for Streamlit
"""
import asyncio
from typing import Any, Coroutine


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """
    Run async function in Streamlit context
    
    Args:
        coro: Coroutine to run
    
    Returns:
        Result of the coroutine
    """
    try:
        # Try to get running event loop
        loop = asyncio.get_running_loop()
        # If we are here, loop is running
        # Create a new event loop in a thread
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(asyncio.run, coro)
            return future.result()
    except RuntimeError:
        # No running event loop, create a new one
        return asyncio.run(coro)

