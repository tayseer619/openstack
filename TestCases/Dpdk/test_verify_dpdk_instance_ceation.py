import logging
import sys
import os
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_dpdk_instance_creation(BaseTestCase):
    """A Basic Test Case to verify_dpdk_instance_creation"""

    name = "Demo test_verify_dpdk_instance_creation"""

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "ovs_dpdk_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "dpdk", settings.get("flavor1_name"))
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.dpdk
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        if self.instance.get("floating_ip") is not None:
            ping_response = os.system(
                "ping -c 3 " + self.instance.get("floating_ip"))
        assert self.instance.get("status") == "active"
        assert ping_response == 0

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instance
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
