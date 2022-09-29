#! /usr/bin/env python3

'''
# -----------------------------------------------------------------------------
# docker-compose-air-gapper.py
# -----------------------------------------------------------------------------
'''

# Import from standard library. https://docs.python.org/3/library/

import argparse
import json
import linecache
import logging
import os
import signal
import sys
import time

# Import from https://pypi.org/

import yaml

# Metadata

__all__ = []
__version__ = "1.0.3"  # See https://www.python.org/dev/peps/pep-0396/
__date__ = '2021-09-25'
__updated__ = '2022-09-29'

SENZING_PRODUCT_ID = "5028"  # See https://github.com/Senzing/knowledge-base/blob/main/lists/senzing-product-ids.md
LOG_FORMAT = '%(asctime)s %(message)s'

# Working with bytes.

KILOBYTES = 1024
MEGABYTES = 1024 * KILOBYTES
GIGABYTES = 1024 * MEGABYTES

# The "configuration_locator" describes where configuration variables are in:
# 1) Command line options, 2) Environment variables, 3) Configuration files, 4) Default values

CONFIGURATION_LOCATOR = {
    "debug": {
        "default": False,
        "env": "SENZING_DEBUG",
        "cli": "debug"
    },
    "docker_compose_file": {
        "default": None,
        "env": "SENZING_DOCKER_COMPOSE_FILE",
        "cli": "docker-compose-file"
    },
    "output_file": {
        "default": None,
        "env": "SENZING_OUTPUT_FILE",
        "cli": "output-file"
    },
    "sleep_time_in_seconds": {
        "default": 0,
        "env": "SENZING_SLEEP_TIME_IN_SECONDS",
        "cli": "sleep-time-in-seconds"
    },
    "subcommand": {
        "default": None,
        "env": "SENZING_SUBCOMMAND",
    }
}

# Enumerate keys in 'configuration_locator' that should not be printed to the log.

KEYS_TO_REDACT = [
    "password",
]

# -----------------------------------------------------------------------------
# Define argument parser
# -----------------------------------------------------------------------------


def get_parser():
    ''' Parse commandline arguments. '''

    subcommands = {
        'create-save-images': {
            "help": 'Create the save-images.sh file.',
            "argument_aspects": ["common"],
            "arguments": {
                "--docker-compose-file": {
                    "dest": "docker_compose_file",
                    "metavar": "SENZING_DOCKER_COMPOSE_FILE",
                    "help": "Location of 'docker-compose.yaml' file. Default: STDIN"
                },
                "--output-file": {
                    "dest": "output_file",
                    "metavar": "SENZING_OUTPUT_FILE",
                    "help": "Send output to this file. Default: STDOUT"
                },
            },
        },
        'sleep': {
            "help": 'Do nothing but sleep. For Docker testing.',
            "arguments": {
                "--sleep-time-in-seconds": {
                    "dest": "sleep_time_in_seconds",
                    "metavar": "SENZING_SLEEP_TIME_IN_SECONDS",
                    "help": "Sleep time in seconds. DEFAULT: 0 (infinite)"
                },
            },
        },
        'version': {
            "help": 'Print version of program.',
        },
        'docker-acceptance-test': {
            "help": 'For Docker acceptance testing.',
        },
    }

    # Define argument_aspects.

    argument_aspects = {
        "common": {
            "--debug": {
                "dest": "debug",
                "action": "store_true",
                "help": "Enable debugging. (SENZING_DEBUG) Default: False"
            },
        },
    }

    # Augment "subcommands" variable with arguments specified by aspects.

    for subcommand, subcommand_value in subcommands.items():
        if 'argument_aspects' in subcommand_value:
            for aspect in subcommand_value['argument_aspects']:
                if 'arguments' not in subcommands[subcommand]:
                    subcommands[subcommand]['arguments'] = {}
                arguments = argument_aspects.get(aspect, {})
                for argument, argument_value in arguments.items():
                    subcommands[subcommand]['arguments'][argument] = argument_value

    parser = argparse.ArgumentParser(prog="docker-compose-air-gapper.py", description="Initialize Senzing installation. For more information, see https://github.com/Senzing/docker-compose-air-gapper")
    subparsers = parser.add_subparsers(dest='subcommand', help='Subcommands (SENZING_SUBCOMMAND):')

    for subcommand_key, subcommand_values in subcommands.items():
        subcommand_help = subcommand_values.get('help', "")
        subcommand_arguments = subcommand_values.get('arguments', {})
        subparser = subparsers.add_parser(subcommand_key, help=subcommand_help)
        for argument_key, argument_values in subcommand_arguments.items():
            subparser.add_argument(argument_key, **argument_values)

    return parser

