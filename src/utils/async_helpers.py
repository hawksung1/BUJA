"""
Async helpers for Streamlit
"""
import asyncio
from typing import Coroutine, Any


def run_async(coro: Coroutine[Any, Any, Any]) -> Any:
    """
    Run async function in Streamlit context
    
    Args:
        coro: Coroutine to run
    
    Returns:
        Result of the coroutine
    """
    try:
        # Try to get existing event loop
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, we can't use run_until_complete
            # Create a new event loop in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, coro)
                return future.result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(coro)

