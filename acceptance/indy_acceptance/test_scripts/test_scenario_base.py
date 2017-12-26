"""
Created on Nov 22, 2017

@author: khoi.ngo

Containing the test base class.
"""
import inspect
import os
import time

from indy_acceptance.utilities import common
from indy_acceptance.utilities import constant
from indy_acceptance.utilities import utils
from indy_acceptance.utilities.constant import Color
from indy_acceptance.utilities.logger import Logger
from indy_acceptance.utilities.result import TestResult, Status
from indy_acceptance.utilities.step import Steps
from indy_acceptance.utilities.utils import generate_random_string,\
                                    run_async_method, make_final_result


class TestScenarioBase:
    """
    Test base....
    All test scenario should inherit from this class.
    This class controls the work flow and hold some general test data for
    test scenarios that inherit it.
    """
    pool_name = generate_random_string("test_pool")
    wallet_name = generate_random_string("test_wallet")
    pool_handle = 0
    wallet_handle = 0
    pool_genesis_txn_file = constant.pool_genesis_txn_file
    logger = None
    steps = None
    test_result = None
    test_name = ""

    def init_data_test(self):
        """
        Init test data.
        If the test case need some extra test date
        then just override this method.
        """
        self.test_name = os.path.splitext(
            os.path.basename(inspect.getfile(self.__class__)))[0]
        self.test_result = TestResult(self.test_name)
        self.steps = Steps()
        self.logger = Logger(self.test_name)

    async def execute_precondition_steps(self):
        """
         Execute pre-condition of test scenario.
         If the test case need some extra step in pre-condition
         then just override this method.
        """
        common.clean_up_pool_and_wallet_folder(
            self.pool_name, self.wallet_name)

    async def execute_postcondition_steps(self):
        """
        Execute post-condition of test scenario.
        If the test case need some extra step in post-condition
        then just override this method.
        """
        await common.clean_up_pool_and_wallet(self.pool_name, self.pool_handle,
                                              self.wallet_name,
                                              self.wallet_handle)

    async def execute_test_steps(self):
        """
        The method where contain all main script of a test scenario.
        All test scenario inherit TestScenarioBase have to override this method
        """
        pass

    def execute_scenario(self):
        """
        Execute the test scenario and control the work flow of
        this test scenario.
        """
        begin_time = time.time()
        self.init_data_test()
        utils.print_with_color("\nTest case: {} ----> started\n"
                               .format(self.test_name), Color.BOLD)
        try:
            run_async_method(self.execute_precondition_steps)
            run_async_method(self.execute_test_steps)
        except Exception as e:
            message = constant.EXCEPTION.format(str(e))
            utils.print_error("\n{}\n".format(str(message)))
            self.steps.get_last_step().set_status(Status.FAILED, message)
        finally:
            try:
                run_async_method(self.execute_postcondition_steps)
            except Exception as e:
                utils.print_error("\n{}\n".format(str(type(e))))
            make_final_result(self.test_result, self.steps.get_list_step(),
                              begin_time, self.logger)
            test_result_status = self.test_result.get_test_status()
            utils.print_test_result(self.test_name, test_result_status)