# -----------------------------------------------------------------------------
# Message handling
# -----------------------------------------------------------------------------

# 1xx Informational (i.e. logging.info())
# 3xx Warning (i.e. logging.warning())
# 5xx User configuration issues (either logging.warning() or logging.err() for Client errors)
# 7xx Internal error (i.e. logging.error for Server errors)
# 9xx Debugging (i.e. logging.debug())


MESSAGE_INFO = 100
MESSAGE_WARN = 300
MESSAGE_ERROR = 700
MESSAGE_DEBUG = 900

MESSAGE_DICTIONARY = {
    "100": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}I",
    "294": "Version: {0}  Updated: {1}",
    "295": "Sleeping infinitely.",
    "296": "Sleeping {0} seconds.",
    "297": "Enter {0}",
    "298": "Exit {0}",
    "299": "{0}",
    "300": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}W",
    "499": "{0}",
    "500": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}E",
    "696": "Bad SENZING_SUBCOMMAND: {0}.",
    "697": "No processing done.",
    "698": "Program terminated with error.",
    "699": "{0}",
    "700": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}E",
    "899": "{0}",
    "900": "senzing-" + SENZING_PRODUCT_ID + "{0:04d}D",
    "998": "Debugging enabled.",
    "999": "{0}",
}


def message(index, *args):
    ''' Return an instantiated message. '''
    index_string = str(index)
    template = MESSAGE_DICTIONARY.get(index_string, "No message for index {0}.".format(index_string))
    return template.format(*args)


def message_generic(generic_index, index, *args):
    ''' Return a formatted message. '''
    return "{0} {1}".format(message(generic_index, index), message(index, *args))


def message_info(index, *args):
    ''' Return an info message. '''
    return message_generic(MESSAGE_INFO, index, *args)


def message_warning(index, *args):
    ''' Return a warning message. '''
    return message_generic(MESSAGE_WARN, index, *args)


def message_error(index, *args):
    ''' Return an error message. '''
    return message_generic(MESSAGE_ERROR, index, *args)


def message_debug(index, *args):
    ''' Return a debug message. '''
    return message_generic(MESSAGE_DEBUG, index, *args)


def get_exception():
    ''' Get details about an exception. '''
    exception_type, exception_object, traceback = sys.exc_info()
    frame = traceback.tb_frame
    line_number = traceback.tb_lineno
    filename = frame.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, line_number, frame.f_globals)
    return {
        "filename": filename,
        "line_number": line_number,
        "line": line.strip(),
        "exception": exception_object,
        "type": exception_type,
        "traceback": traceback,
    }

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------


