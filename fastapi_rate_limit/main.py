from fastapi import FastAPI

from fastapi_rate_limit.workers.redis_sub_worker import RedisSubscribeWorker

redis_worker = RedisSubscribeWorker(
    subscription_key="metrics:request_count",
    host="localhost",
    port=6379,
    password=None
)

app = FastAPI()


@app.on_event("startup")
def startup_event():
    redis_worker.start()


@app.on_event("shutdown")
def shutdown_event():
    redis_worker.stop()


@app.get("/")
def read_root():
    return redis_worker.list_stored_values()


@app.get("/test/{client_name}")
def read_item(client_name: str):

    request_count = redis_worker.getint(client_name)
    if request_count is not None and request_count >= 10:
        return {"error": "Request quota exceeded"}

    request_count = redis_worker.incr(client_name)

    return {"name": client_name, "request_count": request_count}
