"""
Created on Nov 12, 2017

@author: nghia.huynh

Containing all functions and classes to make a HTML report.
"""
import os
import json
import socket
import platform
import glob
import sys
import subprocess
import errno


class FileNameGetter:
    __FILE_NAME_GETTER = {"name": "get_name", "date": "get_date"}
    __BEGIN_DATE_PART = 24
    __END_DATE_PART = 14

    @staticmethod
    def get_part_of_name(part: str, file_name: str) -> str:
        """
        The format of "file_name" is [name]_[date]_[time].json
        Example: test_scenario_09_2017-11-21_14-20-30.json

        This function get the [name] (test_scenario_09) or the [date] (2017-11-20)

        :param part: part in file name ('date' or 'name').
        :param file_name:
        :return: the part in file name that you want.
        """
        if part in FileNameGetter.__FILE_NAME_GETTER:
            getter = getattr(FileNameGetter, FileNameGetter.__FILE_NAME_GETTER[part])
            return getter(file_name)

        return ""

    @staticmethod
    def get_name(file_name: str) -> str:
        """
        The format of "file_name" is [name]_[date]_[time].json
        Example: test_scenario_09_2017-11-21_14-20-30.json

        This function get the [name] (test_scenario_09)

        :param file_name:
        :return: name of test.
        """
        if file_name is None or len(file_name) < (FileNameGetter.__BEGIN_DATE_PART + 1):
            return ""
        return file_name[0:(len(file_name) - (FileNameGetter.__BEGIN_DATE_PART + 1))]

    @staticmethod
    def get_date(file_name: str) -> str:
        """
        The format of "file_name" is [name]_[date]_[time].json
        Example: test_scenario_09_2017-11-21_14-20-30.json

        This function get the [date] (2017-11-20)

        :param file_name:
        :return: date of test.
        """
        if file_name is None or len(file_name) < FileNameGetter.__BEGIN_DATE_PART:
            return ""
        return file_name[(len(file_name) - FileNameGetter.__BEGIN_DATE_PART):
                         (len(file_name) - FileNameGetter.__END_DATE_PART)]


class FileNameFilter:
    __FILTER_SUPPORTED = ["name", "date"]
    __FILTER_REGEX = "&"
    __VALUE_REGEX = "="

    def __init__(self, list_filter: dict):
        self.__filter = list_filter

    def do_filter(self, list_file_name) -> list:
        """
        :param list_file_name: list to filter.
        :return: list of file name that satisfy condition.
        """
        result = []
        for file_name in list_file_name:
            if self.__check(os.path.basename(file_name)):
                result.append(file_name)

        return result

    def get_filter(self):
        return self.__filter

    def __check(self, file_name: str) -> bool:
        """
        Check if the file name satisfy the condition.

        :param file_name:
        :return: True if file_name satisfy all filters.
                 False if file_name does not satisfy at least one filter.
        """
        temp = {}
        for f in FileNameFilter.__FILTER_SUPPORTED:
            temp[f] = True

        for f in self.__filter.keys():
            if f in temp:
                part = FileNameGetter.get_part_of_name(part=f, file_name=file_name)
                if not part or not self.__filter[f] or not part.startswith(self.__filter[f]):
                    temp[f] = False

        return all(value is True for value in temp.values())


def get_version(program: str) -> str:
    """
    Return version of a program.

    :param program: program's name.
    :return: version.
    """
    cmd = "dpkg -l | grep '{}'".format(program)
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    (out, err) = process.communicate()
    result = out.decode()
    version = result.split()

    if len(version) >= 3:
        return version[2]
    return "Cannot find version for '{}'".format(program)


