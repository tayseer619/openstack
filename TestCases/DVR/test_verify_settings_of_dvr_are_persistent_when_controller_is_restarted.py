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

class test_verify_settings_of_dvr_are_persistent_when_controller_is_restarted(BaseTestCase):
    """A Test case for test_verify_settings_of_dvr_are_persistent_when_controller_is_restarted"""
    name = "test_verify_settings_of_dvr_are_persistent_when_controller_is_restarted"

    def __init__(self):
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("dvr_enable")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)

    @pytest.mark.dvr
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        nodes_ips = common_utils.get_all_baremtal_nodes_ip(
            testbed_obj, "controller")
        # restart baremetal node
        common_utils.restart_baremetal_node(nodes_ips[0], settings)
        dvr_enabled = utils.verify_dvr_agent_on_nodes(nodes_ips, "controller")
        assert dvr_enabled == True

    def post_testcase(self, testbed_obj):
        pass
        