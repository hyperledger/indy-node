"""
Created on Feb 2, 2018

@author: nhan.nguyen

This module contains class "PerformanceTestRunner" that executes the test base
on the mode that user pass to system.
"""

import os
import argparse
import time
import threading
import asyncio
import sys
import perf_add_requests
import perf_get_requests
import perf_load
import perf_traffic
import requests_sender
import utils


class Options:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='This script will execute the test base on the '
                        'mode that user passes to system.')

        parser.add_argument('-a',
                            help='Use this parameter to start adding '
                                 'request performance testing',
                            action='store_true',
                            default=False, required=False, dest='adding')

        parser.add_argument('-g',
                            help='Use this parameter to start getting '
                                 'request performance testing',
                            action='store_true',
                            default=False, required=False, dest='getting')

        parser.add_argument('-l',
                            help='Use this parameter to perform load test',
                            action='store_true',
                            default=False, required=False, dest='loading')

        parser.add_argument('-t',
                            help='Use this parameter to simulate traffic',
                            action='store_true',
                            default=False, required=False,
                            dest='simulate_traffic')

        parser.add_argument('-c',
                            help='Number of client you want to create. '
                                 'Default value will be 1',
                            default=1, type=int, required=False,
                            dest='clients')

        parser.add_argument('-d',
                            help='Directory you want to store requests '
                                 'info when sending adding request. '
                                 'If you start getting request testing, '
                                 'program will collect info from '
                                 'this dir instead.'
                                 'Default value will be {}'.
                            format(os.path.join(os.path.dirname(__file__),
                                                "request_info")),
                            default=os.path.join(os.path.dirname(__file__),
                                                 "request_info"),
                            required=False,
                            dest='info_dir')

        parser.add_argument('-n',
                            help='How many transactions you want to submit to '
                                 'ledger when starting adding requests.'
                                 'If you start getting request testing, '
                                 'this arg will be ignore.'
                                 'In case that you use flag "-t", this '
                                 'parameter will be the number of '
                                 'transactions of a set.'
                                 'Default value will be 100',
                            default=100, type=int, required=False, dest='txns')

        parser.add_argument('-s',
                            help='Number of thread will '
                                 'be created by each client.'
                                 'Default value is 1',
                            default=1, type=int, required=False,
                            dest='thread_num')

        parser.add_argument('-k',
                            help='Kind of request to be sent. '
                                 'The default value will be "nym"',
                            action='store',
                            choices=['nym', 'schema', 'attribute', 'claim'],
                            default='nym', dest='kind', required=False)

        parser.add_argument('--log',
                            help='To see all log. If this flag does not exist,'
                                 'program just only print fail message',
                            action='store_true', default=False, dest='log',
                            required=False)

        parser.add_argument('-to',
                            help='Timeout of testing. This flag '
                                 'just visible in two mode "-l" and "-t"'
                                 'Default value will be 100.',
                            action='store', type=int,
                            default=100, dest='time_out', required=False)

        parser.add_argument('--init',
                            help='To build "GET" request, we need to '
                                 'send "ADD" request first. This argument is '
                                 'the number of "ADD" request will be sent '
                                 'to ledger to make sample for "GET" requests.'
                                 ' Default value will be 100',
                            action='store', type=int, required=False,
                            default=100, dest='number_of_request_samples')

        self.args = parser.parse_args()


