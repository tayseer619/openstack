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

class validate_ovs_virtual_nics_are_assigned_with_correct_ips_on_instance_reboot(BaseTestCase):
    """A Basic Test Case to validate_ovs_virtual_nics_are_assigned_with_correct_ips_on_instance_reboot"""

    name = "validate_ovs_virtual_nics_are_assigned_with_correct_ips_on_instance_reboot"""

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
            overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
            overcloud_token = common_utils.get_overcloud_token(testbed_obj)
            ping_response = os.system(
                "ping -c 3 " + self.instance.get("floating_ip"))
            reboot_server = common_utils.reboot_server(
                overcloud_ep, overcloud_token, self.instance.get("id"))
            server_build_wait = common_utils.server_build_wait(
                overcloud_ep, overcloud_token, [self.instance.get("id")])
        assert self.instance.get("status") == "active"
        assert ping_response == 0

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instance
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
        common_utils.delete_port(testbed_obj, self.instance.get("port_id"))
