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

class test_verify_dvr_is_deployed_on_all_compute_nodes(BaseTestCase):
    """A Test case for dvr_is_deployed_on_all_compute_nodes"""
    name = "dvr_is_deployed_on_all_compute_nodes"

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
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        agents = utils.get_agent_list(overcloud_ep, overcloud_token)
        total_l3_agents = agents.count("L3 agent")
        total_compute_nodes = len(
            common_utils.get_all_baremtal_nodes_ip(testbed_obj, "compute"))
        total_controller_nodes = len(
            common_utils.get_all_baremtal_nodes_ip(testbed_obj, "controller"))
        assert total_l3_agents == (total_compute_nodes+total_controller_nodes)

    def post_testcase(self, testbed_obj):
        pass
        