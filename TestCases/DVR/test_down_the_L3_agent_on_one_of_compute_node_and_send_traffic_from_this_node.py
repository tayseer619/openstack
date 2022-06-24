import logging
import os
import sys
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
import utils
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from neutron import Neutron
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_external_traffic_must_pass_through_the_floating_ip_namespace_of_compute_node(BaseTestCase):
    """A Basic Test Case for test_verify_external_traffic_must_pass_through_the_floating_ip_namespace_of_compute_node"""

    name = " test_verify_external_traffic_must_pass_through_the_floating_ip_namespace_of_compute_node."

    def __init__(self):
        self.flavor_id = ""
        self.instance1 = None
        self.instance2 = None
        self.compute0 = ""
        self.compute1 = ""
        self.compute0_ip = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("dvr_enable")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute1 = common_utils.get_compute_name(testbed_obj, "compute-1")
        self.compute0_ip = common_utils.get_compute_ip(
            testbed_obj, "compute-0")
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "dvr", settings.get("flavor1_name"))
        self.instance1 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"), self.compute0)
        self.instance2 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_2_name"], settings["network2_name"], common_utils.ids.get("network2_id"), self.compute1)

    @pytest.mark.dvr
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        if self.instance1.get("floating_ip") is not None and self.instance2.get("floating_ip"):
            ping_response1 = os.system(
                "ping -c 3 " + self.instance1.get("floating_ip"))
            ping_response2 = os.system(
                "ping -c 3 " + self.instance2.get("floating_ip"))
            ping_test_before_service_stop = common_utils.ping_test_between_instances(
                self.instance1.get("floating_ip"), self.instance2.get("floating_ip"), settings)
            # stop l3 service
            common_utils.stop_service_on_node(
                self.compute0_ip, "tripleo_neutron_l3_agent.service")
            # ping test
            ping_test_after_service_stop = common_utils.ping_test_between_instances(
                self.instance1.get("floating_ip"), self.instance2.get("floating_ip"), settings)
            common_utils.start_service_on_node(
                self.compute0_ip, "tripleo_neutron_l3_agent.service")
        assert self.instance1.get("status") == "active"
        assert self.instance2.get("status") == "active"
        assert ping_test_before_service_stop[0] == True
        assert ping_test_after_service_stop[0] != True
        assert ping_response1 == 0
        assert ping_response2 == 0

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance1)
        common_utils.delete_instance(testbed_obj, self.instance2)