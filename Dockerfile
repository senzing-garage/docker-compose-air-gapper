ARG BASE_IMAGE=debian:11.3-slim@sha256:f75d8a3ac10acdaa9be6052ea5f28bcfa56015ff02298831994bd3e6d66f7e57
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2022-05-09

LABEL Name="senzing/docker-compose-air-gapper" \
      Maintainer="support@senzing.com" \
      Version="1.0.2"

HEALTHCHECK CMD ["/app/healthcheck.sh"]

# Run as "root" for system installation.

USER root

# Install packages via apt.

RUN apt update \
 && apt -y install \
      python3-dev \
      python3-pip \
 && rm -rf /var/lib/apt/lists/*

# Install packages via PIP.

COPY requirements.txt ./
RUN pip3 install --upgrade pip \
 && pip3 install -r requirements.txt \
 && rm requirements.txt

# Copy files from repository.

COPY ./rootfs /
COPY ./docker-compose-air-gapper.py /app/

# Make non-root container.

USER 1001

# Runtime execution.

ENV SENZING_DOCKER_LAUNCHED=true

WORKDIR /app
ENTRYPOINT ["/app/docker-compose-air-gapper.py"]
