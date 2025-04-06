import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union, Callable
from functools import wraps, lru_cache
from concurrent.futures import ThreadPoolExecutor

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# Thread pool for CPU-bound tasks
thread_pool = ThreadPoolExecutor(max_workers=settings.MAX_WORKERS)


# Performance monitoring
class PerformanceMonitor:
    """
    Monitor and track performance metrics.
    """

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, name: str) -> None:
        """
        Start a timer for a specific operation.

        Args:
            name: Name of the operation
        """
        self.start_times[name] = time.time()

    def stop_timer(self, name: str) -> float:
        """
        Stop a timer and record the duration.

        Args:
            name: Name of the operation

        Returns:
            Duration in seconds
        """
        if name not in self.start_times:
            return 0

        duration = time.time() - self.start_times[name]

        if name not in self.metrics:
            self.metrics[name] = {
                "count": 0,
                "total_time": 0,
                "min_time": float("inf"),
                "max_time": 0,
            }

        self.metrics[name]["count"] += 1
        self.metrics[name]["total_time"] += duration
        self.metrics[name]["min_time"] = min(self.metrics[name]["min_time"], duration)
        self.metrics[name]["max_time"] = max(self.metrics[name]["max_time"], duration)

        del self.start_times[name]

        return duration

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all performance metrics.

        Returns:
            Dictionary of metrics
        """
        result = {}

        for name, data in self.metrics.items():
            result[name] = {
                "count": data["count"],
                "total_time": data["total_time"],
                "avg_time": data["total_time"] / data["count"]
                if data["count"] > 0
                else 0,
                "min_time": data["min_time"] if data["min_time"] != float("inf") else 0,
                "max_time": data["max_time"],
            }

        return result

    def reset_metrics(self) -> None:
        """
        Reset all metrics.
        """
        self.metrics = {}
        self.start_times = {}


# Create a global performance monitor
performance_monitor = PerformanceMonitor()


# Performance optimization decorators
def measure_performance(func):
    """
    Decorator to measure the performance of a function.

    Args:
        func: Function to measure

    Returns:
        Wrapped function
    """

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        operation_name = f"{func.__module__}.{func.__name__}"
        performance_monitor.start_timer(operation_name)

        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = performance_monitor.stop_timer(operation_name)
            logger.debug(f"Operation {operation_name} took {duration:.4f} seconds")

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        operation_name = f"{func.__module__}.{func.__name__}"
        performance_monitor.start_timer(operation_name)

        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = performance_monitor.stop_timer(operation_name)
            logger.debug(f"Operation {operation_name} took {duration:.4f} seconds")

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper


def run_in_threadpool(func):
    """
    Decorator to run a CPU-bound function in a thread pool.

    Args:
        func: Function to run in thread pool

    Returns:
        Wrapped function
    """

    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await asyncio.get_event_loop().run_in_executor(
            thread_pool, lambda: func(*args, **kwargs)
        )

    return wrapper


def cache_result(maxsize: int = 128, ttl: int = 300):
    """
    Decorator to cache the result of a function with a time-to-live.

    Args:
        maxsize: Maximum size of the cache
        ttl: Time-to-live in seconds

    Returns:
        Decorator function
    """
    cache = {}

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Create a cache key from the function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check if the result is in the cache and not expired
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return result

            # Call the function and cache the result
            result = await func(*args, **kwargs)
            cache[key] = (result, time.time())

            # Limit the cache size
            if len(cache) > maxsize:
                # Remove the oldest entry
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Create a cache key from the function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"

            # Check if the result is in the cache and not expired
            if key in cache:
                result, timestamp = cache[key]
                if time.time() - timestamp < ttl:
                    return result

            # Call the function and cache the result
            result = func(*args, **kwargs)
            cache[key] = (result, time.time())

            # Limit the cache size
            if len(cache) > maxsize:
                # Remove the oldest entry
                oldest_key = min(cache.keys(), key=lambda k: cache[k][1])
                del cache[oldest_key]

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Database optimization
def optimize_query(query, limit: Optional[int] = None, offset: Optional[int] = None):
    """
    Optimize a database query.

    Args:
        query: SQLAlchemy query
        limit: Maximum number of results
        offset: Offset for pagination

    Returns:
        Optimized query
    """
    # Add limit and offset if provided
    if limit is not None:
        query = query.limit(limit)

    if offset is not None:
        query = query.offset(offset)

    return query


# Code execution optimization
async def optimize_code_execution(code: str) -> str:
    """
    Optimize code for execution.

    Args:
        code: Code to optimize

    Returns:
        Optimized code
    """
    # Add imports for common libraries to avoid repeated imports
    optimized_code = """
# Common imports
import math
import json
import random
import datetime
import re
import collections
import itertools
import functools

