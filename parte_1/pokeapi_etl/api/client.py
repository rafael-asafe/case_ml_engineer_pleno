import time
import uuid

import hishel
import hishel.httpx
import httpx
from httpx_retries import Retry, RetryTransport

from utils.logger import logger

retry = Retry(total=5, backoff_factor=0.5)

retry_transport = RetryTransport(retry=retry)

transport = hishel.httpx.SyncCacheTransport(
    next_transport=retry_transport,
    storage=hishel.SyncSqliteStorage(),
)


def before_request(request: httpx.Request):
    request_id = str(uuid.uuid4())
    request.headers["X-Requests-ID"] = request_id
    request.extensions["request_id"] = request_id
    request.extensions["start_time"] = time.monotonic()


def after_request(response: httpx.Response):
    request = response.request
    start = response.request.extensions.get("start_time", None)
    if start:
        elapsed = time.monotonic() - start
    else:
        elapsed = None

    logger.info(
        f"<pokeapi - extract> {request.method} {request.url} {response.status_code} "
        f"{elapsed} {request.extensions.get('request_id')}"
    )


client = httpx.Client(
    event_hooks={"request": [before_request], "response": [after_request]},
    transport=transport,
    base_url="https://pokeapi.co/api/v2/",
)

async_client = httpx.AsyncClient(
    event_hooks={"request": [before_request], "response": [after_request]},
    transport=transport,
    base_url="https://pokeapi.co/api/v2/",
)
