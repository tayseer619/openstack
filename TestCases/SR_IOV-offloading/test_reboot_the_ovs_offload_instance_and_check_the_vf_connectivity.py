import logging
import sys
import utils
import os
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class TestVerifyOvsOffloadInstanceCreation(BaseTestCase):
    """A Basic Test Case for offload VM testing"""

    name = "Test to verify OVS offloading instance creation"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("smart_nic")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        # create flavor
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "offloading", settings.get("flavor1_name"))
        # create instance
        self.instance = common_utils.create_instance(
                testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], 
                common_utils.ids.get("network1_id"), None, "No", "smart_nic", common_utils.ids.get("subnet1_id"))

    @pytest.mark.offloading
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        assert self.flavor_id is not None
        assert self.instance.get("status") == "active"
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # ping test instance
        if self.instance.get("floating_ip") is not None:
            ping_response = os.system(
                "ping -c 3 " + self.instance.get("floating_ip"))
            reboot_server = common_utils.reboot_server(
                overcloud_ep, overcloud_token, self.instance.get("id"))
            server_bulid_wait = common_utils.server_build_wait(
                overcloud_ep, overcloud_token, [self.instance.get("id")])
            ping_test = common_utils.ping_test_between_instances(
                self.instance.get("floating_ip"), "8.8.8.8", settings)
        assert ping_response == 0
        assert ping_test[0] == True

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
        # delete port1
        common_utils.delete_port(testbed_obj, self.instance.get("port_id"))
