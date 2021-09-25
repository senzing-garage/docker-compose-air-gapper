#!/usr/bin/env bash

# The save-images.sh script takes 1 input:
#  - DOCKER_IMAGE_NAMES
# Given that input, the docker images are downloaded, saved, and compressed into a single file.

# Enumerate docker images to be processed.

DOCKER_IMAGE_NAMES=(
  "senzing/senzing-console:1.0.3"
  "senzing/xterm:1.2.0"
)

# Make output variables.

MY_HOME=~
OUTPUT_DATE=$(date +%s)
OUTPUT_DATE_HUMAN=$(date --rfc-3339=seconds)
OUTPUT_FILE=${MY_HOME}/docker-compose-air-gapper-${OUTPUT_DATE}.tgz
OUTPUT_DIR_NAME=docker-compose-air-gapper-${OUTPUT_DATE}
OUTPUT_DIR=${MY_HOME}/${OUTPUT_DIR_NAME}
OUTPUT_IMAGES_DIR=${OUTPUT_DIR}/images
OUTPUT_LOAD_REPOSITORY_SCRIPT=${OUTPUT_DIR}/load-images.sh

# Make output directories.

mkdir ${OUTPUT_DIR}
mkdir ${OUTPUT_IMAGES_DIR}

# Define return codes.

OK=0
NOT_OK=1

# Create preamble to OUTPUT_LOAD_REPOSITORY_SCRIPT.

cat <<EOT > ${OUTPUT_LOAD_REPOSITORY_SCRIPT}
#!/usr/bin/env bash

# 'load-images.sh' uses 'docker load' to import images into local registry.
# Created on ${OUTPUT_DATE_HUMAN}

EOT

chmod +x ${OUTPUT_LOAD_REPOSITORY_SCRIPT}

# Save Docker images and scripts to output directory.

for DOCKER_IMAGE_NAME in ${DOCKER_IMAGE_NAMES[@]};
do

  # Pull docker image.

  echo "Pulling ${DOCKER_IMAGE_NAME} from DockerHub."
  docker pull ${DOCKER_IMAGE_NAME}

  # Do a "docker save" to make a file from docker image.

  DOCKER_OUTPUT_FILENAME=$(echo ${DOCKER_IMAGE_NAME} | tr "/:" "--")-${OUTPUT_DATE}.tar
  echo "Creating ${OUTPUT_IMAGES_DIR}/${DOCKER_OUTPUT_FILENAME}"
  docker save ${DOCKER_IMAGE_NAME} --output ${OUTPUT_IMAGES_DIR}/${DOCKER_OUTPUT_FILENAME}

  # Add commands to OUTPUT_LOAD_REPOSITORY_SCRIPT to load file into local repository.

  echo "docker load --input images/${DOCKER_OUTPUT_FILENAME}" >> ${OUTPUT_LOAD_REPOSITORY_SCRIPT}

done

# Compress results.

tar -zcvf ${OUTPUT_FILE} --directory ${MY_HOME} ${OUTPUT_DIR_NAME}

# Epilog.

echo "Done."
echo "    Output file: ${OUTPUT_FILE}"
echo "    Which is a compressed version of ${OUTPUT_DIR}"

exit ${OK}
