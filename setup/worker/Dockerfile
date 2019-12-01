# import from image on dockerhub
FROM amancevice/pandas:0.25.2-alpine

# copy requirements to container
COPY ./setup/worker/requirements.txt /tmp/requirements.txt

# run the following commands to install required libraries
RUN apk add --no-cache \
    curl \
    bash \
    nginx \
    uwsgi \
    uwsgi-python3 \
    supervisor && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r /tmp/requirements.txt && \
    rm /etc/nginx/conf.d/default.conf && \
    rm -r /root/.cache

# copy configuration files for supervisor
COPY ./setup/worker/supervisord.conf /etc/supervisord.conf

# copy main code
COPY ./code /project/code
WORKDIR /project/code

# execute supervisor to start the container
CMD ["/usr/bin/supervisord"]
