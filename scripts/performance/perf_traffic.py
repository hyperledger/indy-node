"""
Created on Feb 27, 2018

@author: nhan.nguyen

This module contains class "TesterSimulateTraffic" that simulates the real time
traffic.
"""

import threading
import random
import time
import utils
import os
import asyncio
import argparse
import requests_sender
import requests_builder
import perf_add_requests

from perf_tester import Tester


class Option:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Script to simulate the traffic which will send'
                        'request to ledger in several sets. Each set contains '
                        'a specified number of requests and between two set, '
                        'the system will be delayed for a random length of'
                        ' time (from 1 to 10 seconds).\n\n',

            usage='To create 5 client to simulate the traffic in 50 seconds '
                  'and you want each set contains 100 request.'
                  '\nuse: python3.6 perf_traffic.py -c 5 -t 50 -n 100')

        parser.add_argument('-c',
                            help='Specify the number of clients '
                                 'will be simulated. Default value will be 1.',
                            action='store',
                            type=int, default=1, dest='clients')

        parser.add_argument('-n',
                            help='Number of transactions will be sent '
                                 'in a set. Default value will be 100.',
                            action='store', type=int,
                            default=100, dest='transactions_delay')

        parser.add_argument('--log',
                            help='To see all log. If this flag does not exist,'
                                 'program just only print fail message',
                            action='store_true', default=False, dest='log')

        parser.add_argument('-to',
                            help='Timeout of testing. '
                                 'Default value will be 100.',
                            action='store', type=int,
                            default=100, dest='time_out')

        parser.add_argument('--init',
                            help='To build "GET" request, we need to '
                                 'send "ADD" request first. This argument is '
                                 'the number of "ADD" request will be sent '
                                 'to ledger to make sample for "GET" requests.'
                                 ' Default value will be 100',
                            action='store', type=int,
                            default=100, dest='number_of_request_samples')

        self.args = parser.parse_args()


def catch_number_of_request_samples():
    """
    Parse number of sample of "GET" requests will be created.
    If the number is less than of equal with zero, default value (100) will be
    returned.

    :return: number of sample of "GET" requests.
    """
    import sys
    result = 100

    if "--init" in sys.argv:
        index = sys.argv.index("--init")
        if index < len(sys.argv) - 1:
            temp = -1
            try:
                temp = int(sys.argv[index + 1])
            except ValueError:
                pass
            if temp > 0:
                result = temp

    return result


