# docker-compose-air-gapper

## Synopsis

Create a TGZ bundle of docker images for air-gapped environments
based on a `docker-compose.yaml` file.

## Overview

Process:

1. In an internet-connected environment:
    1. "Normalize" a `docker-compose.yaml` file to instantiate variables.
    1. Scan through the normalized `docker-compose.yaml` file looking for `image:` tags.
    1. Create a shell script that does `docker pull` and `docker save`
       for the images.
       Example: [save-images-example.sh](docs/save-images-example.sh)
    1. Run shell script to create TGZ file containing docker images
       with a script to do `docker load`.
1. In an air-gapped environment:
    1. Uncompress the TGZ file.
    1. Run the script to perform `docker load` of the docker images.

### Contents

1. [Preamble](#preamble)
    1. [Legend](#legend)
1. [Related artifacts](#related-artifacts)
1. [Expectations](#expectations)
1. [In an internet-connected environment](#in-an-internet-connected-environment)
    1. [Internet-connected prerequisites](#internet-connected-prerequisites)
    1. [Create save-images.sh](#create-save-imagessh)
    1. [Run save-images.sh](#run-save-imagessh)
1. [In an air-gapped environment](#in-an-air-gapped-environment)
    1. [Air-gapped prerequisites](#air-gapped-prerequisites)
    1. [Load air-gapped docker repository](#load-air-gapped-docker-repository)
1. [Develop](#develop)
1. [Advanced](#advanced)
    1. [Download docker-compose-air-gapper.py](#download-docker-compose-air-gapperpy)
    1. [Create save-images.sh using command-line](#create-save-imagessh-using-command-line)
    1. [Modified docker-compose.yaml file](#modified-docker-composeyaml-file)
1. [Errors](#errors)
1. [References](#references)

## Preamble

At [Senzing](http://senzing.com),
we strive to create GitHub documentation in a
"[don't make me think](https://github.com/Senzing/knowledge-base/blob/main/WHATIS/dont-make-me-think.md)" style.
For the most part, instructions are copy and paste.
Whenever thinking is needed, it's marked with a "thinking" icon :thinking:.
Whenever customization is needed, it's marked with a "pencil" icon :pencil2:.
If the instructions are not clear, please let us know by opening a new
[Documentation issue](https://github.com/Senzing/docker-compose-air-gapper/issues/new?template=documentation_request.md)
describing where we can improve.   Now on with the show...

### Legend

1. :thinking: - A "thinker" icon means that a little extra thinking may be required.
   Perhaps there are some choices to be made.
   Perhaps it's an optional step.
1. :pencil2: - A "pencil" icon means that the instructions may need modification before performing.
1. :warning: - A "warning" icon means that something tricky is happening, so pay attention.

## Related artifacts

1. [DockerHub](https://hub.docker.com/r/senzing/docker-compose-air-gapper)

## Expectations

- **Space:** This repository and demonstration require 1-3 GB free disk space per image saved.
- **Time:** Budget 10 minutes per image saved, depending on CPU and network speeds.
- **Background knowledge:** This repository assumes a working knowledge of:
  - [Docker](https://github.com/Senzing/knowledge-base/blob/main/WHATIS/docker.md)
  - [Docker-compose](https://github.com/Senzing/knowledge-base/blob/main/WHATIS/docker-compose.md)

## In an internet-connected environment

### Internet-connected prerequisites

1. Software requirements on the internet-connected (i.e. not the air-gapped) system:
    1. [docker](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-docker.md)
    1. [docker-compose](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-docker-compose.md)

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
      https://raw.githubusercontent.com/Senzing/knowledge-base/main/lists/docker-versions-latest.sh

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

1. Get the latest version of `senzing/docker-compose-air-gapper`.
   Example:

    ```console
    docker pull senzing/docker-compose-air-gapper:latest
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
      senzing/docker-compose-air-gapper:latest
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

## In an air-gapped environment

### Air-gapped prerequisites

1. Software requirements on the air-gapped system:
    1. [docker](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-docker.md)
    1. [docker-compose](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-docker-compose.md)
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

## Develop

The following instructions are used when modifying and building the Docker image.

### Prerequisites for development

:thinking: The following tasks need to be complete before proceeding.
These are "one-time tasks" which may already have been completed.

1. The following software programs need to be installed:
    1. [git](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-git.md)
    1. [make](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-make.md)
    1. [docker](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-docker.md)

### Clone repository

For more information on environment variables,
see [Environment Variables](https://github.com/Senzing/knowledge-base/blob/main/lists/environment-variables.md).

1. Set these environment variable values:

    ```console
    export GIT_ACCOUNT=senzing
    export GIT_REPOSITORY=docker-compose-air-gapper
    export GIT_ACCOUNT_DIR=~/${GIT_ACCOUNT}.git
    export GIT_REPOSITORY_DIR="${GIT_ACCOUNT_DIR}/${GIT_REPOSITORY}"
    ```

1. Using the environment variables values just set, follow steps in [clone-repository](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/clone-repository.md) to install the Git repository.

### Build Docker image

1. **Option #1:** Using `docker` command and GitHub.

    ```console
    sudo docker build \
      --tag senzing/docker-compose-air-gapper \
      https://github.com/senzing/docker-compose-air-gapper.git#main
    ```

1. **Option #2:** Using `docker` command and local repository.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo docker build --tag senzing/docker-compose-air-gapper .
    ```

1. **Option #3:** Using `make` command.

    ```console
    cd ${GIT_REPOSITORY_DIR}
    sudo make docker-build
    ```

## Advanced

### Download docker-compose-air-gapper.py

1. Have [python 3](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-python-3.md) installed.
    1. Using [pip3](https://github.com/Senzing/knowledge-base/blob/main/HOWTO/install-pip3.md),
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

## Errors

1. See [docs/errors.md](docs/errors.md).

## References
