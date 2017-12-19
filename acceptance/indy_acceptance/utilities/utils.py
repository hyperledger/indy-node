"""
Created on Nov 9, 2017

@author: khoi.ngo

Containing all functions used by several test steps on test scenarios.
"""
from indy.error import IndyError
from .constant import Color
from . import constant
from .result import Status


def generate_random_string(prefix="", suffix="", size=20):
    """
    Generate random string .

    :param prefix: (optional) Prefix of a string.
    :param suffix: (optional) Suffix of a string.
    :param size: (optional) Max length of a string (include prefix and suffix)
    :return: The random string.
    """
    import random
    import string
    left_size = size - len(prefix) - len(suffix)
    random_str = ""
    if left_size > 0:
        random_str = ''.join(random.choice(
            string.ascii_uppercase + string.digits) for _ in range(left_size))
    else:
        print("Warning: Length of prefix and suffix more than %s chars"
              % str(size))
    result = str(prefix) + random_str + str(suffix)
    return result


def exit_if_exception(result):
    """
    If "result" is an exception then raise the "result".
    Unless "result" is an exception then return the "result".
    :param result: the value that you want to check.
    :return: "result" if it is not an exception.
    """
    if (isinstance(result, Exception)):
        exit(1)
    else:
        return result


async def perform(steps, func, *args, ignore_exception=True):
    """
    Execute an function and set status, message for the last test step depend
    on the result of the function.

    :param steps: list of test steps.
    :param func: executed function.
    :param args: argument of function.
    :param ignore_exception: (optional) raise exception or not.
    :return: the result of function of the exception that the function raise.
    """
    try:
        result = await func(*args)
        steps.get_last_step().set_status(Status.PASSED)
    except IndyError as E:
        print(Color.FAIL + constant.INDY_ERROR.format(str(E)) + Color.ENDC)
        steps.get_last_step().set_status(Status.FAILED, str(E))
        result = E
    except Exception as Ex:
        print(Color.FAIL + constant.EXCEPTION.format(str(Ex)) + Color.ENDC)
        steps.get_last_step().set_status(Status.FAILED, str(Ex))
        result = Ex

    if not ignore_exception:
        exit_if_exception(result)

    return result


async def perform_with_expected_code(steps, func, *agrs, expected_code=0):
    """
    Execute the "func" with expectation that the "func" raise an IndyError
    that IndyError.error_code = "expected_code".

    :param steps: list of test steps.
    :param func: executed function.
    :param agrs: arguments of "func".
    :param expected_code: (optional) the error code that you expect
                          in IndyError.
    :return: exception if the "func" raise it without "expected_code".
             'None' if the "func" run without any exception of
             the exception contain "expected_code".
    """
    try:
        await func(*agrs)
        message = "Expected exception %s but not." % str(expected_code)
        steps.get_last_step().set_status(Status.FAILED, message)
        return None
    except IndyError as E:
        if E.error_code == expected_code:
            steps.get_last_step().set_status(Status.PASSED)
            return None
        else:
            print(Color.FAIL + constant.INDY_ERROR.format(str(E)) + Color.ENDC)
            steps.get_last_step().set_status(Status.FAILED, str(E))
            return E
    except Exception as Ex:
        print(Color.FAIL + constant.EXCEPTION.format(str(Ex)) + Color.ENDC)
        steps.get_last_step().set_status(Status.FAILED, str(Ex))
        return Ex


def run_async_method(method):
    """
    Run async method until it complete.
    :param method: The method want to run with event loop.

    @note: We can customize this method to adapt different situations
           in the future.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(method())


def make_final_result(test_result, steps, begin_time, logger):
    """
    Making a test result.

    :param test_result: the object result was collected into test case.
    :param steps: list of steps.
    :param begin_time: time that the test begin.
    :param logger: The object captures screen log.
    """
    import time
    for step in steps:
        test_result.add_step(step)
        if step.get_status() == Status.FAILED:
            print('%s: ' % str(step.get_id()) + Color.FAIL +
                  'failed\nMessage: ' + step.get_message() + Color.ENDC)
            test_result.set_test_failed()

    test_result.set_duration(time.time() - begin_time)
    test_result.write_result_to_file()
    logger.save_log(test_result.get_test_status())


def print_with_color(message: str, color: str):
    print(color + message + Color.ENDC)


def print_error(message: str):
    print_with_color(message, Color.FAIL)
