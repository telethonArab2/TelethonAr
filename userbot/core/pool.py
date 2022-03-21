import asyncio
from concurrent.futures import Future, ThreadPoolExecutor
from functools import partial, wraps
from typing import Any, Callable

from motor.frameworks.asyncio import _EXECUTOR

from .logger import logging

_LOG = logging.getLogger(__name__)
_LOG_STR = " %s "


def submit_thread(func: Callable[[Any], Any], *args: Any, **kwargs: Any) -> Future:
    """إرسال الموضوع إلى تجمع"""
    return _EXECUTOR.submit(func, *args, **kwargs)


def run_in_thread(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """تشغيل في موضوع"""

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_EXECUTOR, partial(func, *args, **kwargs))

    return wrapper


def _get() -> ThreadPoolExecutor:
    return _EXECUTOR


def _stop():
    _EXECUTOR.shutdown()
    # pylint: disable=protected-access
    _LOG.info(_LOG_STR, f" تم تنصيب جميع مكاتب تليثون العربي : {_EXECUTOR._max_workers} ")


# pylint: disable=protected-access
_LOG.info(_LOG_STR, f" تم تنصيب جميع مكاتب تليثون العربي : {_EXECUTOR._max_workers} ")
