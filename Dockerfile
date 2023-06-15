ARG BASE_IMAGE=debian:11.7-slim@sha256:924df86f8aad741a0134b2de7d8e70c5c6863f839caadef62609c1be1340daf5
FROM ${BASE_IMAGE}

ENV REFRESHED_AT=2023-06-15

LABEL Name="senzing/docker-compose-air-gapper" \
      Maintainer="support@senzing.com" \
      Version="1.0.4"

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
