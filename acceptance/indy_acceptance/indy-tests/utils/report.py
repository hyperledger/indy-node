"""
Created on Nov 9, 2017

@author: nhan.nguyen
"""

import json
import time
import os
import sys
import logging
import datetime
import socket
import platform


class KeyWord:
    TEST_CASE = "testcase"
    RESULT = "result"
    START_TIME = "starttime"
    DURATION = "duration"
    RUN = "run"
    STEP = "step"
    STATUS = "status"
    MESSAGE = "message"


class Status:
    PASSED = "Passed"
    FAILED = "Failed"


class Printer(object):
    """
    Class that write content to several file.
    Use this class when you want to write log
    not only on console but only on some other files.
    """
    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        """
        Write a content into several files.

        :param obj: content you want to write.
        """
        for f in self.files:
            f.write(obj)
            f.flush()  # Want this content is displayed immediately on file

    def flush(self):
        for f in self.files:
            f.flush()


class TestReport:
    __default_result_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_results/"
    __result_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_results/"
    __log_level = logging.DEBUG

    def __init__(self, test_case_name):
        """
        Constructor of a TestReport instance.

        :param test_case_name:
        """
        self.__test_result = {}  # Store information of a test case
        self.__run = []  # Store information of steps in test case
        self.__test_result[KeyWord.TEST_CASE] = test_case_name
        self.__test_result[KeyWord.RESULT] = Status.PASSED
        self.__test_result[KeyWord.START_TIME] = str(time.strftime("%Y%m%d_%H-%M-%S"))

    def set_result(self, result):
        """
        Set a result (PASSED or FAILED) for test case.

        :param result:
        """
        self.__test_result[KeyWord.RESULT] = result

    def set_duration(self, duration):
        """
        Set duration for test.

        :param duration: (second)
        """
        self.__test_result[KeyWord.DURATION] = round(duration * 1000)

    def set_step_status(self, step_summary: str, status: str = Status.PASSED, message: str = None):
        """
        Set status and message for specify step.

        :param step_summary: title of step.
        :param status: PASSED or FAILED.
        :param message: anything that involve to step like Exception, Log,...
        """
        temp = {KeyWord.STEP: step_summary, KeyWord.STATUS: status, KeyWord.MESSAGE: message}
        self.__run.append(temp)

    def setup_json_report(self):
        """
        Create the result folder for json and log file
        """
        self.__result_dir = self.__create_result_folder()
        self.__file_path = "{0}/{1}_{2}".format(self.__result_dir, self.__test_result[KeyWord.TEST_CASE],
                                                self.__test_result[KeyWord.START_TIME])
        self.__log = open(self.__file_path + ".log", "w")
        self.__original_stdout = sys.stdout
        sys.stdout = Printer(sys.stdout, self.__log)
        logging.basicConfig(stream=sys.stdout, level=TestReport.__log_level)

    def write_result_to_file(self):
        """
        Write the result as json and log file to folder.
        If test status is PASSED, delete log file.
        """
        filename = self.__file_path + ".json"
        self.__log.close()
        if self.__test_result[KeyWord.RESULT] == Status.PASSED:
            if os.path.isfile(self.__file_path + ".log"):
                os.remove(self.__file_path + ".log")
        sys.stdout = self.__original_stdout

        self.__test_result[KeyWord.RUN] = self.__run
        with open(filename, "w+") as outfile:
            json.dump(self.__test_result, outfile, ensure_ascii=False, indent=2)

    def set_test_failed(self):
        """
        Set status of test to FAILED.
        """
        self.set_result(Status.FAILED)

    def get_result_folder(self) -> str:
        """
        Return the path that the result will be writen.
        :return: the result dir
        """
        return self.__result_dir

    def set_test_passed(self):
        """
        Set status of test to PASSED.
        """
        self.set_test_passed(Status.PASSED)

    def __create_result_folder(self) -> str:
        """
        Check if the result folder is exist.
        Create folder if it is not exist.

        :return: result folder path.
        """
        temp_dir = TestReport.__result_dir
        if temp_dir == TestReport.__default_result_dir:
            temp_dir = "{0}{1}_{2}".format(temp_dir, self.__test_result[KeyWord.TEST_CASE],
                                           self.__test_result[KeyWord.START_TIME])
        if not os.path.exists(temp_dir):
            try:
                os.makedirs(temp_dir)
            except IOError as E:
                print(str(E))
                raise E

        return temp_dir

    @staticmethod
    def change_result_dir(new_dir: str):
        """
        It will be used when you want to run multiple test case.
        Change the path where the tests save the result.

        :param new_dir:
        """
        if new_dir != "":
            if not new_dir.endswith("/"):
                new_dir += "/"
            TestReport.__result_dir = new_dir


