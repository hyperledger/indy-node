"""
Created on Feb 2, 2018

@author: nhan.nguyen

This module contains class "PerformanceTesterForAddingRequest" that executes
submit several "ADD" requests testing.
"""

import os
import time
import argparse
import utils
import threading
import requests_builder
import requests_sender
import perf_tester


class Option:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Script to create multiple requests '
                        'and store their info in .txt files to be  '
                        'used by the \'perf_get_requests.py\' script.\n\n',
            usage='To create 500 NYMs in the default '
                  '\'request_info\' directory '
                  '\nuse: python3.6 perf_add_requests.py -p '
                  'testPool -n 500 -i 000000000000000000000000Steward1 -s 1')

        parser.add_argument('-d',
                            help='Specify the directory location to store '
                                 'information of sent request as .txt files.  '
                                 'The default directory is set to the '
                                 'directory in this scripts '
                                 'current working '
                                 'directory.', action='store',
                            default=os.path.join(os.path.dirname(__file__),
                                                 "request_info"),
                            dest='info_dir')

        parser.add_argument('-n',
                            help='Specify the number of requests to be '
                                 'created.  The default value will be 100',
                            action='store', type=int, default=100,
                            dest='number_of_requests')

        parser.add_argument('-k',
                            help='Kind of request to be sent. '
                                 'The default value will be "nym"',
                            action='store',
                            choices=['nym', 'schema', 'attribute', 'claim'],
                            default='nym', dest='kind')

        parser.add_argument('-i',
                            help='Specify the role to use to create the NYMs. '
                                 ' The default trustee ID will be  used',
                            action='store',
                            default='000000000000000000000000Steward1',
                            dest='seed')

        parser.add_argument('-s',
                            help='Specify the number of threads'
                                 'The default value will be 1', action='store',
                            type=int, default=1, dest='thread_num')

        parser.add_argument('--log',
                            help='To see all log. If this flag does not exist,'
                                 'program just only print fail message',
                            action='store_true', default=False, dest='log')

        self.args = parser.parse_args()


class PerformanceTesterForAddingRequest(perf_tester.Tester):
    def __init__(self, info_dir=os.path.join(os.path.dirname(__file__),
                                             "request_info"),
                 request_num=100, request_kind='nym',
                 seed='000000000000000000000000Trustee1', thread_num=1,
                 log=False):
        super().__init__(log, seed)

        self.info_dir = info_dir
        self.req_num = request_num
        self.req_kind = request_kind
        if thread_num <= 0:
            self.thread_num = 1
        elif request_num < thread_num:
            self.thread_num = request_num
        else:
            self.thread_num = thread_num

        self.info_file_path = "{}_{}_{}.txt".format(
            self.req_kind + "_requests_info", str(threading.get_ident()),
            time.strftime("%d-%m-%Y_%H-%M-%S"))

        self.info_file_path = os.path.join(self.info_dir,
                                           self.info_file_path)
        self.req_info = list()
        self.threads = list()

        utils.create_folder(self.info_dir)

    async def _test(self):
        """
        Override from "Tester" class to implement testing steps.
        """
        # 1. Create pool config.
        # 2. Open pool ledger
        # 3. Create My Wallet and Get Wallet Handle
        # 4 Create and sender DID

        args = {'wallet_handle': self.wallet_handle,
                'pool_handle': self.pool_handle,
                'submitter_did': self.submitter_did}

        # 5. Build requests and save them in to files.
        builder = requests_builder.RequestBuilder(self.info_file_path,
                                                  self.log)

        req_files = await builder.build_several_adding_req_to_files(
            args, self.req_kind, self.thread_num, self.req_num)

        # 6. Sign and submit several request into ledger.
        sender = requests_sender.RequestsSender(self.log)
        try:
            await sender.sign_and_submit_several_reqs_from_files(
                args, req_files, self.req_kind)
        except Exception as e:
            utils.force_print_error_to_console(str(e) + "\n")
        self.passed_req, self.failed_req = sender.passed_req, sender.failed_req

        self.start_time, self.finish_time = (sender.start_time,
                                             sender.finish_time)
        self.fastest_txn = sender.fastest_txn
        self.lowest_txn = sender.lowest_txn


if __name__ == '__main__':
    options = Option()
    opts = options.args
    tester = PerformanceTesterForAddingRequest(
        opts.info_dir, opts.number_of_requests, opts.kind, opts.seed,
        opts.thread_num, opts.log)

    utils.run_async_method(None, tester.test)

    elapsed_time = tester.finish_time - tester.start_time

    utils.print_client_result(tester.passed_req, tester.failed_req,
                              elapsed_time)
