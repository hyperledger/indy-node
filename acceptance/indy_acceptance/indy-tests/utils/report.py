'''
Created on Nov 9, 2017

@author: nhan.nguyen
'''

import json
import time
import os


class TestReport:
    result_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_results/"

    def __init__(self, test_case_name):
        self.__error_id = 1
        self.__test_result = {}
        self.__test_result[KeyWord.TEST_CASE] = test_case_name
        self.__test_result[KeyWord.RESULT] = KeyWord.PASSED
        self.__test_result[KeyWord.START_TIME] = str(time.strftime("%Y%m%d_%H-%M-%S"))

    def set_result(self, result):
        self.__test_result[KeyWord.RESULT] = result

    def set_duration(self, duration):
        self.__test_result[KeyWord.DURATION] = duration

    def set_step_status(self, step, name, message):
        content = "{0}: {1}".format(str(name), str(message))
        step = KeyWord.ERROR + str(step)
        self.__test_result[step] = content

    def write_result_to_file(self):
        filename = "{0}{1}_{2}.json".format(TestReport.result_dir, self.__test_result[KeyWord.TEST_CASE],
                                            self.__test_result[KeyWord.START_TIME])
        with open(filename, "w+") as outfile:
            json.dump(self.__test_result, outfile, ensure_ascii=False)

    def set_test_failed(self):
        self.set_result(KeyWord.FAILED)

    def set_test_passed(self):
        self.set_test_passed(KeyWord.PASSED)

    def add_error(self, name, message):
        self.set_step_status(self.__error_id, name, message)
        self.__error_id += 1


    @staticmethod
    def change_result_dir(new_dir):
        TestReport.result_dir = new_dir


class KeyWord:
    TEST_CASE = "testcase"
    RESULT = "result"
    START_TIME = "starttime"
    DURATION = "duration"
    ERROR = "error"
    PASSED = "Passed"
    FAILED = "Failed"