def get_configuration(subcommand, args):
    ''' Order of precedence: CLI, OS environment variables, INI file, default. '''
    result = {}

    # Copy default values into configuration dictionary.

    for key, value in list(CONFIGURATION_LOCATOR.items()):
        result[key] = value.get('default', None)

    # "Prime the pump" with command line args. This will be done again as the last step.

    for key, value in list(args.__dict__.items()):
        new_key = key.format(subcommand.replace('-', '_'))
        if value:
            result[new_key] = value

    # Copy OS environment variables into configuration dictionary.

    for key, value in list(CONFIGURATION_LOCATOR.items()):
        os_env_var = value.get('env', None)
        if os_env_var:
            os_env_value = os.getenv(os_env_var, None)
            if os_env_value:
                result[key] = os_env_value

    # Copy 'args' into configuration dictionary.

    for key, value in list(args.__dict__.items()):
        new_key = key.format(subcommand.replace('-', '_'))
        if value:
            result[new_key] = value

    # Add program information.

    result['program_version'] = __version__
    result['program_updated'] = __updated__

    # Special case: subcommand from command-line

    if args.subcommand:
        result['subcommand'] = args.subcommand

    # Special case: Change boolean strings to booleans.

    booleans = [
        'debug',
    ]
    for boolean in booleans:
        boolean_value = result.get(boolean)
        if isinstance(boolean_value, str):
            boolean_value_lower_case = boolean_value.lower()
            if boolean_value_lower_case in ['true', '1', 't', 'y', 'yes']:
                result[boolean] = True
            else:
                result[boolean] = False

    # Special case: Change integer strings to integers.

    integers = [
        'sleep_time_in_seconds'
    ]
    for integer in integers:
        integer_string = result.get(integer)
        result[integer] = int(integer_string)

    return result


def validate_configuration(config):
    ''' Check aggregate configuration from commandline options, environment variables, config files, and defaults. '''

    user_warning_messages = []
    user_error_messages = []

    # Perform subcommand specific checking.

    subcommand = config.get('subcommand')

    if subcommand in ['service']:
        pass

    # Log warning messages.

    for user_warning_message in user_warning_messages:
        logging.warning(user_warning_message)

    # Log error messages.

    for user_error_message in user_error_messages:
        logging.error(user_error_message)

    # Log where to go for help.

    if len(user_warning_messages) > 0 or len(user_error_messages) > 0:
        logging.info(message_info(293))

    # If there are error messages, exit.

    if len(user_error_messages) > 0:
        exit_error(697)


def redact_configuration(config):
    ''' Return a shallow copy of config with certain keys removed. '''
    result = config.copy()
    for key in KEYS_TO_REDACT:
        try:
            result.pop(key)
        except Exception:
            pass
    return result

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def create_signal_handler_function(args):
    ''' Tricky code.  Uses currying technique. Create a function for signal handling.
        that knows about "args".
    '''

    def result_function(signal_number, frame):
        logging.info(message_info(298, args))
        logging.debug(message_debug(901, signal_number, frame))
        sys.exit(0)

    return result_function


def bootstrap_signal_handler(signal_number, frame):
    ''' Exit on signal error. '''
    logging.debug(message_debug(901, signal_number, frame))
    sys.exit(0)


def entry_template(config):
    ''' Format of entry message. '''
    debug = config.get("debug", False)
    config['start_time'] = time.time()
    if debug:
        final_config = config
    else:
        final_config = redact_configuration(config)
    config_json = json.dumps(final_config, sort_keys=True)
    return message_info(297, config_json)


def exit_template(config):
    ''' Format of exit message. '''
    debug = config.get("debug", False)
    stop_time = time.time()
    config['stop_time'] = stop_time
    config['elapsed_time'] = stop_time - config.get('start_time', stop_time)
    if debug:
        final_config = config
    else:
        final_config = redact_configuration(config)
    config_json = json.dumps(final_config, sort_keys=True)
    return message_info(298, config_json)


def exit_error(index, *args):
    ''' Log error message and exit program. '''
    logging.error(message_error(index, *args))
    logging.error(message_error(698))
    sys.exit(1)


def exit_silently():
    ''' Exit program. '''
    sys.exit(0)

# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------


def replace_variables_in_text(function_with_text, variables):
    """ Perform variable replacement in text """

    return function_with_text.__doc__.format(**variables)

# -----------------------------------------------------------------------------
# Text functions
# -----------------------------------------------------------------------------


