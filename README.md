# docker-compose-air-gapper

Create a TGZ bundle for air-gapped environments based on docker-compose.yaml

## In an internet-connected environment

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

### Create save-images.sh

This step creates the `save-images.sh` shell script using a specified `docker-compose.yaml` file.

1. :pencil2: Identify the directory containing the `docker-compose.yaml` file.
   **Note:** Unfortunately `docker-compose config` only accepts 4 file names:
   docker-compose.yml, docker-compose.yaml, compose.yml, compose.yaml.
   So if your docker-compose file has a different name, it will need to be renamed or copied to an acceptable name.
   A docker-compose [GitHub issue](https://github.com/docker/compose/issues/8671) has been created to address this.
   Example:

    ```console
    export SENZING_DOCKER_COMPOSE_DIRECTORY=~/my-docker-compose
    ```

1. :pencil3: Identify the directory to hold a new shell script.
   This script will be used to download, save and compress docker images into a single file.
   Example:

    ```console
    export SENZING_SAVE_IMAGE_FILE=~/save-images.sh
    ```

1. XXX
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
