from typing import Any

import aiohttp
import aiohttp.web as web
from aiocache import Cache
from aiocache.serializers import PickleSerializer

from aiohttp_aiocache import cache_middleware, cached


async def test_cache_middleware(aiohttp_client):
    """
    test if cache middleware works
    and doesn't prevent other middlewares from execution
    """

    handler_hits = 0
    before_cache_middleware_hits = 0
    after_cache_middleware_hits = 0

    @web.middleware
    async def before_cache_middleware(request: web.Request, handler: Any):
        nonlocal before_cache_middleware_hits
        before_cache_middleware_hits += 1
        return await handler(request)

    @web.middleware
    async def after_cache_middleware(request: web.Request, handler: Any):
        nonlocal after_cache_middleware_hits
        after_cache_middleware_hits += 1
        return await handler(request)

    @cached
    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application(middlewares=[
        before_cache_middleware, cache_middleware, after_cache_middleware
    ])
    app.router.add_route('GET', '/', handler)
    cache = Cache(
        Cache.MEMORY,
        serializer=PickleSerializer(),
        namespace="0",
        ttl=60,
    )
    app["cache"] = cache
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp: aiohttp.ClientResponse = await client.get("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200

    assert handler_hits == 1
    assert before_cache_middleware_hits == hits
    assert after_cache_middleware_hits == 1


async def test_middleware_bypass_not_decorated_handlers(aiohttp_client):
    """check if middleware doesn't affect excess handlers"""

    handler_hits = 0

    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application(middlewares=[cache_middleware])
    app.router.add_route('GET', '/', handler)
    app["cache"] = None
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp: aiohttp.ClientResponse = await client.get("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200

    assert handler_hits == hits


async def test_middleware_bypass_post_requests(aiohttp_client):
    handler_hits = 0

    @cached
    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application(middlewares=[cache_middleware])
    app.router.add_route('POST', '/', handler)
    app["cache"] = None  # must not be used
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp: aiohttp.ClientResponse = await client.post("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200

    assert handler_hits == hits


async def test_exception_in_cache_backend(aiohttp_client):
    """check if application still works if cache backend is misconfigured
    or cache backend doesn't work"""
    handler_hits = 0

    @cached
    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application(middlewares=[
        cache_middleware
    ])
    app.router.add_route('GET', '/', handler)
    cache = Cache(
        Cache.REDIS,
        endpoint="such.hostname.must.not.exist",
        serializer=PickleSerializer(),
        namespace="main",
        ttl=60,
    )
    app["cache"] = cache
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp: aiohttp.ClientResponse = await client.get("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200
    assert handler_hits == hits