class HTMLReporter:
    __default_dir = os.path.join(os.path.dirname(__file__), "..")

    __json_dir = __default_dir + "/test_output/test_results/"

    __report_dir = __default_dir + "/reporter_summary_report/"

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
        """
        Generating the statistics table.
        :param suite_name:
        """
        self.__suite_name = self.__suite_name.replace("s_name", suite_name)
        self.__statictics_table = self.__statictics_table.replace("plan_name", suite_name)

    def make_configurate_table(self):
        """
        Generating the configuration table.
        """
        self.__configuration_table = self.__configuration_table.replace("host_name", socket.gethostname())
        self.__configuration_table = self.__configuration_table.replace("os_name", os.name + platform.system() +
                                                                        platform.release())
        self.__configuration_table = self.__configuration_table.replace("v_plenum", get_version("indy-plenum"))
        self.__configuration_table = self.__configuration_table.replace("v_anoncreds", get_version("indy-anoncreds"))
        self.__configuration_table = self.__configuration_table.replace("v_indynode", get_version("indy-node"))
        self.__configuration_table = self.__configuration_table.replace("v_sovrin", get_version("sovrin"))

    def make_report_content_by_list(self, list_json: list):
        """
        Generating the report content by reading all json file within the inputted path
        :param list_json:
        """
        if not list_json:
            return

        passed = 0
        failed = 0
        total = 0

        for js in list_json:
            with open(js) as json_file:
                json_text = json.load(json_file)

                # summary item
                testcase = json_text['testcase']
                result = json_text['result']
                starttime = json_text['starttime']
                duration = json_text['duration']

                # statictic Table items
                total = total + int(duration)
                if result == "Passed":
                    passed = passed + 1

                    temp_testcase = self.__passed_testcase_template
                    temp_testcase = temp_testcase.replace("tc_name", testcase)
                    temp_testcase = temp_testcase.replace("tc_starttime", starttime)
                    temp_testcase = temp_testcase.replace("tc_duration", str(duration))
                    # Add passed test case into  table
                    self.__passed_testcase_table = self.__passed_testcase_table + temp_testcase

                elif result == "Failed":
                    failed = failed + 1

                    temp_testcase = self.__failed_testcase_template
                    temp_testcase = temp_testcase.replace("tc_name", testcase)
                    temp_testcase = temp_testcase.replace("tc_starttime", starttime)
                    temp_testcase = temp_testcase.replace("tc_duration", str(duration))
                    temp_testcase = temp_testcase.replace("tc_link", testcase.replace(" ", ""))
                    # Add failed test case into  table
                    self.__failed_testcase_table = self.__failed_testcase_table + temp_testcase

                    test_log = self.__table_test_log
                    test_log = test_log.replace("test_name", testcase)
                    test_log = test_log.replace("tc_link", testcase.replace(" ", ""))

                    self.__table_test_log_content = self.__table_test_log_content + test_log

                    # loop for each step
                    for i in range(0, len(json_text['run'])):
                        if json_text['run'][i]['status'] == "Passed":
                            temp = self.__passed_test_log
                        else:
                            temp = self.__failed_test_log
                            temp = temp.replace("error_message", json_text['run'][i]['message'])

                        temp = temp.replace("step_num", str(i + 1))
                        temp = temp.replace("step_name", json_text['run'][i]['step'])
                        temp = temp.replace("step_status", json_text['run'][i]['status'])
                        self.__table_test_log_content = self.__table_test_log_content + temp

                    self.__table_test_log_content = self.__table_test_log_content + self.__end_table + self.__go_to_summary

        self.__statictics_table = self.__statictics_table.replace("plan_name", str(passed))
        self.__statictics_table = self.__statictics_table.replace("passed_num", str(passed))
        self.__statictics_table = self.__statictics_table.replace("failed_num", str(failed))
        self.__statictics_table = self.__statictics_table.replace("total_time", str(total))

    def __init__(self):
        self.__filter = None
        HTMLReporter.__init_report_folder()

    def generate_report(self, file_filter: dict):
        print("Generating a html report...")
        self.__filter = FileNameFilter(file_filter)
        list_file_name = glob.glob(HTMLReporter.__json_dir + "*.json")
        list_file_name = self.__filter.do_filter(list_file_name)
        report_file_name = HTMLReporter.__make_report_name(self.__filter.get_filter())
        self.make_suite_name(report_file_name)
        self.make_configurate_table()
        self.make_report_content_by_list(list_file_name)

        # Write to file.
        print(("Refer to " + self.__report_dir + "{}.html").format(report_file_name))
        f = open((self.__report_dir + "{}.html").format(report_file_name), 'w')
        f.write(
            self.__head +
            self.__suite_name +
            self.__configuration_table +
            self.__statictics_table +
            self.__summary_head +
            self.__begin_summary_content +
            self.__passed_testcase_table +
            self.__end_summary_content +
            self.__begin_summary_content +
            self.__failed_testcase_table +
            self.__end_summary_content +
            self.__end_table +
            self.__test_log_head +
            self.__table_test_log_content +
            self.__end_file)

        f.close()

    @staticmethod
    def __make_report_name(json_filter: dict) -> str:
        """
        Generate report name from filter.
        :param json_filter:
        :return: report name.
        """
        name = ""
        if "name" in json_filter:
            name += json_filter["name"]

        if "date" in json_filter:
            if name is not "":
                name += "_"
            name = "{}{}".format(name, json_filter["date"])

        if name is "":
            name = "Summary"

        return name

    @staticmethod
    def __init_report_folder():
        """
        Create reporter_summary_report directory if it not exist.
        :raise OSError.
        """
        try:
            os.makedirs(HTMLReporter.__report_dir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e


def print_help():
    content = "\nGenerate html report from serveral json files\n\n" \
              "-help: print help\n\n" \
              "-name: test name of json files that will be selected to make report\n" \
              "-date: date of test of json files that will be selected to make report\n" \
              "Example: python3.6 html_reporter.py -name Test09 -date 2017-11-20\n"
    print(content)


if __name__ == "__main__":
    __FILTER_SUPPORTED = {"-date": "date", "-name": "name"}
    args = sys.argv
    if "-help" in args:
        print_help()
        exit(0)

    # Get argument from sys.argv to make filters
    reporter = HTMLReporter()
    json_filter = {}
    for key in __FILTER_SUPPORTED:
        if key in args:
            index = args.index(key)
            if index + 1 < len(args):
                json_filter[__FILTER_SUPPORTED[key]] = args[index + 1]

    # Generate a html report
    reporter.generate_report(json_filter)
