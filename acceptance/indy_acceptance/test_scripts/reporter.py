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
import subprocess
import errno
import argparse
import time


def get_version(program: str) -> str:
    """
    Return version of a program.

    :param program: program's name.
    :return: version.
    """
    cmd = "dpkg -l | grep '{}'".format(program)
    process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE,
                               stdin=subprocess.PIPE)
    (out, _) = process.communicate()
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
             <meta http-equiv="Content-Type" content="text/html;
             charset=windows-1252">
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

    __suite_name = """<h3>{}</h3>"""

    __configuration_table = """<table id="configuration">
            <tbody>
            <tr>
                <th>Run machine</th>
                <td>{}</td>
            </tr>
            <tr>
                <th>OS</th>
                <td>{}</td>
            </tr>
            <tr>
                <th>indy - plenum</th>
                <td>{}</td>
            </tr>
             <tr>
                <th>indy - anoncreds</th>
                <td>{}</td>
            </tr>
            <tr>
                <th>indy - node</th>
                <td>{}</td>
            </tr>
            <tr>
                <th>sovrin</th>
                <td>{}</td>
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
                <td>{}</td>
                <td class="num">{}</td>
                <td class="num">{}</td>
                <td class="num">{}</td>
            </tr>
            </tbody>
        </table>"""

    __passed_testcase_template = """<tr class="passedeven">
                                           <td rowspan="1">{}</td>
                                           <td>Passed</td>
                                           <td rowspan="1">{}</td>
                                           <td rowspan="1">{}</td>
                                       </tr>"""

    __failed_testcase_template = """<tr class="failedeven">
                                            <td rowspan="1">{}</td>
                                            <td><a href='#{}'>Failed</a></td>
                                            <td rowspan="1">{}</td>
                                            <td rowspan="1">{}</td>
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

    __table_test_log = """<h3 id = "{}">{}</h3>
                            <table id="execution_logs"
                            border='1' width='800'>"""

    __table_test_log_content = """ """

    __passed_test_log = """
            <tr>
                <td><font color="green">{} : {} :: {}</font></td>
            </tr>"""

    __failed_test_log = """
            <tr>
                <td><font color="red">{} : {} :: {}
                <br>Traceback: {}</br>
                </font>
                </td>
            </tr>
            """

    def make_suite_name(self, suite_name):
        """
        Generating the statistics table.
        :param suite_name:
        """
        self.__suite_name = self.__suite_name.format(suite_name)

    def make_configurate_table(self):
        """
        Generating the configuration table.
        """
        self.__configuration_table = \
            self.__configuration_table.format(socket.gethostname(),
                                              platform.system() +
                                              platform.release(),
                                              get_version("indy-plenum"),
                                              get_version("indy-anoncreds"),
                                              get_version("indy-node"),
                                              get_version("sovrin"))

    def make_report_content_by_list(self, list_json: list, suite_name):
        """
        Generating the report content by reading all json file
        within the inputted path
        :param list_json:
        :param suite_name:
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
                    temp_testcase = temp_testcase.format(testcase, starttime,
                                                         str(duration))

                    # Add passed test case into  table
                    self.__passed_testcase_table = \
                        self.__passed_testcase_table + temp_testcase

                elif result == "Failed":
                    failed = failed + 1

                    temp_testcase = self.__failed_testcase_template
                    temp_testcase = \
                        temp_testcase.format(testcase,
                                             testcase.replace(" ", ""),
                                             starttime, str(duration))

                    # Add failed test case into  table
                    self.__failed_testcase_table = \
                        self.__failed_testcase_table + temp_testcase

                    test_log = self.__table_test_log
                    test_log = test_log.format(testcase.replace(" ", ""),
                                               testcase)

                    self.__table_test_log_content = \
                        self.__table_test_log_content + test_log

                    # loop for each step
                    for i in range(0, len(json_text['run'])):
                        step = json_text['run'][i]['step']
                        status = json_text['run'][i]['status']
                        if json_text['run'][i]['status'] == "Passed":
                            temp = self.__passed_test_log.format(str(i + 1),
                                                                 step, status)
                        else:
                            message = json_text['run'][i]['message']
                            temp = self.__failed_test_log.format(str(i + 1),
                                                                 step, status,
                                                                 message)

                        self.__table_test_log_content = \
                            self.__table_test_log_content + temp

                    self.__table_test_log_content = \
                        self.__table_test_log_content + self.__end_table +\
                        self.__go_to_summary

        self.__statictics_table = self.__statictics_table.format(suite_name,
                                                                 str(passed),
                                                                 str(failed),
                                                                 str(total))

    def __init__(self):
        HTMLReporter.__init_report_folder()

    def generate_report(self, file_filter):
        print("Generating a html report...")
        report_file_name = HTMLReporter.__make_report_name()
        file_filter = "*" if not file_filter else file_filter
        list_file_name = glob.glob(self.__json_dir + file_filter + ".json")
        self.make_suite_name(report_file_name)
        self.make_configurate_table()
        self.make_report_content_by_list(list_file_name, report_file_name)

        # Write to file.
        print(("Refer to " + self.__report_dir + "{}.html").
              format(report_file_name))
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
    def __make_report_name() -> str:
        """
        Generate report name.
        :return: report name.
        """
        name = "Summary_{}".format(str(time.strftime("%Y-%m-%d_%H-%M-%S")))

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


if __name__ == "__main__":
    reporter = HTMLReporter()
    # Get argument from sys.argv to make filters
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-n", "--name", dest="name", nargs="?",
                            default=None, help="filter json file by name")
    args = arg_parser.parse_args()
    json_name = args.name

    # Generate a html report
    reporter.generate_report(json_name)