def file_text_for_save_images():
    """#!/usr/bin/env bash

# The save-images.sh script takes 1 input:
#  - DOCKER_IMAGE_NAMES
# Given that input, the docker images are downloaded, saved, and compressed into a single file.

# Enumerate docker images to be processed.

DOCKER_IMAGE_NAMES=(
{image_list})

# Make output variables.

MY_HOME=${{MY_HOME:-~}}
OUTPUT_DATE=$(date +%s)
OUTPUT_DATE_HUMAN=$(date --rfc-3339=seconds)
OUTPUT_FILE=${{OUTPUT_FILE:-${{MY_HOME}}/docker-compose-air-gapper-${{OUTPUT_DATE}}.tgz}}
OUTPUT_DIR_NAME=docker-compose-air-gapper-${{OUTPUT_DATE}}
OUTPUT_DIR=${{MY_HOME}}/${{OUTPUT_DIR_NAME}}
OUTPUT_IMAGES_DIR=${{OUTPUT_DIR}}/images
OUTPUT_LOAD_REPOSITORY_SCRIPT=${{OUTPUT_DIR}}/load-images.sh

# Make output directories.

mkdir ${{OUTPUT_DIR}}
mkdir ${{OUTPUT_IMAGES_DIR}}

# Define return codes.

OK=0
NOT_OK=1

# Create preamble to OUTPUT_LOAD_REPOSITORY_SCRIPT.

cat <<EOT > ${{OUTPUT_LOAD_REPOSITORY_SCRIPT}}
#!/usr/bin/env bash

# 'load-images.sh' uses 'docker load' to import images into local registry.
# Created on ${{OUTPUT_DATE_HUMAN}}

EOT

chmod +x ${{OUTPUT_LOAD_REPOSITORY_SCRIPT}}

# Save Docker images and scripts to output directory.

for DOCKER_IMAGE_NAME in ${{DOCKER_IMAGE_NAMES[@]}};
do

  # Pull docker image.

  echo "Pulling ${{DOCKER_IMAGE_NAME}} from DockerHub."
  docker pull ${{DOCKER_IMAGE_NAME}}

  # Do a "docker save" to make a file from docker image.

  DOCKER_OUTPUT_FILENAME=$(echo ${{DOCKER_IMAGE_NAME}} | tr "/:" "--")-${{OUTPUT_DATE}}.tar
  echo "Creating ${{OUTPUT_IMAGES_DIR}}/${{DOCKER_OUTPUT_FILENAME}}"
  docker save ${{DOCKER_IMAGE_NAME}} --output ${{OUTPUT_IMAGES_DIR}}/${{DOCKER_OUTPUT_FILENAME}}

  # Add commands to OUTPUT_LOAD_REPOSITORY_SCRIPT to load file into local repository.

  echo "docker load --input images/${{DOCKER_OUTPUT_FILENAME}}" >> ${{OUTPUT_LOAD_REPOSITORY_SCRIPT}}

done

# Compress results.

tar -zcvf ${{OUTPUT_FILE}} --directory ${{MY_HOME}} ${{OUTPUT_DIR_NAME}}

# Epilog.

echo "Done."
echo "    Output file: ${{OUTPUT_FILE}}"
echo "    Which is a compressed version of ${{OUTPUT_DIR}}"

exit ${{OK}}
"""
    return 0

# -----------------------------------------------------------------------------
# Text functions
# -----------------------------------------------------------------------------


def create_output_text(images):
    """ Perform variable replacement in text """

    image_list = ""
    for image in images:
        image_list += "  \"{0}\"\n".format(image)
    variables = {
        "image_list": image_list,
    }
    return replace_variables_in_text(file_text_for_save_images, variables)

# -----------------------------------------------------------------------------
# do_* functions
#   Common function signature: do_XXX(args)
# -----------------------------------------------------------------------------


def do_docker_acceptance_test(subcommand, args):
    ''' For use with Docker acceptance testing. '''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(subcommand, args)

    # Prolog.

    logging.info(entry_template(config))

    # Epilog.

    logging.info(exit_template(config))


