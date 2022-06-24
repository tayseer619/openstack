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
from neutron import Neutron

LOGGER = logging.getLogger(__name__)

class test_verify_network_creation_on_mtu_size_9000(BaseTestCase):
    """test_verify_network_creation_on_mtu_size_9000.py"""
    name = "test_verify_network_creation_on_mtu_size_9000"

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
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        network = Neutron.get_network_detail(
            overcloud_ep, overcloud_token, common_utils.ids.get("network1_id"))
        assert network["network"]["mtu"] == 9000

    def post_testcase(self, testbed_obj):
        pass
        
