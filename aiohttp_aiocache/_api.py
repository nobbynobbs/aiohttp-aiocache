from typing import Callable, Any

import aiocache.base
from aiohttp import web

from aiohttp_aiocache._middleware import cache_middleware, CACHE_INSTANCE_KEY


def cached(handler: Callable[..., Any]) -> Callable[..., Any]:
    """decorator just add new attribute to request handler"""
    handler.cache_with_aiocache = True  # type: ignore
    return handler


def register_cache(
        app: web.Application,
        cache: aiocache.base.BaseCache
) -> None:
    app.middlewares.append(cache_middleware)
    app[CACHE_INSTANCE_KEY] = cache
