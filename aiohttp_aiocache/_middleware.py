import logging
from typing import Any

from aiohttp import web
from aiocache.base import BaseCache

from ._utils import make_key


CACHE_INSTANCE_KEY = "aiohttp-aiocache-backend"

_logger = logging.getLogger("aiohttp-aiocache")


@web.middleware
async def cache_middleware(request: web.Request, handler: Any) -> web.Response:
    """caching middleware implementation"""

    if request.method != "GET":
        _logger.warning("only GET method available for caching")
        return await handler(request)

    # here we check attribute from real request handler,
    # but after using handler from argument for fetching response
    # thus we're respecting all the other middlewares... likely
    # I've wrote quite detailed test, so I'm almost sure it works as expected
    real_handler = request.match_info.handler
    if getattr(real_handler, "cache_with_aiocache", None) is None:
        return await handler(request)

    cache: BaseCache = request.app[CACHE_INSTANCE_KEY]

    key = make_key(request)
    try:
        resp: web.Response = await cache.get(key)
    except Exception:  # noqa
        _logger.error("cache reading error, check if cache backend is ok")
    else:
        if resp is not None:
            return resp

    resp = await handler(request)

    try:
        await cache.add(key, resp)
    except Exception:  # noqa
        _logger.error("cache writing error, check if cache backend is ok")

    return resp
