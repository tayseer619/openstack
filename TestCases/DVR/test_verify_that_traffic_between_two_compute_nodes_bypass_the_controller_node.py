import logging
import os
import sys
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from neutron import Neutron
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_that_traffic_between_two_compute_nodes_bypass_the_controller_node(BaseTestCase):
    """A Basic Test Case for traffic_between_two_compute_nodes_bypass_the_controller_node"""

    name = "traffic_between_two_compute_nodes_bypass_the_controller_node"

    def __init__(self):
        self.flavor_id = ""
        self.instance1 = None
        self.instance2 = None
        self.compute0 = ""
        self.compute1 = ""
        self.controller0_ip = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("dvr_enable")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute1 = common_utils.get_compute_name(testbed_obj, "compute-1")
        self.controller0_ip = common_utils.get_controller_ip(
            testbed_obj, "controller-0")
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "dvr", settings.get("flavor1_name"))
        self.instance1 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"],
            common_utils.ids.get("network1_id"), self.compute0)
        self.instance2 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_2_name"], settings["network2_name"],
            common_utils.ids.get("network2_id"), self.compute1)

    @pytest.mark.dvr
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        if self.instance1.get("floating_ip") or self.instance2.get("floating_ip") is not None:
            ping_response1 = os.system(
                "ping -c 3 " + self.instance1.get("floating_ip"))
            ping_response2 = os.system(
                "ping -c 3 " + self.instance2.get("floating_ip"))
        if ping_response1 == 0 and ping_response2 == 0:
            router_namespace = "qrouter-"+common_utils.ids.get("router_id")
            received_icmp = utils.verify_traffic_on_namespace(self.controller0_ip, router_namespace, self.instance1.get(
                "floating_ip"), self.instance2.get("floating_ip"), settings)
        assert self.instance1.get("status")
               or self.instance2.get("status") == "active"
        assert received_icmp == False
        assert ping_response1 == 0
        assert ping_response2 == 0

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance1)
        common_utils.delete_instance(testbed_obj, self.instance2)