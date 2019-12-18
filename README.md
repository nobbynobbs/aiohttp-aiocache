# aiohttp-aiocache

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

## Usage
```python
import asyncio

import aiohttp.web as web
from aiocache import Cache
from aiocache.serializers import PickleSerializer

from aiohttp_aiocache import cache_middleware, cached

@cached
async def handler(_: web.Request) -> web.Response:
    await asyncio.sleep(1)
    return web.Response(body=b"Hello world")

# it's your responsibility to put cache_middleware into the right place among
# the other middlewares
app = web.Application(middlewares=[cache_middleware])
app.router.add_route('GET', '/', handler)
cache = Cache(
    Cache.MEMORY,
    serializer=PickleSerializer(),
    namespace="main",
    ttl=60,
)
app["cache"] = cache

web.run_app(app)
```


## License

MIT