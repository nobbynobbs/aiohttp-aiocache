from _sha256 import sha256
from typing import List

from aiohttp import web


def make_key(request: web.Request) -> str:
    key_parts: List[str] = [
        request.method,
        request.rel_url.path_qs,
        request.url.host,
        request.content_type,
    ]
    key = "#".join(part for part in key_parts)
    key = sha256(key.encode()).hexdigest()
    return key
