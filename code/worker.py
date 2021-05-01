import os

from celery import Celery

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]
REDIS_DB = os.environ["REDIS_DB"]

REDIS_BROKER = f"{REDIS_HOST}://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# initialise celery
celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)