class PerformanceTestRunner:
    modes = ["-t", "-l", "-a", "-g"]

    def __init__(self):
        self.options = Options().args

        self.tester = None

        temp = 0
        for mode in PerformanceTestRunner.modes:
            if mode in sys.argv:
                temp += 1

        if temp == 0:
            utils.print_error(
                'Cannot determine any kind of request for testing')
            utils.print_error(
                'May be you missing arguments "-a" or "-b" or "-t" or "-l"')
            sys.exit(1)

        if temp > 1:
            utils.force_print_error_to_console(
                '"-a" and "-g" and "-t" and "-l" '
                'cannot exist at the same time\n')
            sys.exit(1)

        self.list_tester = list()

        self.start_time = self.finish_time = 0
        self.lowest = self.fastest = 0
        self.passed_req = self.failed_req = 0
        self.result_path = os.path.join(os.path.dirname(__file__), 'results')
        utils.create_folder(self.result_path)
        log_path = os.path.join(os.path.dirname(__file__), 'logs')
        utils.create_folder(log_path)

        now = time.strftime("%d-%m-%Y_%H-%M-%S")
        self.result_path = os.path.join(self.result_path,
                                        'result_{}.txt'.format(now))

        log_path = os.path.join(
            log_path, self.create_log_file_name())
        requests_sender.RequestsSender.init_log_file(log_path)
        utils.create_folder(self.options.info_dir)

    def run(self):
        """
        Run the test.
        """

        utils.print_header("Start {}...\n".format(self.get_kind_of_test()))

        if not self.options.log:
            utils.start_capture_console()
        self.start_time = time.time()
        if self.options.adding or self.options.getting \
                and self.options.clients > 1:
            self.start_tester_in_thread()
        else:
            self.list_tester.append(self.create_tester())
            utils.run_async_method(None, self.list_tester[-1].test)

        self.finish_time = time.time()

        utils.stop_capture_console()
        self.collect_result()
        with open(self.result_path, 'w') as result:
            self.write_result(result)
        self.write_result(sys.stdout)
        requests_sender.RequestsSender.close_log_file()

        utils.print_header("\nFinish {}\n".format(self.get_kind_of_test()))

    def collect_result(self):
        """
        Collect all necessary information to make the result.
        """
        self.passed_req = self.failed_req = 0
        for tester in self.list_tester:
            self.failed_req += tester.failed_req
            self.passed_req += tester.passed_req

        self.find_lowest_and_fastest_transaction()

        self.find_start_and_finish_time()

    def write_result(self, result_file):
        """
        Compute and write result to file.

        :param result_file: the file that result will be written.
        """
        total_time = self.finish_time - self.start_time
        hours = total_time / 3600
        minutes = total_time / 60 % 60
        seconds = total_time % 60

        ttl_txns = int(self.passed_req + self.failed_req)

        ttl_seconds = total_time
        if ttl_seconds == 0:
            print('\nThere is no request sent.\n', file=result_file)
            return
        txns_per_second = int(ttl_txns / ttl_seconds)
        txns_per_client = ttl_txns / self.options.clients

        print("\n -----------  Total time to run the test: %dh:%dm:%ds" % (
            hours, minutes, seconds) + "  -----------", file=result_file)
        print("\n Kind: " + self.get_kind_of_test(), file=result_file)
        print("\n Client(s): " + str(self.options.clients), file=result_file)
        print("\n Fastest transaction (individual thread): {} second(s)".
              format(str(self.fastest)),
              file=result_file)
        print("\n Lowest transaction (individual thread): {} second(s)".
              format(str(self.lowest)), file=result_file)
        print("\n Transaction per client: " + str(int(txns_per_client)),
              file=result_file)
        print("\n Total requested transactions: " + str(int(ttl_txns)),
              file=result_file)
        print("\n Total passed transactions: " + str(self.passed_req),
              file=result_file)
        print("\n Total failed transactions: " + str(self.failed_req),
              file=result_file)
        print("\n Average time of a transaction "
              "(multiple threads): {} second(s)".
              format(str((self.finish_time - self.start_time) / ttl_txns)),
              file=result_file)
        print("\n Estimated transactions per second: " + str(txns_per_second),
              file=result_file)

    def find_lowest_and_fastest_transaction(self):
        """
        Find lowest and fastest transactions.
        """
        self.lowest = self.list_tester[0].lowest_txn
        self.fastest = self.list_tester[0].fastest_txn
        for tester in self.list_tester:
            temp_lowest = tester.lowest_txn
            temp_fastest = tester.fastest_txn
            if self.lowest < temp_lowest:
                self.lowest = temp_lowest
            if self.fastest > temp_fastest:
                self.fastest = temp_fastest

    def find_start_and_finish_time(self):
        """
        Find the earliest time that a client is started and latest time that a
        client is finished.
        """
        self.start_time = self.list_tester[0].start_time
        self.finish_time = self.list_tester[0].finish_time

        for tester in self.list_tester:
            if self.start_time > tester.start_time:
                self.start_time = tester.start_time

            if self.finish_time < tester.finish_time:
                self.finish_time = tester.finish_time

    def start_tester_in_thread(self):
        """
        Create thread and start all the tester in list.
        """
        threads = list()
        for _ in range(self.options.clients):
            tester = self.create_tester()
            self.list_tester.append(tester)
            thread = threading.Thread(target=self.run_tester_in_thread,
                                      kwargs={'tester': tester})
            thread.daemon = True
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    @staticmethod
    def run_tester_in_thread(tester):
        """
        Execute testing function of tester.
        """
        loop = asyncio.new_event_loop()
        utils.run_async_method(loop, tester.test)
        loop.close()

    def create_tester(self):
        """
        Create tester base mode "-a", "-t", "-g", "-l".

        :return: tester
        """
        if self.options.adding:
            return perf_add_requests.PerformanceTesterForAddingRequest(
                self.options.info_dir, self.options.txns, self.options.kind,
                thread_num=self.options.thread_num, log=self.options.log)

        elif self.options.getting:
            return perf_get_requests.PerformanceTesterGetSentRequestFromLedger(
                self.options.info_dir, self.options.kind,
                self.options.thread_num, log=self.options.log)

        elif self.options.loading:
            return perf_load.TesterSimulateLoad(
                self.options.clients, self.options.txns,
                self.options.time_out, self.options.log)

        elif self.options.simulate_traffic:
            return perf_traffic.TesterSimulateTraffic(
                self.options.clients, self.options.txns,
                self.options.time_out, self.options.log)

        return None

    def get_kind_of_test(self) -> str:
        """
        Return kind of testing.

        :return: kind of test.
        """
        if self.options.adding:
            return "sending 'ADD {}' requests".format(self.options.kind)
        elif self.options.getting:
            return "sending 'GET {}' requests".format(self.options.kind)
        elif self.options.simulate_traffic:
            return "simulating traffic"
        elif self.options.loading:
            return "performing load test"

        return ""

    def create_log_file_name(self):
        """
        Create and return log file name.

        :return: log file name.
        """
        temp = 'get' if self.options.getting else ""
        now = time.strftime("%d-%m-%Y_%H-%M-%S")

        if self.options.adding or self.options.getting:
            return '{}-perf-{}{}_{}.log'.format(self.options.clients, temp,
                                                self.options.kind, now)
        elif self.options.simulate_traffic:
            return '{}-{}_{}.log'.format(self.options.clients,
                                         'simulate_traffic', now)
        else:
            return '{}-{}_{}.log'.format(self.options.clients,
                                         'perform_load_test', now)


if __name__ == '__main__':
    PerformanceTestRunner().run()