class HTMLReport:
    __head = """<html>
            <head>
             <meta http-equiv="Content-Type" content="text/html; charset=windows-1252">
                <title>Summary Report</title>
                <style type="text/css">table {
                    margin-bottom: 10px;
                    border-collapse: collapse;
                    empty-cells: show
                }   

                th, td {
                    border: 1px solid #009;
                    padding: .25em .5em
                }

                th {
                    text-align: left
                }

                te {
                    border: 1px solid #009;
                    padding: .25em .5em
                    text-align: left
                    color_name: red
                }

                td {
                    vertical-align: top
                }

                table a {
                    font-weight: bold
                }

                .stripe td {
                    background-color: #E6EBF9
                }

                .num {
                    text-align: right
                }

                .passedodd td {
                    background-color: #3F3
                }

                .passedeven td {
                    background-color: #0A0
                }

                .skippedodd td {
                    background-color: #DDD
                }

                .skippedeven td {
                    background-color: #CCC
                }

                .failedodd td, .attn {
                    background-color: #F33
                }

                .failedeven td, .stripe .attn {
                    background-color: #D00
                }

                .stacktrace {
                    white-space: pre;
                    font-family: monospace
                }

                .totop {
                    font-size: 85%;
                    text-align: center;
                    border-bottom: 2px solid #000
                }</style>
            </head>"""

    __end_file = """</html>"""

    __suite_name = """<h3>s_name</h3>"""

    __configuration_table = """<table id="configuration">
            <tbody>
            <tr>
                <th>Run machine</th>
                <td>host_name</td>            
            </tr>
            <tr>
                <th>OS</th>
                <td>os_name</td>
            </tr>
            <tr>
                <th>indy - plenum</th>
                <td>v_plenum</td>            
            </tr>
             <tr>
                <th>indy - anoncreds</th>
                <td>v_anoncreds</td>            
            </tr>
            <tr>
                <th>indy - node</th>
                <td>v_indynode</td>            
            </tr>
            <tr>
                <th>sovrin</th>
                <td>v_sovrin</td>            
            </tr>
            </tbody>
        </table>"""

    __statictics_table = """<table border='1' width='800'>
            <tbody>
            <tr>
                <th>Test Plan</th>
                <th># Passed</th>       
                <th># Failed</th>
                <th>Time (ms)</th>
            </tr>
            <tr>
                <td>plan_name</td>
                <td class="num">passed_num</td>
                <td class="num">failed_num</td>            
                <td class="num">total_time</td>
            </tr>
            </tbody>
        </table>"""

    __passed_testcase_template = """<tr class="passedeven">
                                           <td rowspan="1">tc_name</td>
                                           <td>Passed</td>
                                           <td rowspan="1">tc_starttime</td>
                                           <td rowspan="1">tc_duration</td>
                                       </tr>"""

    __failed_testcase_template = """<tr class="failedeven">
                                            <td rowspan="1">tc_name</td>
                                            <td><a href='#tc_link'>Failed</a></td>
                                            <td rowspan="1">tc_starttime</td>
                                            <td rowspan="1">tc_duration</td>
                                        </tr>"""

    __summary_head = """<h2>Test Summary</h2>
            <table id="summary" border='1' width='800'>
            <thead>
            <tr>
                <th>Test Case</th>
                <th>Status</th>
                <th>Start Time</th>
                <th>Duration (ms)</th>
            </tr>
            </thead>"""

    __go_to_summary = """<a href = #summary>Back to summary.</a>"""

    __begin_summary_content = """ 
            <tbody>
            <tr>
                <th colspan="4"></th>
            </tr>"""

    __end_summary_content = """</tbody>"""

    __end_table = """ </table> """

    __passed_testcase_table = """ """

    __failed_testcase_table = """ """

    __test_log_head = """<h2>Test Execution Logs</h2>"""

    __table_test_log = """<h3 id = "tc_link">test_name</h3>
                            <table id="execution_logs" border='1' width='800'>"""

    __table_test_log_content = """ """

    __passed_test_log = """
            <tr>
                <td><font color="green">step_num : step_name :: step_status</font></td>       
            </tr>"""

    __failed_test_log = """
            <tr>
                <td><font color="red">step_num : step_name :: step_status
                <br>Traceback: error_message</br>
                </font>
                </td>            
            </tr>
            """

    def make_suite_name(self, suite_name):
        # os.path.basename(__file__)
        """
        Generating the statictics table
        :param suite_name:
        """
        time = datetime.datetime.now().time()
        date = datetime.datetime.today().strftime('%Y%m%d')
        HTMLReport.__suite_name = HTMLReport.__suite_name.replace("s_name", "Summary_" + date + "_" + str(time))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("plan_name", suite_name + "_" + date + "_" + str(time))

    def make_configurate_table(self):
        """
        Generating the configuration table
        """
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("host_name", socket.gethostname())
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("os_name", os.name + platform.system() + platform.release())
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("v_plenum", "1.1.27")
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("v_anoncreds", "1.0.10")
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("v_indynode", "1.1.43")
        HTMLReport.__configuration_table = HTMLReport.__configuration_table.replace("v_sovrin", "1.1.6")
        # dpkg -l | grep 'indy-plenum'
        # dpkg -l | grep 'indy-anoncreds'
        # dpkg -l | grep 'indy-node'
        # dpkg -l | grep 'sovrin'

    def make_report_content(self, path_to_json):
        """
        Generating the report content by reading all json file within the inputted path
        :param path_to_json:
        """

        # this finds our json files
        json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
        passed = 0
        failed = 0
        total = 0

        for index, js in enumerate(json_files):
            with open(os.path.join(path_to_json, js)) as json_file:
                json_text = json.load(json_file)

                # summary item
                testcase = json_text['testcase']
                result = json_text['result']
                starttime = json_text['starttime']
                duration = json_text['duration']

                # staticticTable items
                total = total + int(duration)
                if result == "Passed":
                    passed = passed + 1

                    temp_testcase = HTMLReport.__passed_testcase_template
                    temp_testcase = temp_testcase.replace("tc_name", testcase)
                    temp_testcase = temp_testcase.replace("tc_starttime", starttime)
                    temp_testcase = temp_testcase.replace("tc_duration", str(duration))
                    # Add passed test case into  table
                    HTMLReport.__passed_testcase_table = HTMLReport.__passed_testcase_table + temp_testcase

                elif result == "Failed":
                    failed = failed + 1

                    temp_testcase = HTMLReport.__failed_testcase_template
                    temp_testcase = temp_testcase.replace("tc_name", testcase)
                    temp_testcase = temp_testcase.replace("tc_starttime", starttime)
                    temp_testcase = temp_testcase.replace("tc_duration", str(duration))
                    temp_testcase = temp_testcase.replace("tc_link", testcase.replace(" ", ""))
                    # Add failed test case into  table
                    HTMLReport.__failed_testcase_table = HTMLReport.__failed_testcase_table + temp_testcase

                    test_log = HTMLReport.__table_test_log
                    test_log = test_log.replace("test_name", testcase)
                    test_log = test_log.replace("tc_link", testcase.replace(" ", ""))

                    HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + test_log

                    # loop for each step
                    for i in range(0, len(json_text['run'])):
                        if (json_text['run'][i]['status'] == "Passed"):
                            temp = HTMLReport.__passed_test_log
                        else:
                            temp = HTMLReport.__failed_test_log
                            temp = temp.replace("error_message", json_text['run'][i]['message'])

                        temp = temp.replace("step_num", str(i + 1))
                        temp = temp.replace("step_name", json_text['run'][i]['step'])
                        temp = temp.replace("step_status", json_text['run'][i]['status'])
                        HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + temp

                    HTMLReport.__table_test_log_content = HTMLReport.__table_test_log_content + HTMLReport.__end_table + HTMLReport.__go_to_summary

        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("plan_name", str(passed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("passed_num", str(passed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("failed_num", str(failed))
        HTMLReport.__statictics_table = HTMLReport.__statictics_table.replace("total_time", str(total))

    def make_html_report(self, json_folder, suite_name):
        """
        Generating completely the report.
        :param json_folder:
        :param suite_name:
        """

        self.make_suite_name(suite_name)
        self.make_configurate_table()
        self.make_report_content(json_folder)

        # Write to file.
        print("Refer to " + json_folder + '/summary.html')
        f = open(json_folder + '/summary.html', 'w')
        f.write(
            HTMLReport.__head + HTMLReport.__suite_name + HTMLReport.__configuration_table + HTMLReport.__statictics_table + HTMLReport.__summary_head + HTMLReport.__begin_summary_content + HTMLReport.__passed_testcase_table + HTMLReport.__end_summary_content + HTMLReport.__begin_summary_content + HTMLReport.__failed_testcase_table + HTMLReport.__end_summary_content + HTMLReport.__end_table + HTMLReport.__test_log_head +
            HTMLReport.__table_test_log_content + HTMLReport.__end_file)

        f.close()

    def __init__(self):
        print("Generating a html report...")

    def create_result_folder(self, test_name):
        """
        Creating the folder for html summary report.
        :param test_name:
        :return: the actual folder path
        """
        temp_dir = os.path.join(os.path.dirname(__file__), "..") + "/test_results/"
        temp_dir = "{0}{1}_{2}".format(temp_dir, test_name, str(time.strftime("%Y%m%d_%H-%M-%S")))
        if not os.path.exists(temp_dir):
            try:
                os.makedirs(temp_dir)
            except IOError as E:
                print(str(E))
                raise E
        return temp_dir