def do_create_save_images(subcommand, args):
    ''' Create 'save-images.sh' '''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(subcommand, args)

    # Prolog.

    logging.info(entry_template(config))

    # Construct docker_compose dictionary from YAML.

    docker_compose = {}
    docker_compose_file = config.get('docker_compose_file')
    if docker_compose_file:
        with open(docker_compose_file) as a_file:
            docker_compose = yaml.safe_load(a_file)
    else:
        docker_compose = yaml.load(sys.stdin)

    # Create list of images.

    services = docker_compose.get('services', {})
    images = []
    for value in services.values():
        images.append(value.get("image"))

    # Create output.

    output_text = create_output_text(images)

    # Print output.

    output_file = config.get('output_file')
    if output_file:
        with open(output_file, "w") as a_file:
            a_file.write(output_text)
    else:
        print(output_text)

    # Epilog.

    logging.info(exit_template(config))


def do_sleep(subcommand, args):
    ''' Sleep.  Used for debugging. '''

    # Get context from CLI, environment variables, and ini files.

    config = get_configuration(subcommand, args)

    # Prolog.

    logging.info(entry_template(config))

    # Pull values from configuration.

    sleep_time_in_seconds = config.get('sleep_time_in_seconds')

    # Sleep.

    if sleep_time_in_seconds > 0:
        logging.info(message_info(296, sleep_time_in_seconds))
        time.sleep(sleep_time_in_seconds)

    else:
        sleep_time_in_seconds = 3600
        while True:
            logging.info(message_info(295))
            time.sleep(sleep_time_in_seconds)

    # Epilog.

    logging.info(exit_template(config))


def do_version(subcommand, args):
    ''' Log version information. '''

    logging.info(message_info(294, __version__, __updated__))
    logging.debug(message_debug(902, subcommand, args))

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------


if __name__ == "__main__":

    # Configure logging. See https://docs.python.org/2/library/logging.html#levels

    LOG_LEVEL_MAP = {
        "notset": logging.NOTSET,
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "fatal": logging.FATAL,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    LOG_LEVEL_PARAMETER = os.getenv("SENZING_LOG_LEVEL", "info").lower()
    LOG_LEVEL = LOG_LEVEL_MAP.get(LOG_LEVEL_PARAMETER, logging.INFO)
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
    logging.debug(message_debug(998))

    # Trap signals temporarily until args are parsed.

    signal.signal(signal.SIGTERM, bootstrap_signal_handler)
    signal.signal(signal.SIGINT, bootstrap_signal_handler)

    # Parse the command line arguments.

    SUBCOMMAND = os.getenv("SENZING_SUBCOMMAND", None)
    PARSER = get_parser()
    if len(sys.argv) > 1:
        ARGS = PARSER.parse_args()
        SUBCOMMAND = ARGS.subcommand
    elif SUBCOMMAND:
        ARGS = argparse.Namespace(subcommand=SUBCOMMAND)
    else:
        PARSER.print_help()
        if len(os.getenv("SENZING_DOCKER_LAUNCHED", "")) > 0:
            SUBCOMMAND = "sleep"
            ARGS = argparse.Namespace(subcommand=SUBCOMMAND)
            do_sleep(SUBCOMMAND, ARGS)
        exit_silently()

    # Catch interrupts. Tricky code: Uses currying.

    SIGNAL_HANDLER = create_signal_handler_function(ARGS)
    signal.signal(signal.SIGINT, SIGNAL_HANDLER)
    signal.signal(signal.SIGTERM, SIGNAL_HANDLER)

    # Transform subcommand from CLI parameter to function name string.

    SUBCOMMAND_FUNCTION_NAME = "do_{0}".format(SUBCOMMAND.replace('-', '_'))

    # Test to see if function exists in the code.

    if SUBCOMMAND_FUNCTION_NAME not in globals():
        logging.warning(message_warning(696, SUBCOMMAND))
        PARSER.print_help()
        exit_silently()

    # Tricky code for calling function based on string.

    globals()[SUBCOMMAND_FUNCTION_NAME](SUBCOMMAND, ARGS)
