import logging
import sys
import time
import utils
import os
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_communication_of_two_ovs_offload_instance_on_same_compute_and_same_network(BaseTestCase):
    """A Basic Test Case for test_verify_communication_of_two_ovs_offload_instance_on_same_compute_and_same_network"""

    name = "test_verify_communication_of_two_ovs_offload_instance_on_same_compute_and_same_network"

    def __init__(self):
        self.flavor_id = ""
        self.instance1 = None
        self.instance2 = None
        self.compute0 = ""
        self.compute0_ip = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("smart_nic")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        # get ip of compute nodes
        self.nodes_ips = common_utils.get_all_baremtal_nodes_ip(
            testbed_obj, "compute-0")
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute0_ip = common_utils.get_compute_ip(
            testbed_obj, "compute-0")
        # create flavor
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "offloading", settings.get("flavor1_name"))
        # create instance1
        self.instance1 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], 
            common_utils.ids.get("network1_id"), self.compute0, "No", "smart_nic", common_utils.ids.get("subnet1_id"))
        # create instance2
        self.instance2 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_2_name"], settings["network1_name"], 
            common_utils.ids.get("network1_id"), self.compute0, "No", "smart_nic", common_utils.ids.get("subnet1_id"))

    @pytest.mark.offloading
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
            received_icmp = utils.verify_offloading_on_representor_port(
                self.compute0_ip, self.instance1.get("floating_ip"), self.instance2.get("floating_ip"), settings)
        assert received_icmp == True

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
