# docker-compose-air-gapper

## Synopsis

Create a TGZ bundle for air-gapped environments based on `docker-compose.yaml`

## Overview

Steps:

1. Create a `tgz` file containing
1. "Normalize" a `docker-compose.yaml` file to instantiate variables.
1. Scan through the normalized `docker-compose.yaml` file looking for `image:` tags
1. Create a shell script that

## In an internet-connected environment

### Internet-connected prerequisites

1. Software requirements on the internet-connected (i.e. not the air-gapped) system:
    1. [docker](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker.md)
    1. [docker-compose](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker-compose.md)

### Create save-images.sh

1. :pencil2: Identify the directory containing the `docker-compose.yaml` file.
   Example:

    ```console
    export SENZING_DOCKER_COMPOSE_DIRECTORY=~/my-docker-compose
    ```

1. :thinking: **Optional:** Set any needed environment variables.
   For instance,
   to specify the latest docker image tags for docker-compose.yaml files in
   [docker-compose-demo](https://github.com/Senzing/docker-compose-demo)
   environment variables can be set in this manner.
   Example:

    ```console
    curl -X GET \
      --output ~/docker-versions-latest.sh \
      https://raw.githubusercontent.com/Senzing/knowledge-base/master/lists/docker-versions-latest.sh

    source ~/docker-versions-latest.sh
    ```

1. Use [docker-compose config](https://docs.docker.com/compose/reference/config/)
   to normalize the `docker-compose.yaml` file into a new `docker-compose-normalized.yaml` file.

   Example:

    ```console
    cd ${SENZING_DOCKER_COMPOSE_DIRECTORY}

    docker-compose \
      --file docker-compose.yaml \
      config \
    > docker-compose-normalized.yaml
    ```

1. Using a `senzing/docker-compose-air-gapper` docker container,
   create a `save-images.sh` file in the `SENZING_DOCKER_COMPOSE_DIRECTORY` directory.
   Example:

    ```console
    docker run \
      --env SENZING_DOCKER_COMPOSE_FILE=/data/docker-compose-normalized.yaml \
      --env SENZING_OUTPUT_FILE=/data/save-images.sh \
      --env SENZING_SUBCOMMAND=create-save-images \
      --interactive \
      --rm \
      --tty \
      --volume ${SENZING_DOCKER_COMPOSE_DIRECTORY}:/data \
      senzing/docker-compose-air-gapper
    ```

### Run save-images.sh

1. Run `save-images.sh`
   Example:

    ```console
    cd ${SENZING_DOCKER_COMPOSE_DIRECTORY}
    chmod +x save-images.sh

    ./save-images.sh
    ```

1. After `save-images.sh` has completed, there will be a new `~/docker-compose-air-gapper-0000000000.tgz` file.
   This is the file to be transferred to the air-gapped system.
   Example output:

    ```console
    Done.
        Output file: /home/senzing/docker-compose-air-gapper-0000000000.tgz
        Which is a compressed version of /home/senzing/docker-compose-air-gapper-0000000000
    ```

## In air-gapped environment

### Air-gapped prerequisites

1. Software requirements on the air-gapped system:
    1. [docker](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker.md)
    1. [docker-compose](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker-compose.md)
1. The `docker-compose-air-gapper-0000000000.tgz` needs to be transferred to the air-gapped system.

### Load air-gapped docker repository

1. :pencil2: Set Environment variables.
   Identify the location of the `tgz` file (`SENZING_TGZ_FILE`)
   and the location where the files should be extracted (`SENZING_OUTPUT_DIRECTORY`).
   Example:

    ```console
    export SENZING_OUTPUT_DIRECTORY=/tmp
    export SENZING_TGZ_FILE=~/docker-compose-air-gapper-0000000000.tgz
    ```

1. Extract `docker-compose-air-gapper-0000000000.tgz` file into specified directory.
   Example:

    ```console
    tar \
      --directory=${SENZING_OUTPUT_DIRECTORY} \
      --extract \
      --file=${SENZING_TGZ_FILE} \
      --verbose
    ```

1. Change directory to the location of the extracted files.
   Example:

    ```console
    export SENZING_TGZ_FILENAME=${SENZING_TGZ_FILE##*/}
    export SENZING_INPUT_DIRECTORY=${SENZING_OUTPUT_DIRECTORY}/${SENZING_TGZ_FILENAME%%.tgz}

    cd ${SENZING_INPUT_DIRECTORY}
    ```

1. Run `load-images.sh`.
   This step loads the local docker repository with the images extracted
   from the `docker-compose-air-gapper-0000000000.tgz` file.
   Example:

    ```console
    ./load-images.sh
    ```

### Run docker-compose up

1. :pencil2: Set environment variables that are use by the `docker-compose.yaml` file.
   **NOTE:** Depending on the `docker-compose.yaml`, more environment variables may need to be set.
   Example:

    ```console
    export SENZING_DATA_VERSION_DIR=/opt/senzing/data/2.0.0
    export SENZING_ETC_DIR=/etc/opt/senzing
    export SENZING_G2_DIR=/opt/senzing/g2
    export SENZING_VAR_DIR=/var/opt/senzing
    ```

1. Bring up docker-compose.
   Example:

    ```console
    cd ${SENZING_INPUT_DIRECTORY}
    docker-compose up
    ```

## Alternatives

### Download docker-compose-air-gapper.py

1. Have [python 3](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-python-3.md) installed.
    1. Using [pip3](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-pip3.md),
       install Python requirements in [requirements.txt](requirments.txt).

1. Get a local copy of
   [docker-compose-air-gapper.py](docker-compose-air-gapper.py).
   Example:

    1. :pencil2: Specify where to download file.
       Example:

        ```console
        export SENZING_DOWNLOAD_FILE=~/docker-compose-air-gapper.py
        ```

    1. Download file.
       Example:

        ```console
        curl -X GET \
          --output ${SENZING_DOWNLOAD_FILE} \
          https://raw.githubusercontent.com/Senzing/docker-compose-air-gapper/main/docker-compose-air-gapper.py
        ```

    1. Make file executable.
       Example:

        ```console
        chmod +x ${SENZING_DOWNLOAD_FILE}
        ```

### Create save-images.sh using command-line

This step creates the `save-images.sh` shell script using a specified `docker-compose.yaml` file.

1. :pencil2: Identify the file to hold a new shell script.
   This script will be used to download, save, and compress docker images into a single file.
   Example:

    ```console
    export SENZING_SAVE_IMAGE_FILE=~/save-images.sh
    ```

1. Create `save-images.sh` by using `docker-compose config` to normalize `docker-compose.yaml`.
   The normalized output is used by `docker-compose-air-gapper.py` to create `save-images.sh`
   Example:

    ```console
    cd ${SENZING_DOCKER_COMPOSE_DIRECTORY}

    docker-compose --file docker-compose.yaml config \
       | ${SENZING_DOWNLOAD_FILE} create-save-images \
       > ${SENZING_SAVE_IMAGE_FILE}
    ```

1. Make `save-image.sh` executable.
   Example:

    ```console
    chmod +x ${SENZING_SAVE_IMAGE_FILE}
    ```

### Modified docker-compose.yaml file

Since
[docker-compose-air-gapper.py](docker-compose-air-gapper.py)
only looks at a few properties in the `docker-compose.yaml` file,
it's possible to make a skeleton `docker-compose.yaml`
file for the purposes of creating a TGZ file for an air-gapped enviroment.

1. For example, a `/tmp/docker-compose-skeleton.yaml` file could look like this:

    ```yaml
    services:
      x:
        image: senzing/senzing-console:1.0.3
      y:
        image: senzing/stream-loader:1.9.0
      z:
        image: senzing/senzing-api-server:2.7.4
    ```

1. Since the `docker-compose-skeleton.yaml` file is already "normalized"
   (i.e. there are no variables for substitution), there is no need to run `docker-compose config`.

1. Using a `senzing/docker-compose-air-gapper` docker container,
   create a `save-images.sh` file in the `/tmp` directory.
   Example:

    ```console
    docker run \
      --env SENZING_DOCKER_COMPOSE_FILE=/data/docker-compose-skeleton.yaml \
      --env SENZING_OUTPUT_FILE=/data/save-images.sh \
      --env SENZING_SUBCOMMAND=create-save-images \
      --interactive \
      --rm \
      --tty \
      --volume /tmp:/data \
      senzing/docker-compose-air-gapper
    ```

1. Run `save-images.sh`.
   Example:

    ```console
    chmod +x /tmp/save-images.sh
    /tmp/save-images.sh
    ```
