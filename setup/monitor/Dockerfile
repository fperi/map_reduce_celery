# import from image on dockerhub
FROM python:3.7-alpine

# copy requirements to container
COPY ./setup/monitor/requirements.txt /tmp/requirements.txt

# run the following commands to install required libraries
RUN apk add --no-cache \
    curl \
    bash \
    supervisor && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    pip3 install -r /tmp/requirements.txt && \
    rm -r /root/.cache

# copy configuration files for supervisor
COPY ./setup/monitor/supervisord.conf /etc/supervisord.conf

# copy main code
COPY ./code /project/code
WORKDIR /project/code

# execute supervisor to start the container
CMD ["/usr/bin/supervisord"]
