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

class TestVerifyVfsAreCreatedAndInUpState(BaseTestCase):
    """A Basic Test Case for verification of VF's creation"""

    name = "A Basic Test Case for verification of VF's creation"

    def __init__(self):
        self.flavor_id = ""
        self.nodes_ips = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):

        self.check = common_utils.check_if_feature_is_enabled("sriov_enable")
        common_utils.validate_osp_environment(testbed_obj)
        # get ip of compute nodes
        self.nodes_ips = common_utils.get_all_baremtal_nodes_ip(
            testbed_obj, "compute")

    @pytest.mark.sriov
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        # check status of interfaces
        sriov_interfaces_status = utils.get_sriov_enabled_interfaces(
            self.nodes_ips)
        # Validate interfaces
        assert sriov_interfaces_status == True

    def post_testcase(self, testbed_obj):
        pass
