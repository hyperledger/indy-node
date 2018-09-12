"""
Created on Feb 27, 2018

@author: nhan.nguyen

This module contains class "TesterSimulateLoad" that performs load testing.
"""

import threading
import time
import utils
import asyncio
import argparse
import random
import requests_builder
import requests_sender

from perf_tester import Tester


class Option:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Script to perform load testing. Send a specified '
                        'number of "ADD" request in a specified time.\n\n',

            usage='To create 5 client to send 100 requests '
                  'with time out is 50 seconds '
                  '\nuse: python3.6 perf_traffic.py -c 5 -t 50 -n 100')

        parser.add_argument('-c',
                            help='Specify the number of clients '
                                 'will be simulated. Default value will be 1.',
                            action='store',
                            type=int, default=1, dest='clients')

        parser.add_argument('-n',
                            help='Number of transactions will be sent '
                                 'Default value will be 100.',
                            action='store', type=int,
                            default=100, dest='transactions_num')

        parser.add_argument('--log',
                            help='To see all log. If this flag does not exist,'
                                 'program just only print fail message',
                            action='store_true', default=False, dest='log')

        parser.add_argument('-to',
                            help='Timeout of testing. '
                                 'Default value will be 100.',
                            action='store', type=int,
                            default=100, dest='time_out')

        self.args = parser.parse_args()


class TesterSimulateLoad(Tester):
    __kinds_of_request = ["nym", "attribute", "schema", "claim"]

    def __init__(self, number_of_clients: int=2,
                 number_of_transactions: int=1000,
                 time_out: int=300, log=False,
                 seed="000000000000000000000000Trustee1"):
        super().__init__(log=log, seed=seed)

        self.time_out = time_out
        self.number_of_clients = number_of_clients
        self.number_of_transactions = number_of_transactions
        self.__current_time = time.time()
        self.__current_total_txn = 0
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

        :return: True if can update, otherwise, return False.
        """
        self.__lock.acquire()
        if self.start_time == 0 and self.finish_time != 0:
            self.start_time = self.finish_time
        self.__current_total_txn += 1

        result = (self.__current_total_txn > self.number_of_transactions)

        self.__lock.release()

        return result

    def __simulate_client(self):
        """
        Simulate the client to perform the test.
        """
        loop = asyncio.new_event_loop()
        args = {"wallet_handle": self.wallet_handle,
                "pool_handle": self.pool_handle,
                "submitter_did": self.submitter_did}

        asyncio.set_event_loop(loop)
        while time.time() - self.__current_time < self.time_out:
            if self.__update():
                break

            self.finish_time = utils.run_async_method(
                loop, TesterSimulateLoad._build_and_send_request,
                self.__sender, args)

        loop.close()

    @staticmethod
    def _random_req_kind():
        """
        Choice a request kind randomly.

        :return: request kind.
        """
        return random.choice(TesterSimulateLoad.__kinds_of_request)

    @staticmethod
    async def _build_and_send_request(sender, args):
        """
        Build a request and send it onto ledger.

        :param sender: send the request.
        :param args: contains some arguments to send request to ledger
                     (pool handle, wallet handle, submitter did)
        :return: response time.
        """
        kind = TesterSimulateLoad._random_req_kind()

        req = await requests_builder.RequestBuilder.build_request(args, kind)

        return await sender.send_request(args, kind, req)


if __name__ == '__main__':
    opts = Option().args

    tester = TesterSimulateLoad(time_out=opts.time_out,
                                number_of_clients=opts.clients,
                                log=opts.log,
                                number_of_transactions=opts.transactions_num)

    utils.run_async_method(None, tester.test)

    elapsed_time = tester.finish_time - tester.start_time

    utils.print_client_result(tester.passed_req, tester.failed_req,
                              elapsed_time)
