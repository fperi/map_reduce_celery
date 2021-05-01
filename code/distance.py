import math
import os

import pandas as pd
from celery import Celery

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]
REDIS_DB = os.environ["REDIS_DB"]

REDIS_BROKER = f"{REDIS_HOST}://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"

# initialise celery
celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)


def compute_distance(row):
    """
    This function returns the distance between pairs of points in the
    dataframe rows.
    """

    return math.sqrt(
        math.pow(row["y2"] - row["y1"], 2) + math.pow(row["x2"] - row["x1"], 2)
    )


@celery.task(name="tasks.compute_min_distance")
def compute_min_distance(data):
    """
    This function receives a pandas dataframe as input of which the columns
    are pairs of coordinates [x1, y1, x2, y2]. It then computes the minimum
    distance between such points.
    """

    data = pd.read_json(data)
    data["distance"] = data.apply(compute_distance, axis=1)

    return data["distance"].min()
