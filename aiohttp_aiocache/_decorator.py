from typing import Callable, Any


def cached(handler: Callable[..., Any]) -> Callable[..., Any]:
    """decorator just add new attribute to request handler"""
    handler.cached = True  # type: ignore
    return handler
