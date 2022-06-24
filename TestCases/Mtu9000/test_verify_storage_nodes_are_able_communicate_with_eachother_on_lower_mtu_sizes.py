import logging
import sys
import os
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from neutron import Neutron
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_storage_nodes_are_able_communicate_with_eachother_on_lower_mtu_sizes(BaseTestCase):
    """test_verify_storage_nodes_are_able_communicate_with_eachother_on_lower_mtu_sizes"""
    name = "test_verify_storage_nodes_are_able_communicate_with_eachother_on_lower_mtu_sizes"

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
            testbed_obj, "storage")
        ping_64 = utils.ping_nodes_on_custom_mtu(nodes_ips, 64)
        ping_128 = utils.ping_nodes_on_custom_mtu(nodes_ips, 128)
        ping_512 = utils.ping_nodes_on_custom_mtu(nodes_ips, 512)
        ping_1500 = utils.ping_nodes_on_custom_mtu(nodes_ips, 1500)
        ping_3000 = utils.ping_nodes_on_custom_mtu(nodes_ips, 3000)
        ping_6000 = utils.ping_nodes_on_custom_mtu(nodes_ips, 6000)

        assert ping_64 == True
        assert ping_128 == True
        assert ping_512 == True
        assert ping_1500 == True 
        assert ping_3000 == True 
        assert ping_6000 == True 

    def post_testcase(self, testbed_obj):
        pass
        
