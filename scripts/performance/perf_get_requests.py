"""
Created on Feb 2, 2018

@author: nhan.nguyen

This module contains class "PerformanceTesterGetSentRequestFromLedger" that
executes submit several "GET" requests testing.
"""

import os
import sys
import glob
import utils
import argparse
import perf_tester
import requests_builder
import requests_sender


class Options:
    def __init__(self):
        parser = argparse.ArgumentParser(
            description='Script to feed multiple NYMs from files created '
                        'by the \'perf_add_requests.py\'')

        parser.add_argument('-d',
                            help='Specify the directory that contains the .txt'
                                 ' files with requests info.  The default '
                                 'directory is set to the "request_info" '
                                 'directory in the scripts current working '
                                 'directory.', action='store',
                            default=os.path.join(os.path.dirname(__file__),
                                                 "request_info"),
                            dest='info_dir')

        parser.add_argument('-k',
                            help='Kind of request to be sent. '
                                 'The default value will be "nym"',
                            action='store',
                            choices=['nym', 'schema', 'attribute', 'claim'],
                            default='nym', dest='kind')

        parser.add_argument('-s',
                            help='Specify the number of threads'
                                 'The default value will be 1', action='store',
                            type=int, default=1, dest='thread_num')

        parser.add_argument('--log',
                            help='To see all log. If this flag does not exist,'
                                 'program just only print fail message',
                            action='store_true', default=False, dest="log")

        self.args = parser.parse_args()


class PerformanceTesterGetSentRequestFromLedger(perf_tester.Tester):
    def __init__(self, info_dir=os.path.join(os.path.dirname(__file__),
                                             "request_info"),
                 kind='nym', thread_num=1, log=False):
        super().__init__(log, '000000000000000000000000Trustee1')
        if thread_num <= 0:
            self.thread_num = 1
        else:
            self.thread_num = thread_num
        self.info_dir = info_dir
        self.req_kind = kind
        self.pool_handle = self.wallet_handle = 0

        self.threads = list()
        self.works_per_threads = list()
        self.lst_req_info = list()

    async def _test(self):
        """
        Override from "Tester" class to implement testing steps.
        """

        info_files = self.__collect_requests_info_files()

        # 1. Create ledger config from genesis txn file
        # 2. Open pool
        # 3. Create My Wallet and Get Wallet Handle
        # 4. Create the DID to use

        args = {'submitter_did': self.submitter_did,
                'pool_handle': self.pool_handle,
                'wallet_handle': self.wallet_handle}

        # 5. Build getting request from info from files.
        builder = requests_builder.RequestBuilder(None, self.log)
        req_files = await builder.build_several_getting_req_to_files(
            args, self.req_kind, self.thread_num, info_files)

        # 6. Submit getting request to ledger.
        sender = requests_sender.RequestsSender(self.log)
        try:
            await sender.submit_several_reqs_from_files(args, req_files,
                                                        self.req_kind)
        except Exception:
            pass

        self.passed_req, self.failed_req = sender.passed_req, sender.failed_req
        self.start_time, self.finish_time = (sender.start_time,
                                             sender.finish_time)
        self.fastest_txn = sender.fastest_txn
        self.lowest_txn = sender.lowest_txn

    def __collect_requests_info_files(self):
        """
        Collect all request info file from directory.

        :return: list of file name.
        """
        lst_files = glob.glob(os.path.join(
            self.info_dir, '{}_requests_info*{}'.format(self.req_kind,
                                                        '.txt')))
        if not lst_files:
            utils.force_print_error_to_console(
                'Cannot found any request info. '
                'Skip sending get request... Abort')
            sys.exit(1)

        return lst_files


if __name__ == '__main__':
    options = Options()
    opts = options.args
    tester = PerformanceTesterGetSentRequestFromLedger(opts.info_dir,
                                                       opts.kind,
                                                       opts.thread_num,
                                                       opts.log)

    # Start the method
    elapsed_time = utils.run_async_method(None, tester.test)

    utils.print_client_result(tester.passed_req, tester.failed_req,
                              elapsed_time)
