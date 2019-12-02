## Rudimental Map Reduce example with Celery

This is an example of a Map Reduce workflow that allows to query a Postgres
database, retrieve some data, split it and process it in parallel with
multiple Celery workers. The tasks are orchestrated by using a Redis
cache.

### Celery and Redis

Celery is an asynchronous task queue/job queue based on distributed
message passing. It focuses on real-time operation, but supports
scheduling as well (see `http://www.celeryproject.org`).
Redis is an open source (BSD licensed), in-memory data structure store,
used as a database, cache and message broker (see `https://redis.io`).

### What's needed

Docker should be the only requirement. Everything should run as
soon as you type:

````
docker-compose up
````

After a bit, there should be 5 containers up and running:

- db: the Postgres database, automatically populated with the
script under `setup/db/init_docker_postgres.sql`.
- app: the main Flask app from which the db is queried and the
Celery tasks are posted
- worker: the celery worker doing the job
- monitor: a monitoring tool for the tasks, reachable under
`http://localhost:5555/dashboard`.
See `https://flower.readthedocs.io/en/latest/`.
- redis: the redis cache used to keep track of the tasks.

You can test that everything works by calling:

````
curl -X GET http://127.0.0.1:80
````

The containers can be killed with:

````
docker-compose down
````

### Further information

The main functionality of the app is to retrieve pairs of coordinates
from the database and calculate the minimum distance between the
pair of points. This can be done by calling the following two
endpoints:

- `curl -X POST http://127.0.0.1:80/compute_min_distance`: this
endpoint queries the database and retrieves the pairs of
coordinates. The data is split in four and submitted to independent
Celery tasks that will compute the minimum distance between points
of each group. If the submission goes well this endpoint will pass
a code 200 and a task-id.
- `curl -X GET http://127.0.0.1:80/get_min_distance/<task-id>` once the Celery
tasks are done, the results are passed back to the main app and
the overall minimum distance can be obtained with this endpoint. If
the tasks are not finished the endpoint returns a 204. It will turn
into 200 when they are all done.

#### Useful links

````
https://github.com/gbroccolo/celery-remote-worker
https://github.com/mattkohl/docker-flask-celery-redis
https://testdriven.io/blog/asynchronous-tasks-with-flask-and-redis-queue/
https://github.com/mher/flower
https://github.com/nszceta/celery-map-reduce-demo
https://medium.com/@wkrzywiec/database-in-a-docker-container-how-to-start-and-whats-it-about-5e3ceea77e50
https://hackernoon.com/docker-compose-install-postgresql-for-local-development-environment-ph293zxd
http://www.postgresqltutorial.com/postgresql-cheat-sheet/
````