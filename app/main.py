# import libraries
import json
import os

import celery.states as states
import numpy as np
import pandas as pd
from celery import Celery
from flask import Flask
from redis import StrictRedis
from sqlalchemy import create_engine

POSTGRES_USER = os.environ["POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"]
POSTGRES_DB = os.environ["POSTGRES_DB"]
POSTGRES_PORT = os.environ["POSTGRES_PORT"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]
REDIS_DB = os.environ["REDIS_DB"]

REDIS_BROKER = f"{REDIS_HOST}://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
SQL_ENGINE = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# initialise Flask
app = Flask(__name__)

# initialise redis cache
redis_cache = StrictRedis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)

# initialise celery
celery = Celery("tasks", broker=REDIS_BROKER, backend=REDIS_BROKER)


# health-check endpoint
@app.route("/", methods=["GET"])
def home():
    return "Hello, World!\n"


# post endpoint to compute min distance btw points in db
@app.route("/compute_min_distance", methods=["POST"])
def compute_min_distance():
    """
    This function queries a database and retrieves the coordinates of
    pairs of points from which it computes the minimum distance.
    The data is split into 4 groups each of which is submitted to be processed
    as a different celery task.
    """

    try:
        # use sql alchemy to connect to database
        engine = create_engine(SQL_ENGINE)
        # query database
        data = pd.read_sql_query('select * from "points"', con=engine)
        # split data into 4 to be processed by different celery processes
        data_split = np.array_split(data, 4)

        # loop over data and submit to celery tasks
        for i, d in enumerate(data_split):
            task = celery.send_task(
                "tasks.compute_min_distance", args=[data_split[i].to_json()], kwargs={}
            )
            # create a list in redis to keep track of the tasks
            if i == 0:
                key = "agg_" + task.id
            redis_cache.lpush(key, task.id)

        # return a 200 response as the job was properly submitted
        return app.response_class(
            response=json.dumps({"status": "task submitted", "task_id": key}, indent=4),
            status=200,
            mimetype="application/json",
        )

    # return exception in case of errors
    except Exception as e:

        return app.response_class(
            response=json.dumps(
                {"status": "task not submitted", "error": str(e)}, indent=4
            ),
            status=500,
            mimetype="application/json",
        )


# get endpoint to retrieve the minimum distance
@app.route("/get_min_distance/<task_id>", methods=["GET"])
def get_min_distance(task_id):
    """
    This function retrieves the results from the various celery tasks, each
    of which has calculated the minimum distance between points of the datasets
    they had received. The overall minimum distance between the received
    results is computed and returned.
    """

    try:
        # retrieve task result and compute overall min distance
        min_distance = -1
        for i in range(0, redis_cache.llen(str(task_id))):
            result = celery.AsyncResult(redis_cache.lindex(str(task_id), i))
            if result.state != states.SUCCESS:
                break
            if result.result < min_distance or min_distance == -1:
                min_distance = result.result

        # return 204 when some tasks are not ready
        if result.state == states.PENDING:
            return app.response_class(
                response=json.dumps({"status": "task pending"}, indent=4),
                status=204,
                mimetype="application/json",
            )

        # return 200 when all tasks are finished
        elif result.state == states.SUCCESS:
            # clearn redis
            redis_cache.delete(str(task_id))

            return app.response_class(
                response=json.dumps(
                    {"status": "task completed", "result": str(min_distance)}, indent=4
                ),
                status=200,
                mimetype="application/json",
            )
        # return 500 when tasks failed
        else:
            # clean redis
            redis_cache.delete(str(task_id))
            return app.response_class(
                response=json.dumps({"status": "something went wrong"}, indent=4),
                status=500,
                mimetype="application/json",
            )
    # return 500 when something goes wrong
    except Exception as e:
        return app.response_class(
            response=json.dumps(
                {"status": "impossible to retrieve task", "error": str(e)}, indent=4
            ),
            status=500,
            mimetype="application/json",
        )


if __name__ == "__main__":
    # make Flask server publicly available
    app.run(host="0.0.0.0")
