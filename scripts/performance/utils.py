"""
Created on Feb 2, 2018

@author: nhan.nguyen

This module contains common functions that are used in several modules.
"""

import random
import string
import os
import sys
import tempfile


class Colors:
    """ Class to set the colors for text.
    Syntax:  print(Colors.OKGREEN +"TEXT HERE" +Colors.ENDC) """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'  # Normal default color
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class StandardIOInfo:
    old_stdout = sys.stdout
    stdout_fd = old_stdout.fileno()
    saved_stdout_fd = os.dup(stdout_fd)

    old_stderr = sys.stderr
    stderr_fd = old_stderr.fileno()
    saved_stderr_fd = os.dup(stderr_fd)
    capture = 0
    capture_file = None


def start_capture_console():
    """
    Start capture log in console.

    :return: the file that log in console is written.
    """
    if StandardIOInfo.capture > 0:
        StandardIOInfo.capture += 1
        return None
    StandardIOInfo.capture += 1
    StandardIOInfo.capture_file = tempfile.TemporaryFile("w")
    os.dup2(StandardIOInfo.capture_file.fileno(), sys.stdout.fileno())
    os.dup2(StandardIOInfo.capture_file.fileno(), sys.stderr.fileno())

    return StandardIOInfo.capture_file


def stop_capture_console():
    """
    Stop capture log on console to file.
    """
    if StandardIOInfo.capture > 1:
        StandardIOInfo.capture -= 1
        return
    os.dup2(StandardIOInfo.saved_stdout_fd, StandardIOInfo.stdout_fd)
    os.close(StandardIOInfo.saved_stdout_fd)
    sys.stdout = StandardIOInfo.old_stdout

    os.dup2(StandardIOInfo.saved_stderr_fd, StandardIOInfo.stderr_fd)
    os.close(StandardIOInfo.saved_stderr_fd)
    sys.stderr = StandardIOInfo.old_stderr

    StandardIOInfo.old_stdout = sys.stdout
    StandardIOInfo.stdout_fd = StandardIOInfo.old_stdout.fileno()
    StandardIOInfo.saved_stdout_fd = os.dup(StandardIOInfo.stdout_fd)

    StandardIOInfo.old_stderr = sys.stderr
    StandardIOInfo.stderr_fd = StandardIOInfo.old_stderr.fileno()
    StandardIOInfo.saved_stderr_fd = os.dup(StandardIOInfo.stderr_fd)

    StandardIOInfo.capture -= 1


def force_print_to_console(message: str, color: str):
    """
    Force print a message to console (no matter log is captured or not).
    """
    msg = color + message + Colors.ENDC
    print(msg)
    if StandardIOInfo.capture:
        os.write(StandardIOInfo.saved_stdout_fd, (msg + '\n').encode())


def force_print_green_to_console(message: str):
    """
    Force print a message with green color to console
    (no matter log is captured or not).
    """
    force_print_to_console(message, Colors.OKGREEN)


def force_print_error_to_console(message: str):
    """
    Force print a message with red color to console
    (no matter log is captured or not).
    """
    force_print_to_console(message, Colors.FAIL)


def force_print_warning_to_console(message: str):
    """
    Force print a message with yellow color to console
    (no matter log is captured or not).
    """
    force_print_to_console(message, Colors.WARNING)


def print_with_color(message: str, color: str):
    """
    Print a message with specified color onto console.
    """
    msg = color + message + Colors.ENDC
    print(msg)


def print_error(message: str):
    """
    Print message onto console with "Fail" color.
    """
    print_with_color(message, Colors.FAIL)


def print_header(message: str):
    """
    Print message onto console with "Header" color.
    """
    print_with_color(message, Colors.HEADER)


def print_ok_green(message: str):
    """
    Print message onto console with "OK_GREEN" color.
    """
    print_with_color(message, Colors.OKGREEN)


def print_ok_blue(message: str):
    """
    Print message onto console with "OK_BLUE" color.
    """
    print_with_color(message, Colors.OKBLUE)


def print_warning(message: str):
    """
    Print message onto console with yellow color.
    """
    print_with_color(message, Colors.WARNING)


def print_header_for_step(message: str):
    """
    Print header with format onto console.
    """
    print_header("\n======= {} =======".format(message))


def generate_random_string(
        prefix="", suffix="", size=20,
        characters: str = string.ascii_uppercase + string.digits):
    """
    Generate random string.

    :param prefix:  (optional) Prefix of a string.
    :param suffix:  (optional) Suffix of a string.
    :param size: (optional) Max length of a string (include prefix and suffix)
    :param characters: the characters to make string.
    :return: The random string.
    """
    left_size = size - len(prefix) - len(suffix)
    random_str = ""
    if left_size > 0:
        random_str = ''.join(
            random.choice(characters) for _ in range(left_size))
    else:
        print("Warning: Length of prefix and suffix more than %s chars"
              % str(size))
    result = str(prefix) + random_str + str(suffix)
    return result


def run_async_method(loop, method, *args):
    """
    Run async method.

    :param loop: the loop to run method until complete.
    :param method: method to run.
    :param args: arguments of method.

    :return: result of "method".
    """
    import asyncio
    if not loop:
        loop = asyncio.get_event_loop()
    return loop.run_until_complete(method(*args))


def create_folder(folder):
    """
    Create folder if it is not exist.
    :param folder: folder need to create.
    """
    import errno
    try:
        os.makedirs(folder)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e


def parse_config():
    """
    Return config in 'config.json' as a dictionary.

    :return: config namespace.
    """
    import json

    config_file = os.path.join(os.path.dirname(__file__), 'config.json')

    config_as_dict = json.load(open(config_file))

    class Config:
        pass

    Config.pool_genesis_file = config_as_dict['pool_genesis_file']

    return Config


def print_client_result(passed_req, failed_req, elapsed_time):
    """
    Print a client result (used in perf_add_request and perf_get_request).
    """
    force_print_warning_to_console("\nTotal: %d" % (failed_req +
                                                    passed_req))
    force_print_green_to_console("Passed: %d" % passed_req)
    force_print_error_to_console("Failed: %d\n" % failed_req)

    hours = elapsed_time / 3600
    elapsed_time = 3600 * hours
    minutes = elapsed_time / 60 % 60
    seconds = elapsed_time % 60
    print("\n------ Elapsed time: %dh:%dm:%ds" % (
        hours, minutes, seconds) + " ------")
