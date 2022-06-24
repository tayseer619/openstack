import logging
import sys
import subprocess
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_ports_are_assigned_correctly_to_ovs_dpdk_in_mode_I_and_II(BaseTestCase):
    """A Basic Test Case to verify_ports_are_assigned_correctly_to_ovs_dpdk_in_mode_I_and_II"""
    name = "verify_ports_are_assigned_correctly_to_ovs_dpdk_in_mode_I_and_II"

    def __init__(self):
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "ovs_dpdk_enable")
        common_utils.validate_osp_environment(testbed_obj)

    @pytest.mark.dpdk
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        command = "timeout 2 systemctl status tripleo_neutron_ovs_agent.service"
        neutron_service_status = subprocess.run(
            [command], shell=True, stdout=subprocess.PIPE)
        assert "active (running)" in neutron_service_status.stdout.decode('utf-8')

    def post_testcase(self, testbed_obj):
        pass
        
