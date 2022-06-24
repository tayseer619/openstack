import logging
import sys
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_that_ovs_service_is_working_properly_when_deployed(BaseTestCase):
    """A Basic Test Case to test_verify_that_ovs_service_is_working_properly_when_deployed"""

    name = "test_verify_that_ovs_service_is_working_properly_when_deployed"""

    def __init__(self):
        self.nodes_ips = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "ovs_dpdk_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.nodes_ips = common_utils.get_all_baremtal_nodes_ip(
            testbed_obj, "compute")

    @pytest.mark.dpdk
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        ovs_service_status = utils.verify_status_of_ovs_service(self.nodes_ips)
        assert ovs_service_status == True

    def post_testcase(self, testbed_obj):
        pass
        
