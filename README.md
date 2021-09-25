# docker-compose-air-gapper
Create a TGZ bundle for air-gapped environments based on docker-compose.yaml


## In an internet-connected environment

### Download

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

### Run

This step creates the `save-images.sh` shell script using a specified `docker-compose.yaml` file.

1. XXX
   Example:

    ```console
    ```

### Download

1. XXX
   Example:

    ```console

    ```

### XXX

### xxx

1. XXX
   Example:

    ```console
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

### docker-compose up

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
