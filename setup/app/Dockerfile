# import from image on dockerhub
FROM amancevice/pandas:0.25.2-alpine

# copy requirements to container
COPY ./setup/app/requirements.txt /tmp/requirements.txt

# run the following commands to install required libraries
RUN apk add --no-cache \
    curl \
    bash \
    nginx \
    gcc \
    musl-dev \
    postgresql-dev \
    uwsgi \
    uwsgi-python3 \
    supervisor && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r /tmp/requirements.txt && \
    rm /etc/nginx/conf.d/default.conf && \
    rm -r /root/.cache

# copy configuration files for nginx, uwsgi and supervisor
COPY ./setup/app/nginx.conf /etc/nginx/
COPY ./setup/app/flask-site-nginx.conf /etc/nginx/conf.d/
COPY ./setup/app/uwsgi.ini /etc/uwsgi/
COPY ./setup/app/supervisord.conf /etc/

# copy main code
COPY ./app /project/app
WORKDIR /project

# execute supervisor to start the container
CMD ["/usr/bin/supervisord"]
