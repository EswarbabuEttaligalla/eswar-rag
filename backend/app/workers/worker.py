from redis import Redis
from rq import Connection, Worker

from app.core.config import build_redis_url, settings


redis_conn = Redis.from_url(build_redis_url())

with Connection(redis_conn):
    worker = Worker([settings.RQ_QUEUE_NAME])
    worker.work()
