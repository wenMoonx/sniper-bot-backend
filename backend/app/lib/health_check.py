from math import ceil

from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute

from app.lib.errors import HTTPError
from starlette.status import HTTP_429_TOO_MANY_REQUESTS


def ensure_unique_route_names(app: FastAPI) -> None:
    """
    Check if route name is unique

    :param app:
    :return:
    """
    temp_routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name in temp_routes:
                raise ValueError(f'Non-unique route name: {route.name}')
            temp_routes.add(route.name)


async def http_limit_callback(request: Request, response: Response, expire: int):
    """
    Default callback function when requesting limits

    :param request:
    :param response:
    :param expire: milliseconds remaining
    :return:
    """
    expires = ceil(expire / 1000)
    raise HTTPError(code=HTTP_429_TOO_MANY_REQUESTS, msg='The request is too frequent, please try again later.', headers={'Retry-After': str(expires)})
