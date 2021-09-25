# docker-compose-air-gapper

Create a TGZ bundle for air-gapped environments based on docker-compose.yaml

## In an internet-connected environment

### Internet-connected prerequisites

1. Software requirements on the air-gapped system:
    1. [docker](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker.md)
    1. [docker-compose](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-docker-compose.md)
    1. [python 3](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-python-3.md)
        1. Using [pip3](https://github.com/Senzing/knowledge-base/blob/master/HOWTO/install-pip3.md),
        1. install Python requirements in [requirements.txt](requirments.txt).

### Download docker-compose-air-gapper.py

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

### Prepare docker-compose.yaml

1. :pencil2: Identify the directory containing the `docker-compose.yaml` file.
   **Note:** Unfortunately `docker-compose config` only accepts 4 file names:
   `docker-compose.yml`, `docker-compose.yaml`, `compose.yml`, and `compose.yaml`.
   So if your docker-compose.yaml file in the `SENZING_DOCKER_COMPOSE_DIRECTORY` directory has a different name,
   it will need to be renamed or copied to an acceptable name.
   A docker-compose [GitHub issue](https://github.com/docker/compose/issues/8671) has been created to address this.
   Example:

    ```console
    export SENZING_DOCKER_COMPOSE_DIRECTORY=~/my-docker-compose
    ```

1. :thinking: Set any needed environment variables.
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

### Create save-images.sh

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

    docker-compose config \
       | ${SENZING_DOWNLOAD_FILE} create-save-images \
       > ${SENZING_SAVE_IMAGE_FILE}
    ```

1. Make `save-image.sh` executable.
   Example:

    ```console
    chmod +x ${SENZING_SAVE_IMAGE_FILE}
    ```

### Run save-images.sh

1. Run `save-image.sh`
   Example:

    ```console
    ${SENZING_SAVE_IMAGE_FILE}
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
