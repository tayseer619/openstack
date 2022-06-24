import logging
import sys
import time
import os
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class TestVerifyCommunicationOfTwoOvsOffloadInstanceOnSameComputeAndSameNetwork(BaseTestCase):
    """A Basic Test Case for offload VM's internal communication testing"""

    name = "Test to verify offload VM's internal communication testing"

    def __init__(self):
        self.flavor_id = ""
        self.instance1 = None
        self.instance2 = None
        self.compute0 = ""
        self.compute1 = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):

        self.check = common_utils.check_if_feature_is_enabled("sriov_enable")
        common_utils.validate_osp_environment(testbed_obj)
        # get ip of compute nodes
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute1 = common_utils.get_compute_name(testbed_obj, "compute-1")
        # create flavor
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "sriov", settings.get("flavor1_name"))
        # create instance1
        self.instance1 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], 
            common_utils.ids.get("network1_id"), self.compute0, "No", "sriov", common_utils.ids.get("subnet1_id"))
        # create instance2
        self.instance2 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_2_name"], settings["network2_name"], common_utils.ids.get("network2_id"), self.compute1)

    @pytest.mark.sriov
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
    
        assert self.flavor_id is not None
        # wait for some time to appear traffic on representor port as instances are already pinged during creation
        logging.debug(
            "Wait for traffic to appear om reprsenter port as instances are already pinged during creation")
        time.sleep(60)
        # ping test instance
        if self.instance1.get("status") == "active" and self.instance2.get("status") == "active":
            ping_response1 = os.system(
                "ping -c 3 " + self.instance1.get("floating_ip"))
            ping_response2 = os.system(
                "ping -c 3 " + self.instance2.get("floating_ip"))
        if ping_response1 == 0 and ping_response2 == 0:
            ping_test1 = common_utils.ping_test_between_instances(
                self.instance1.get("floating_ip"), self.instance2.get("floating_ip"), settings)
            ping_test2 = common_utils.ping_test_between_instances(
                self.instance2.get("floating_ip"), self.instance1.get("floating_ip"), settings)
        assert ping_response1 == 0 and ping_response2 == 0
        assert ping_test1[0] == True and ping_test2[0] == True

    def post_testcase(self, testbed_obj):

        common_utils.post_check(self.check)
        # delete flavor
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        # delete instance1
        common_utils.delete_instance(testbed_obj, self.instance1)
        # delete instance2
        common_utils.delete_instance(testbed_obj, self.instance2)
        # delete port1
        common_utils.delete_port(testbed_obj, self.instance1.get("port_id"))
        # delete port2
        common_utils.delete_port(testbed_obj, self.instance2.get("port_id"))
