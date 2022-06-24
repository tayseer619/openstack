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

class test_shutdown_the_loadbalancer_vm_and_check_status_of_loadbalancer(BaseTestCase):
    """A Test case for shutdown_the_loadbalancer_vm_and_check_status_of_loadbalancer"""
    name = "shutdown_the_loadbalancer_vm_and_check_status_of_loadbalancer"

    def __init__(self):
        self.loadbalancer = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("octavia_enable")
        common_utils.validate_osp_environment(testbed_obj)

    @pytest.mark.octavia
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        self.loadbalancer = utils.create_lb(
            overcloud_ep, overcloud_token, "HTTPS", 80, "ROUND_ROBIN")
        # Disable loadbalancer
        utils.disable_loadbalancer(
            overcloud_ep, overcloud_token,  self.loadbalancer.get("lb_id"))
        operating_status_before_shutdown = utils.check_loadbalancer_operating_status(
            overcloud_ep, overcloud_token, self.loadbalancer.get("lb_id"))
        # enable loadbalancer
        utils.enable_loadbalancer(
            overcloud_ep, overcloud_token, self.loadbalancer.get("lb_id"))
        operating_status_after_shutdown = utils.check_loadbalancer_operating_status(
            overcloud_ep, overcloud_token, self.loadbalancer.get("lb_id"))

        assert self.loadbalancer.get("lb_status") == "ACTIVE"
        # verify state of listener
        assert self.loadbalancer.get("listener_status") == "ACTIVE"
        # verify state of pool
        assert self.loadbalancer.get("pool_status") == "ACTIVE"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created loadbalancer
        common_utils.delete_loadbalancer_pool(
            testbed_obj, self.loadbalancer.get("pool_id"))
        common_utils.delete_loadbalancer_listener(
            testbed_obj, self.loadbalancer.get("listener_id"))
        common_utils.delete_loadbalancer(
            testbed_obj, self.loadbalancer.get("lb_id"))
        common_utils.delete_floating_ip(
            testbed_obj, self.loadbalancer.get("floating_ip_id"))
