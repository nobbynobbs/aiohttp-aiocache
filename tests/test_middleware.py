from typing import Any, Awaitable, Callable

import aiohttp
import aiohttp.web as web
from aiocache import Cache
from aiocache.serializers import PickleSerializer
from aiohttp.test_utils import TestClient

from aiohttp_aiocache import cached, register_cache

TestClientFixture = Callable[[web.Application], Awaitable[TestClient]]


async def test_cache_middleware(aiohttp_client: TestClientFixture) -> None:
    """
    test if cache middleware works
    and doesn't prevent other middlewares from execution
    """

    handler_hits = 0
    before_cache_middleware_hits = 0
    after_cache_middleware_hits = 0

    @web.middleware
    async def before_cache_middleware(
            request: web.Request, handler: Any
    ) -> web.Response:
        nonlocal before_cache_middleware_hits
        before_cache_middleware_hits += 1
        return await handler(request)

    @web.middleware
    async def after_cache_middleware(
            request: web.Request,
            handler: Any
    ) -> web.Response:
        nonlocal after_cache_middleware_hits
        after_cache_middleware_hits += 1
        return await handler(request)

    @cached
    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application(middlewares=[before_cache_middleware])
    app.router.add_route('GET', '/', handler)
    cache = Cache(
        Cache.MEMORY,
        serializer=PickleSerializer(),
        namespace="0",
        ttl=60,
    )
    register_cache(app, cache)

    # it's artificial case
    app.middlewares.append(after_cache_middleware)
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp: aiohttp.ClientResponse = await client.get("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200

    assert handler_hits == 1
    assert after_cache_middleware_hits == 1
    assert before_cache_middleware_hits == hits


async def test_middleware_bypass_not_decorated_handlers(
        aiohttp_client: TestClientFixture
) -> None:
    """check if middleware doesn't affect excess handlers"""

    handler_hits = 0

    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application()
    app.router.add_route('GET', '/', handler)
    register_cache(app, None)
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp: aiohttp.ClientResponse = await client.get("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200

    assert handler_hits == hits


async def test_middleware_bypass_post_requests(
        aiohttp_client: TestClientFixture
) -> None:
    handler_hits = 0

    @cached
    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application()
    app.router.add_route('POST', '/', handler)
    register_cache(app, None)  # must not be used
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp: aiohttp.ClientResponse = await client.post("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200

    assert handler_hits == hits


async def test_exception_in_cache_backend(
        aiohttp_client: TestClientFixture
) -> None:
    """check if application still works if cache backend is misconfigured
    or cache backend doesn't work"""
    handler_hits = 0

    @cached
    async def handler(_: web.Request) -> web.Response:
        nonlocal handler_hits
        handler_hits += 1
        return web.Response(body=b"Hello world")

    app = web.Application()
    app.router.add_route('GET', '/', handler)
    cache = Cache(
        Cache.REDIS,
        endpoint="such.hostname.must.not.exist",
        serializer=PickleSerializer(),
        namespace="main",
        ttl=60,
    )
    register_cache(app, cache)
    client = await aiohttp_client(app)

    hits = 10
    for i in range(hits):
        resp = await client.get("/")
        assert await resp.read() == b"Hello world"
        assert resp.status == 200
    assert handler_hits == hits
