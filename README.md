# aiohttp-aiocache

[![Maintainability](https://api.codeclimate.com/v1/badges/4b6f49c9d1e4e1e9963d/maintainability)](https://codeclimate.com/github/nobbynobbs/aiohttp-aiocache/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/4b6f49c9d1e4e1e9963d/test_coverage)](https://codeclimate.com/github/nobbynobbs/aiohttp-aiocache/test_coverage)

Caching middleware for [aiohttp](https://github.com/aio-libs/aiohttp) server
with [aiocache](https://github.com/argaen/aiocache) under the hood.
Inspired by [aiohttp-cache](https://github.com/cr0hn/aiohttp-cache).

## Installation

```bash
pip install aiohttp-aiocache
```

or 

```bash
poetry add aiohttp-aiocache
```

Optional `aiocache` dependencies for redis, memcached and msgpack support
will not be installed. Install them manually if required.

## Usage
```python
import asyncio

import aiohttp.web as web
from aiocache import Cache
from aiocache.serializers import PickleSerializer

from aiohttp_aiocache import cached, register_cache


@cached  # mark handler with decorator
async def handler(_: web.Request) -> web.Response:
    await asyncio.sleep(1)
    return web.Response(text="Hello world")

app = web.Application()
app.router.add_route("GET", "/", handler)

# create aiocache instance
cache = Cache(
    Cache.MEMORY,
    serializer=PickleSerializer(),
    namespace="main",
    ttl=60,
)

# register cache backend in appplication
register_cache(app, cache)

web.run_app(app)
```

## Limitations

Support caching for GET requests only.

## License

MIT