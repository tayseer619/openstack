import logging
import sys
import utils
import time
import os
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from neutron import Neutron
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class TestVerifyOvsoffloadStatus(BaseTestCase):
    """A Basic Test Case for verification of offload status"""

    name = "A Basic Test Case for verification of offload status"

    def __init__(self):
        self.flavor_id = ""
        self.nodes_ips = ""
        self.compute0_ip = None
        self.instance = None
        self.compute0 = ""
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

    @pytest.mark.offloading
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        last_representor_port = utils.get_last_created_presenter_port(
            self.compute0_ip)
        assert self.flavor_id is not None
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], 
            common_utils.ids.get("network1_id"), self.compute0, "Yes", "smart_nic", common_utils.ids.get("subnet1_id"))
        # check status of server is active or not
        assert self.instance.get("status") == "active"
        # ping test instance
        if self.instance.get("status") == "active":
            new_representor_port = utils.get_last_created_presenter_port(
                self.compute0_ip)
            assert last_representor_port != new_representor_port

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # delete flavor
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        # delete instance
        common_utils.delete_instance(testbed_obj, self.instance)
        # delete port
        common_utils.delete_port(testbed_obj, self.instance.get("port_id"))