# User code
"""

    # Add the user code
    optimized_code += code

    return optimized_code


# Memory optimization
class MemoryOptimizer:
    """
    Optimize memory usage.
    """

    @staticmethod
    def clear_cache():
        """
        Clear all caches.
        """
        # Clear LRU caches
        for name, obj in globals().items():
            if callable(obj) and hasattr(obj, "cache_clear"):
                obj.cache_clear()

        # Clear performance metrics
        performance_monitor.reset_metrics()

    @staticmethod
    def optimize_large_data(data: Any) -> Any:
        """
        Optimize large data structures.

        Args:
            data: Data to optimize

        Returns:
            Optimized data
        """
        if isinstance(data, list) and len(data) > 1000:
            # For large lists, return a generator instead
            return (item for item in data)

        if isinstance(data, dict) and len(data) > 1000:
            # For large dictionaries, return a view instead
            return data.items()

        return data


# Pagination utilities
def paginate_results(
    results: List[Any], page: int = 1, page_size: int = 20
) -> Dict[str, Any]:
    """
    Paginate a list of results.

    Args:
        results: List of results
        page: Page number (1-based)
        page_size: Number of items per page

    Returns:
        Paginated results
    """
    total_items = len(results)
    total_pages = (total_items + page_size - 1) // page_size

    # Ensure page is within bounds
    page = max(1, min(page, total_pages)) if total_pages > 0 else 1

    # Calculate start and end indices
    start_idx = (page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)

    # Get the items for the current page
    items = results[start_idx:end_idx]

    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "has_previous": page > 1,
        "has_next": page < total_pages,
    }


# Rate limiting
class RateLimiter:
    """
    Rate limiter for API endpoints.
    """

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        Initialize the rate limiter.

        Args:
            max_requests: Maximum number of requests allowed in the time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}

    def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed.

        Args:
            key: Key to identify the client (e.g., IP address or user ID)

        Returns:
            True if the request is allowed, False otherwise
        """
        current_time = time.time()

        # Remove expired requests
        self.requests = {
            k: v
            for k, v in self.requests.items()
            if current_time - v[-1] < self.time_window
        }

        # Get the requests for this key
        key_requests = self.requests.get(key, [])

        # Remove expired requests for this key
        key_requests = [t for t in key_requests if current_time - t < self.time_window]

        # Check if the number of requests exceeds the limit
        if len(key_requests) >= self.max_requests:
            return False

        # Add the current request
        key_requests.append(current_time)
        self.requests[key] = key_requests

        return True


# Create a global rate limiter
rate_limiter = RateLimiter()


# Timeout handling
class TimeoutError(Exception):
    """
    Exception raised when an operation times out.
    """

    pass


async def with_timeout(coro, timeout: float):
    """
    Run a coroutine with a timeout.

    Args:
        coro: Coroutine to run
        timeout: Timeout in seconds

    Returns:
        Result of the coroutine

    Raises:
        TimeoutError: If the operation times out
    """
    try:
        return await asyncio.wait_for(coro, timeout)
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")


# Performance metrics API
async def get_performance_metrics() -> Dict[str, Any]:
    """
    Get performance metrics.

    Returns:
        Dictionary of metrics
    """
    return performance_monitor.get_metrics()


async def reset_performance_metrics() -> None:
    """
    Reset performance metrics.
    """
    performance_monitor.reset_metrics()


# Optimize E2B session management
class E2BSessionManager:
    """
    Manager for E2B sessions.
    """

    def __init__(self, max_sessions: int = 10, session_timeout: int = 3600):
        """
        Initialize the session manager.

        Args:
            max_sessions: Maximum number of concurrent sessions
            session_timeout: Session timeout in seconds
        """
        self.max_sessions = max_sessions
        self.session_timeout = session_timeout
        self.sessions = {}
        self.last_used = {}

    async def get_session(self, session_id: str):
        """
        Get a session by ID.

        Args:
            session_id: Session ID

        Returns:
            Session object
        """
        # Check if the session exists
        if session_id not in self.sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found",
            )

        # Update the last used time
        self.last_used[session_id] = time.time()

        return self.sessions[session_id]

    async def create_session(self, session_id: str, session):
        """
        Create a new session.

        Args:
            session_id: Session ID
            session: Session object

        Returns:
            Session object
        """
        # Check if we need to clean up old sessions
        if len(self.sessions) >= self.max_sessions:
            await self._cleanup_old_sessions()

        # Create the session
        self.sessions[session_id] = session
        self.last_used[session_id] = time.time()

        return session

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session ID

        Returns:
            True if the session was deleted, False otherwise
        """
        if session_id in self.sessions:
            # Clean up the session
            session = self.sessions[session_id]
            await session.close()

            # Remove the session
            del self.sessions[session_id]
            del self.last_used[session_id]

            return True

        return False

    async def _cleanup_old_sessions(self) -> None:
        """
        Clean up old sessions.
        """
        current_time = time.time()

        # Find sessions that have timed out
        timed_out_sessions = [
            session_id
            for session_id, last_used in self.last_used.items()
            if current_time - last_used > self.session_timeout
        ]

        # Delete timed out sessions
        for session_id in timed_out_sessions:
            await self.delete_session(session_id)

        # If we still have too many sessions, delete the oldest ones
        if len(self.sessions) >= self.max_sessions:
            # Sort sessions by last used time
            sorted_sessions = sorted(self.last_used.items(), key=lambda x: x[1])

            # Delete the oldest sessions
            for session_id, _ in sorted_sessions[
                : len(self.sessions) - self.max_sessions + 1
            ]:
                await self.delete_session(session_id)


# Create a global E2B session manager
e2b_session_manager = E2BSessionManager()
