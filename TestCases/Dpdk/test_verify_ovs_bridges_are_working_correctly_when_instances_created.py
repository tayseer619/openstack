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

class test_verify_ports_assigned_to_ovs_dpdk_are_active_after_the_deployment(BaseTestCase):
    """A Basic Test Case to verify ovs dpdk is deployed on all compute nodes"""

    name = "Demo test verify ovs dpdk is deployed on all compute nodes"""

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
        
        dpdk_bridges = utils.verify_ovs_dpdk_bridges(self.nodes_ips)
        assert dpdk_bridges == True

    def post_testcase(self, testbed_obj):
        pass
        
