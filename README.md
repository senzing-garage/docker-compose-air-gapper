# docker-compose-air-gapper
Create a TGZ bundle for air-gapped environments based on docker-compose.yaml


## In an internet-connected enviroment

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
    cd ${SENZING_OUTPUT_DIRECTORY}/${SENZING_TGZ_FILENAME%%.tgz}
    ```

1. Run `load-images.sh`.
   This step loads the local docker repository with the images extracted
   from the `docker-compose-air-gapper-0000000000.tgz` file.
   Example:

    ```console
    ./load-images.sh
    ```
