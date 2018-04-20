"""
Created on Feb 2, 2018

@author: nhan.nguyen

This module contains class "RequestBuilder" that builds requests
base on king of them.
"""

import utils
import json
import os
import time

from indy import ledger, signus


class RequestBuilder:
    def __init__(self, req_info_file_path=None, log=False):
        self.log = log
        self.req_info_file_path = req_info_file_path
        self.path = os.path.join(os.path.dirname(__file__), 'temp')
        utils.create_folder(self.path)
        pass

    async def build_several_adding_req_to_files(self, args: dict, req_kind,
                                                number_of_file, number_of_req):
        """
        Build several ADD request and write them to list of temporary files.
        :param args: contain all necessary arguments to build a request
                    (pool_handle, wallet_handle, submitter_did)
        :param req_kind: kind of ADD request (schema, nym, attribute, claim).
        :param number_of_file: number of temporary file you want to store
                               requests. Number of request will be divided
                               equally among temp files.
        :param number_of_req: total of requests you want to build.
        :return: list of temporary file name.
        """
        utils.print_header("\n\tBuilding several {} requests..."
                           .format(req_kind))
        if not self.log:
            utils.start_capture_console()
        works = RequestBuilder.divide(number_of_file, number_of_req)

        req_builder = RequestBuilder.get_adding_req_builder(req_kind)

        files = list()
        print(self.req_info_file_path)
        req_info_file = open(self.req_info_file_path, "w")
        for work in works:
            file_name = utils.generate_random_string(
                suffix='_{}.txt'.format(str(time.time())))
            file_name = os.path.join(self.path, file_name)
            temp_file = open(file_name, "w")
            utils.print_ok_green(str(work))
            for i in range(work):
                req = await req_builder(args)
                print(req[1], file=req_info_file)
                print(req[0], file=temp_file)
            temp_file.close()
            files.append(file_name)
        req_info_file.close()

        if not self.log:
            utils.stop_capture_console()

        utils.print_header("\n\tBuilding request complete")

        return files

    async def build_several_getting_req_to_files(self, args, req_kind,
                                                 number_of_file,
                                                 data_files: list):
        """
        Build several ADD request and write them to list of temporary files.
        :param args: contain all necessary arguments to build a request
                    (pool_handle, wallet_handle, submitter_did)
        :param req_kind: kind of ADD request (schema, nym, attribute, claim).
        :param number_of_file: number of temporary file you want to store
                               requests. Number of request will be divided
                               equally among temp files.
        :param data_files: list file that store request information.
        :return:
        """
        utils.print_header("\n\tBuilding several get {} requests..."
                           .format(req_kind))
        if not self.log:
            utils.start_capture_console()

        req_builder = RequestBuilder.get_getting_req_builder(req_kind)

        files = list()
        lst_opened_files = list()
        file_iter = 0

        for data_file_path in data_files:
            with open(data_file_path, 'r') as data_file:
                for line in data_file:
                    if str(line) == '\n':
                        continue
                    req = await req_builder(args, json.dumps(line))
                    if file_iter >= number_of_file:
                        file_iter = 0
                    if file_iter >= len(lst_opened_files):
                        file_name = utils.generate_random_string(
                            suffix='_{}.txt'.format(str(time.time())))
                        temp_file = open(file_name, 'w')
                        lst_opened_files.append(temp_file)
                        files.append(file_name)

                    print(req, file=lst_opened_files[file_iter])
                    file_iter += 1

        for file in lst_opened_files:
            file.close()

        if not self.log:
            utils.stop_capture_console()

        utils.print_header("\n\tBuilding request complete")

        return files

    @staticmethod
    async def build_request(args: dict, kind: str, request_info: str=""):
        """
        Build a request from data base on kind of request.

        :param args: contains some arguments to build request
                     (submitter did, wallet handle, pool handle).
        :param kind: kind of request (get_claim, get_attribute, get_nym,
                     get_schema, schema, nym, attribute, claim).
        :param request_info: to build "GET" request.
        :return: built request.
        """
        if kind.startswith("get_"):
            kind = kind.replace("get_", "")
            builder = RequestBuilder.get_getting_req_builder(kind)
            return await builder(args, request_info)
        else:
            builder = RequestBuilder.get_adding_req_builder(kind)
            result = await builder(args)
            return result[0]

    @staticmethod
    def divide(number_of_file, number_of_req):
        """
        Divide request to temporary file.
        If there is 10 request but you just want to divide them fo 3 files.
        The number of requests in each file are 4, 3, 3.
        :param number_of_file:
        :param number_of_req:
        :return:
        """
        fixed_works = number_of_req // number_of_file
        extra_works = number_of_req % number_of_file

        works = list()
        for _ in range(number_of_file):
            temp = fixed_works
            if extra_works > 0:
                temp += 1
                extra_works -= 1
            works.append(temp)

        return works

    @staticmethod
    def get_adding_req_builder(kind):
        """
        Get ADD request builder.

        :param kind: kind of request.
        :return: ADD request builder.
        """
        if kind == 'nym':
            builder = RequestBuilder.build_nym_req
        elif kind == 'schema':
            builder = RequestBuilder.build_schema_req
        elif kind == 'attribute':
            builder = RequestBuilder.build_attribute_req
        elif kind == 'claim':
            builder = RequestBuilder.build_claim_req
        else:
            builder = None

        return builder

    @staticmethod
    def get_getting_req_builder(kind):
        """
        Get GET request builder.

        :param kind: kind of request.
        :return: GET request builder.
        """
        if kind == 'nym':
            builder = RequestBuilder.build_get_nym_req
        elif kind == 'schema':
            builder = RequestBuilder.build_get_schema_req
        elif kind == 'attribute':
            builder = RequestBuilder.build_get_attribute_req
        elif kind == 'claim':
            builder = RequestBuilder.build_get_claim_req
        else:
            builder = None

        return builder

    @staticmethod
    async def build_nym_req(args: dict):
        """
        Build ADD nym request.

        :param args: arguments for building ADD nym request.
        :return: nym request, request info.
        """
        wallet_handle = args['wallet_handle']
        submitter_did = args['submitter_did']
        try:
            utils.print_header_for_step('Create did')
            did, _, = await signus.create_and_store_my_did(wallet_handle, '{}')

            # Send NYM to ledger
            utils.print_header("\n======== Build NYM request ========")
            nym_req = await ledger.build_nym_request(submitter_did, did, None,
                                                     None, None)
            req_info = json.dumps({'kind': 'nym', 'data': {'target_did': did}})
            req = json.dumps({'request': nym_req})

            return req, req_info

        except Exception as e:
            utils.force_print_error_to_console(
                "Cannot build nym request. Skip building...")
            utils.force_print_error_to_console(str(e))
            return ""

    @staticmethod
    async def build_schema_req(args: dict):
        """
        Build ADD schema request.

        :param args: arguments for building ADD schema request.
        :return: schema request, request info.
        """
        submitter_did = args['submitter_did']
        try:
            data = {
                'name': utils.generate_random_string(prefix='test'),
                'version': '1.0',
                'attr_names': ['test']
            }

            utils.print_header("\n======= Build schema request =======")
            schema_req = await ledger.build_schema_request(submitter_did,
                                                           json.dumps(data))

            del data['attr_names']
            data['dest'] = submitter_did
            req_info = json.dumps({'kind': 'schema', 'data': data})
            req = json.dumps({'request': schema_req})

            return req, req_info

        except Exception as e:
            utils.force_print_error_to_console(
                "Cannot build schema request. Skip building...")
            utils.force_print_error_to_console(str(e))
            return ""

    @staticmethod
    async def build_attribute_req(args: dict):
        """
        Build ADD attribute request.

        :param args: arguments to build ADD attribute request.
        :return: attribute request, request info.
        """
        pool_handle = args['pool_handle']
        wallet_handle = args['wallet_handle']
        submitter_did = args['submitter_did']
        try:
            utils.print_header("\n======= Create did =======")
            did, verkey = await signus.create_and_store_my_did(wallet_handle,
                                                               '{}')

            utils.print_header("\n======= Build nym request =======")
            nym_req = await ledger.build_nym_request(submitter_did, did,
                                                     verkey,
                                                     None, None)

            utils.print_header("\n======= Send nym request =======")
            await ledger.sign_and_submit_request(pool_handle, wallet_handle,
                                                 submitter_did, nym_req)

            data = {'endpoint': {'ha': '127.0.0.1:5555'}}

            utils.print_header("\n======= Build attribute request =======")
            attr_req = await ledger.build_attrib_request(did, did, None,
                                                         json.dumps(data),
                                                         None)

            req_info = json.dumps({'kind': 'attribute',
                                   'data': {'target_did': did,
                                            'raw_name': 'endpoint'}})
            req = json.dumps({'request': attr_req, 'submitter_did': did})

            return req, req_info

        except Exception as e:
            utils.force_print_error_to_console(
                "Cannot build attribute request. Skip building...")
            utils.force_print_error_to_console(str(e))
            return ""

    @staticmethod
    async def build_claim_req(args: dict):
        """
        Build ADD claim request.

        :param args: arguments to build ADD claim request.
        :return: claim request, request info.
        """
        import string
        import random
        pool_handle = args['pool_handle']
        wallet_handle = args['wallet_handle']
        submitter_did = args['submitter_did']
        try:
            utils.print_header("\n======= Create did =======")
            did, verkey = await signus.create_and_store_my_did(wallet_handle,
                                                               '{}')

            utils.print_header("\n======= Build nym request =======")
            nym_req = await ledger.build_nym_request(submitter_did, did,
                                                     verkey,
                                                     None, None)

            utils.print_header("\n======= Send nym request =======")
            await ledger.sign_and_submit_request(pool_handle, wallet_handle,
                                                 submitter_did, nym_req)

            seq_no = random.randint(1, 1000000)
            signature_type = 'CL'
            data = {"primary": {
                "n": utils.generate_random_string(characters=string.digits),
                "s": utils.generate_random_string(characters=string.digits),
                "rms": utils.generate_random_string(characters=string.digits),
                "r": {"name": utils.generate_random_string(
                    characters=string.digits)},
                "rctxt": utils.generate_random_string(
                    characters=string.digits),
                "z": utils.generate_random_string(characters=string.digits)}}

            utils.print_header("\n======= Build claim request =======")
            claim_req = await ledger.build_claim_def_txn(did, seq_no,
                                                         signature_type,
                                                         json.dumps(data))

            req_info = json.dumps({'kind': 'claim',
                                   'data': {'issuer_did': did,
                                            'seq_no': seq_no,
                                            'signature_type': signature_type}})
            req = json.dumps({'request': claim_req, 'submitter_did': did})

            return req, req_info

        except Exception as e:
            utils.force_print_error_to_console(
                "Cannot build claim request. Skip building...")
            utils.force_print_error_to_console(str(e))
            return ""

    @staticmethod
    async def build_get_nym_req(args, data):
        """
        Build GET nym request.

        :param args: arguments to build GET nym request.
        :param data: ADD nym request info.
        :return: GET nym request.
        """
        if not data:
            return ''

        submitter_did = args['submitter_did']
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(data, str):
                data = json.loads(data)
            if data['kind'] != 'nym':
                return ''

            utils.print_header_for_step('Build get nym request')
            target_did = data['data']['target_did']
            get_nym_req = await ledger.build_get_nym_request(submitter_did,
                                                             target_did)

            return get_nym_req
        except Exception as e:
            utils.force_print_error_to_console(
                "Cannot build get NYM request. Skip building...")
            utils.force_print_error_to_console(str(e))
            return ''

    @staticmethod
    async def build_get_attribute_req(args, data):
        """
        Build GET attribute request.

        :param args: arguments to build GET attribute request.
        :param data: ADD attribute request info.
        :return: GET attribute request.
        """

        if not data:
            return ''
        submitter_did = args['submitter_did']
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(data, str):
                data = json.loads(data)
            if data['kind'] != 'attribute':
                return ''

            utils.print_header_for_step('Build get attribute request')
            target_did = data['data']['target_did']
            raw_name = data['data']['raw_name']
            get_attr_req = await ledger.build_get_attrib_request(submitter_did,
                                                                 target_did,
                                                                 raw_name)
            return get_attr_req
        except Exception as e:
            utils.force_print_error_to_console(
                "Cannot build get attribute request. Skip building...")
            utils.force_print_error_to_console(str(e))
            return ''

    @staticmethod
    async def build_get_schema_req(args, data):
        """
        Build GET schema request.

        :param args: arguments to build GET schema request.
        :param data: ADD schema request info.
        :return: GET schema request.
        """
        if not data:
            return ''
        submitter_did = args['submitter_did']
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(data, str):
                data = json.loads(data)
            if data['kind'] != 'schema':
                return ''

            utils.print_header_for_step('Build get schema request')
            dest = data['data']['dest']
            schema_data = {'name': data['data']['name'],
                           'version': data['data']['version']}
            get_schema_req = await ledger.build_get_schema_request(
                submitter_did, dest, json.dumps(schema_data))

            return get_schema_req
        except Exception as e:
            utils.force_print_error_to_console(
                "Cannot build get schema request. Skip building...")
            utils.force_print_error_to_console(str(e))
            return ''

    @staticmethod
    async def build_get_claim_req(args, data):
        """
        Build GET claim request.

        :param args: arguments to build GET claim request.
        :param data: ADD claim request info.
        :return: GET claim request.
        """
        if not data:
            return ''
        submitter_did = args['submitter_did']
        try:
            if isinstance(data, str):
                data = json.loads(data)
            if isinstance(data, str):
                data = json.loads(data)
            if data['kind'] != 'claim':
                return ''

            utils.print_header_for_step('Build get schema request')
            issuer_did = data['data']['issuer_did']
            seq_no = data['data']['seq_no']
            signature_type = data['data']['signature_type']
            get_claim_req = await ledger.build_get_claim_def_txn(
                submitter_did, seq_no, signature_type, issuer_did)

            return get_claim_req
        except Exception as e:
            utils.force_print_error_to_console(
                "Cannot build get claim request. Skip building...")
            utils.force_print_error_to_console(str(e))
            return ''