class TesterSimulateTraffic(Tester):
    __sample_req_info = {}
    __kinds_of_request = ["nym", "attribute", "schema", "claim",
                          "get_nym", "get_attribute", "get_schema",
                          "get_claim"]
    __number_of_request_samples = catch_number_of_request_samples()

    def __init__(self, number_of_clients: int = 2,
                 transactions_delay: int = 100,
                 time_out: int = 300, log=False,
                 seed="000000000000000000000000Trustee1"):
        super().__init__(log=log, seed=seed)
        utils.run_async_method(
            None, TesterSimulateTraffic._prepare_samples_for_get_req,
            TesterSimulateTraffic.__number_of_request_samples)

        if time_out <= 0 or transactions_delay <= 0 or number_of_clients <= 0:
            return

        self.transactions_delay = transactions_delay
        self.time_out = time_out
        self.number_of_clients = number_of_clients
        self.current_total_txn = 0
        self.__current_time = time.time()
        self.__lock = threading.Lock()
        self.__sender = requests_sender.RequestsSender()

    async def _test(self):
        """
        Override from "Tester" class to implement testing steps.
        """
        lst_threads = list()
        self.__current_time = time.time()
        for _ in range(self.number_of_clients):
            thread = threading.Thread(target=self.__simulate_client)
            thread.setDaemon(True)
            thread.start()
            lst_threads.append(thread)

        for thread in lst_threads:
            thread.join(self.time_out * 1.1)

        self.passed_req = self.__sender.passed_req
        self.failed_req = self.__sender.failed_req
        self.fastest_txn = self.__sender.fastest_txn
        self.lowest_txn = self.__sender.lowest_txn

    def __update(self):
        """
        Synchronize within threads to update some necessary information.
        """
        self.__lock.acquire()

        if self.start_time == 0 and self.finish_time != 0:
            self.start_time = self.finish_time

        if self.current_total_txn != 0 and \
                self.current_total_txn % self.transactions_delay == 0:
            time.sleep(random.randint(1, 10))

        self.current_total_txn += 1
        self.__lock.release()

    def __simulate_client(self):
        """
        Simulate a client to create real time traffic.
        """
        loop = asyncio.new_event_loop()
        args = {"wallet_handle": self.wallet_handle,
                "pool_handle": self.pool_handle,
                "submitter_did": self.submitter_did}

        asyncio.set_event_loop(loop)
        while True:
            self.__update()
            if time.time() - self.__current_time >= self.time_out:
                break

            self.finish_time = utils.run_async_method(
                loop, TesterSimulateTraffic._build_and_send_request,
                self.__sender, args)

        loop.close()

    @staticmethod
    async def generate_sample_request_info(kind,
                                           sample_num: int = 100) -> list:
        """
        Generate sample request information.

        :param kind: kind of request.
        :param sample_num: number of samples will be generated.
        :return: a list of samples request information.
        """
        kinds = ["nym", "schema", "attribute", "claim"]

        if kind not in kinds or sample_num <= 0:
            return []

        generator = perf_add_requests.PerformanceTesterForAddingRequest(
            request_num=sample_num, request_kind=kind)

        await generator.test()
        lst_info = list()
        with open(generator.info_file_path, "r") as info_file:
            for line in info_file:
                if len(line) > 2:
                    lst_info.append(line)

        try:
            os.remove(generator.info_file_path)
        except IOError:
            pass

        return lst_info

    @staticmethod
    async def _prepare_samples_for_get_req(sample_num: int = 100):
        """
        Init samples for "GET" requests.

        :param sample_num: create a number of samples request information for
                           each kind of request (nym, attribute, claim, schema)
        """
        if TesterSimulateTraffic.__sample_req_info:
            return

        keys = ["nym", "attribute", "schema", "claim"]
        if sample_num <= 0:
            return

        for key in keys:
            TesterSimulateTraffic.__sample_req_info[key] = \
                await TesterSimulateTraffic.generate_sample_request_info(
                key, sample_num)

    @staticmethod
    def _random_req_kind():
        """
        Random choice a request kind.

        :return: request kind.
        """
        return random.choice(TesterSimulateTraffic.__kinds_of_request)

    @staticmethod
    def _random_sample_for_get_request(kind: str):
        """
        Choice randomly a sample of request info base on kind of request.

        :param kind: kind of request (get_nym, get_attribute,
                     get_claim, get_schema).
        :return: a random sample of request info.
        """
        if kind.startswith("get_"):
            return random.choice(
                TesterSimulateTraffic.__sample_req_info[kind.replace(
                    "get_", "")])
        return ""

    @staticmethod
    async def _build_and_send_request(sender, args):
        """
        Build a request and send it onto ledger.

        :param sender: send the request.
        :param args: contains some arguments to send request to ledger
                     (pool handle, wallet handle, submitter did)
        :return: response time.
        """
        kind = TesterSimulateTraffic._random_req_kind()
        data = TesterSimulateTraffic._random_sample_for_get_request(kind)

        req = await requests_builder.RequestBuilder.build_request(args, kind,
                                                                  data)

        return await sender.send_request(args, kind, req)


if __name__ == '__main__':
    opts = Option().args

    tester = TesterSimulateTraffic(number_of_clients=opts.clients,
                                   transactions_delay=opts.transactions_delay,
                                   time_out=opts.time_out, log=opts.log)

    utils.run_async_method(None, tester.test)

    elapsed_time = tester.finish_time - tester.start_time

    utils.print_client_result(tester.passed_req, tester.failed_req,
                              elapsed_time)
