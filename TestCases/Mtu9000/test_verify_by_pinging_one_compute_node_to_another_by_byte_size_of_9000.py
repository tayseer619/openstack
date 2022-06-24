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

class test_verify_by_pinging_one_compute_node_to_another_by_byte_size_of_9000(BaseTestCase):
    """A basic testcase test_verify_by_pinging_one_compute_node_to_another_by_byte_size_of_9000"""
    name = "test_verify_by_pinging_one_compute_node_to_another_by_byte_size_of_9000"

    def __init__(self):
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "mtu_size_global_default")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)

    @pytest.mark.mtu9000
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        nodes_ips = common_utils.get_all_baremtal_nodes_ip(
            testbed_obj, "compute")
        interfaces_mtu_status = utils.ping_nodes_on_custom_mtu(nodes_ips, 8972)
        assert interfaces_mtu_status == True

    def post_testcase(self, testbed_obj):
        pass
        
