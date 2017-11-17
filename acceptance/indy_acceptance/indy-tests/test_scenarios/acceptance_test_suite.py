import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from test_scenarios import test_scenario_02, test_scenario_03, test_scenario_04, test_scenario_09, test_scenario_11
from utils.report import HTMLReport

def main():
    test_name = "Acceptance_Test"
    html_report = HTMLReport()
    suite_folder_path = html_report.create_result_folder(test_name)
    print("make_html_report>>>>>>>>>>>>>>>>>>>>>>>>" + suite_folder_path)

    #list of test
    test_scenario_02.test(suite_folder_path)
    test_scenario_03.test(suite_folder_path)
    test_scenario_04.test(suite_folder_path)
    test_scenario_09.test(suite_folder_path)
    test_scenario_11.test(suite_folder_path)

    print("make_html_report>>>>>>>>>>>>>>>>>>>>>>>>"+suite_folder_path)
    html_report.make_html_report(suite_folder_path,test_name)

if __name__ == '__main__':
    main()