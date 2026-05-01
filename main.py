import asyncio
from contextlib import suppress
import hashlib
import inspect
import logging
import random
import threading
import time

from fastapi import FastAPI, HTTPException, Request

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("app")

app = FastAPI()

total_requests = 0
total_errors = 0
total_latency_ms = 0.0
metrics_lock = threading.Lock()
maintenance_task = None

MONITOR_INTERVAL_SECONDS = 0.1
EVENT_LOOP_BLOCKED_THRESHOLD_MS = 200.0
SLOW_REQUEST_THRESHOLD_MS = 1000.0
STATS_INTERVAL_SECONDS = 10.0


def record_request_metrics(status_code: int, latency_ms: float) -> None:
    global total_requests, total_errors, total_latency_ms

    with metrics_lock:
        total_requests += 1
        if status_code >= 400:
            total_errors += 1
        total_latency_ms += latency_ms


def get_stats_snapshot() -> tuple[int, int, float, float]:
    with metrics_lock:
        requests = total_requests
        errors = total_errors
        latency_sum = total_latency_ms

    error_rate = (errors / requests * 100) if requests else 0.0
    avg_latency = (latency_sum / requests) if requests else 0.0
    return requests, errors, error_rate, avg_latency


def log_aggregated_stats() -> None:
    requests, _, error_rate, avg_latency = get_stats_snapshot()
    logger.info(
        "stats total_requests=%d error_rate=%.2f%% avg_latency=%.2fms",
        requests,
        error_rate,
        avg_latency,
    )


async def maintenance_loop() -> None:
    loop = asyncio.get_running_loop()
    last_tick = loop.time()
    last_stats_time = loop.time()

    while True:
        await asyncio.sleep(MONITOR_INTERVAL_SECONDS)
        now = loop.time()
        blocked_ms = (now - last_tick - MONITOR_INTERVAL_SECONDS) * 1000
        if blocked_ms > EVENT_LOOP_BLOCKED_THRESHOLD_MS:
            logger.warning("event_loop_blocked blocked_for=%.2fms", blocked_ms)
        if now - last_stats_time >= STATS_INTERVAL_SECONDS:
            log_aggregated_stats()
            last_stats_time = now
        last_tick = now


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception:
        status_code = 500
        raise
    finally:
        endpoint = request.scope.get("endpoint")
        if request.url.path == "/cpu":
            endpoint_type = "cpu-bound"
        elif endpoint is not None and inspect.iscoroutinefunction(endpoint):
            endpoint_type = "async"
        else:
            endpoint_type = "sync"

        duration_ms = (time.perf_counter() - start_time) * 1000
        record_request_metrics(status_code, duration_ms)
        logger.info(
            "endpoint_type=%s endpoint=%s latency=%.2fms status_code=%s",
            endpoint_type,
            request.url.path,
            duration_ms,
            status_code,
        )
        if duration_ms > SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                "slow_request endpoint_type=%s endpoint=%s latency=%.2fms status_code=%s",
                endpoint_type,
                request.url.path,
                duration_ms,
                status_code,
            )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/fast")
async def fast():
    return {"status": "fast"}


@app.get("/slow")
async def slow():
    await asyncio.sleep(0.2)
    return {"status": "slow"}


@app.get("/db")
async def db():
    await asyncio.sleep(0.1)
    return [{"id": index, "name": f"item-{index}"} for index in range(10)]


@app.get("/cpu")
def cpu():
    # CPU-heavy work keeps a worker busy. If this ran inside an async handler,
    # it would also block the event loop and slow every other request.
    digest = hashlib.sha256()
    for index in range(200000):
        digest.update(index.to_bytes(4, "little"))
    return {"result": digest.hexdigest()}


@app.get("/error")
def error():
    if random.random() < 0.2:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return {"status": "ok"}


@app.on_event("startup")
async def start_maintenance_task():
    global maintenance_task

    maintenance_task = asyncio.create_task(maintenance_loop())


@app.on_event("shutdown")
async def stop_maintenance_task():
    if maintenance_task is None:
        return

    maintenance_task.cancel()
    with suppress(asyncio.CancelledError):
        await maintenance_task


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
