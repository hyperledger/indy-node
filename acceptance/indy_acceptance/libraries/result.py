"""
Created on Nov 9, 2017

@author: nhan.nguyen

Containing classes to make the test result as a json.
"""

import errno
import json
import os
import time

from .constant import Color
from enum import Enum

TEST_CASE = "testcase"
RESULT = "result"
START_TIME = "starttime"
DURATION = "duration"
RUN = "run"
STEP = "step"
STATUS = "status"
MESSAGE = "message"


class Status(str, Enum):
    PASSED = "Passed"
    FAILED = "Failed"


class TestResult:
    __json_dir = os.path.join(os.path.dirname(
        __file__), "..") + "/test_output/test_results/"

    def __init__(self, test_case_name):
        """
        Constructor of a TestResult instance.

        :param test_case_name: (optional) name of test case.
        """
        self.__init_output_folder()
        self.__test_result = {}  # Store information of a test case
        self.__run = []  # Store information of steps in test case
        self.__test_result[TEST_CASE] = test_case_name
        self.__test_result[RESULT] = Status.PASSED
        self.__test_result[START_TIME] = str(
            time.strftime("%Y-%m-%d_%H-%M-%S"))
        self.__json_file_path = "{}{}_{}.json".format(
                                TestResult.__json_dir,
                                self.__test_result[TEST_CASE],
                                self.__test_result[START_TIME])

    def set_result(self, result):
        """
        Set a result (PASSED or FAILED) for test case.

        :param result: (optional) result of test.
        """
        self.__test_result[RESULT] = result

    def set_duration(self, duration):
        """
        Set duration for test.

        :param duration: (second).
        """
        self.__test_result[DURATION] = round(duration * 1000)

    def set_step_status(self, step_summary: str, status: str = Status.PASSED,
                        message: str = None):
        """
        Set status and message for specify step.

        :param step_summary: (optional) title of step.
        :param status: (optional) PASSED or FAILED.
        :param message: anything that involve to step like Exception, Log,...
        """
        temp = {STEP: step_summary, STATUS: status, MESSAGE: message}
        self.__run.append(temp)

    def add_step(self, step):
        """
        Add a step to report.

        :param step: (optional) a Step object in step.py
        """
        if not step:
            return
        temp = {STEP: step.get_name(), STATUS: step.get_status(),
                MESSAGE: step.get_message()}
        self.__run.append(temp)

    def write_result_to_file(self):
        """
        Write the result as json.
        """
        self.__test_result[RUN] = self.__run
        with open(self.__json_file_path, "w+") as outfile:
            json.dump(self.__test_result, outfile,
                      ensure_ascii=False, indent=2)
            print(Color.OKBLUE + "\nJson file has been written at: {}\n"
                  .format(self.__json_file_path) + Color.ENDC)

    def set_test_failed(self):
        """
        Set status of test to FAILED.
        """
        self.set_result(Status.FAILED)

    def set_test_passed(self):
        """
        Set status of test to PASSED.
        """
        self.set_result(Status.PASSED)

    def get_test_status(self) -> str:
        """
        Get the status of test.

        :return: test status.
        """
        return self.__test_result[RESULT]

    @staticmethod
    def __init_output_folder():
        """
        Create test_output directory if it not exist.

        :raise OSError.
        """
        try:
            os.makedirs(TestResult.__json_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e
