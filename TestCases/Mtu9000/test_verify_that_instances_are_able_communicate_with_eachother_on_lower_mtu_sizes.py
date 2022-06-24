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

class test_verify_that_instances_are_able_communicate_with_eachother_on_lower_mtu_sizes(BaseTestCase):
    """A Basic Test Case to test_verify_that_instances_are_able_communicate_with_eachother_on_lower_mtu_sizes"""

    name = "test_verify_that_instances_are_able_communicate_with_eachother_on_lower_mtu_sizes"""

    def __init__(self):
        self.flavor_id = ""
        self.instance1 = None
        self.instance2 = None
        self.compute0 = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "mtu_size_global_default")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "mtu9000", settings.get("flavor1_name"))
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.instance1 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"), self.compute0)
        self.instance2 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_2_name"], settings["network1_name"], common_utils.ids.get("network1_id"), self.compute0)

    @pytest.mark.mtu9000
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        if self.instance1.get("floating_ip") or self.instance2.get("floating_ip") is not None:
            ping_response1 = os.system(
                "ping -c 3 " + self.instance1.get("floating_ip"))
            ping_response2 = os.system(
                "ping -c 3 " + self.instance2.get("floating_ip"))
        if ping_response1 == 0 and ping_response2 == 0:
            command = "ping -c 3 -s 64 -M do {}".format(
                self.instance2.get("floating_ip"))
            ping_test_64 = common_utils.ping_test_between_instances(self.instance1.get(
                "floating_ip"), self.instance2.get("floating_ip"), settings,  command)
            command = "ping -c 3 -s 128 -M do {}".format(
                self.instance2.get("floating_ip"))
            ping_test_128 = common_utils.ping_test_between_instances(self.instance1.get(
                "floating_ip"), self.instance2.get("floating_ip"), settings, command)
            command = "ping -c 3 -s 512 -M do {}".format(
                self.instance2.get("floating_ip"))
            ping_test_512 = common_utils.ping_test_between_instances(self.instance1.get(
                "floating_ip"), self.instance2.get("floating_ip"), settings, command)
            command = "ping -c 3 -s 1500 -M do {}".format(
                self.instance2.get("floating_ip"))
            ping_test_1500 = common_utils.ping_test_between_instances(self.instance1.get(
                "floating_ip"), self.instance2.get("floating_ip"), settings, command)
            command = "ping -c 3 -s 3000 -M do {}".format(
                self.instance2.get("floating_ip"))
            ping_test_3000 = common_utils.ping_test_between_instances(self.instance1.get(
                "floating_ip"), self.instance2.get("floating_ip"), settings, command)
            command = "ping -c 3 -s 6000 -M do {}".format(
                self.instance2.get("floating_ip"))
            ping_test_6000 = common_utils.ping_test_between_instances(self.instance1.get(
                "floating_ip"), self.instance2.get("floating_ip"), settings, command)
        assert ping_response1 == 0 and ping_response2 == 0
        assert ping_test_64[0] == True
        assert ping_test_128[0] == True
        assert ping_test_512[0] == True
        assert ping_test_1500[0] == True
        assert ping_test_3000[0] == True
        assert ping_test_6000[0] == True

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instance
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance1)
        common_utils.delete_instance(testbed_obj, self.instance2)
