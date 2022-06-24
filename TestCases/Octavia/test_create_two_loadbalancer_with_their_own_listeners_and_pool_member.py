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

class creation_of_two_loadbalancers(BaseTestCase):
    """A Test case for creation of two loadbalancers"""
    name = "creation of two loadbalancers"

    def __init__(self):
        self.loadbalancer1 = None
        self.loadbalancer2_id = ""
        self.listener2_id = ""
        self.pool2_id = ""
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
        self.loadbalancer1 = utils.create_lb(
            overcloud_ep, overcloud_token, "HTTPS", 80, "ROUND_ROBIN")
        # create second load balancer
        self.loadbalancer2_id = utils.search_and_create_loadbalancer(
            overcloud_ep, overcloud_token, settings["loadbalancer2_name"], common_utils.ids.get("subnet1_id"))
        # wait for loadbalancer creation
        utils.loadbalancer_build_wait(overcloud_ep, overcloud_token, [
                                      self.loadbalancer2_id], settings.get("loadbalancer_build_retires"))
        # get state of loadbalancer
        loadbalancer2_state = utils.check_loadbalancer_status(
            overcloud_ep, overcloud_token, self.loadbalancer2_id)
        if loadbalancer2_state == "ACTIVE":
            self.listener2_id = utils.search_and_create_listener(
                overcloud_ep, overcloud_token, settings.get("listener2_name"), self.loadbalancer2_id, "HTTPS", 80)
            # wait for listener creation
            utils.listener_build_wait(overcloud_ep, overcloud_token, [
                                      self.listener2_id], settings.get("loadbalancer_listener_creation_retires"))
            # get listener state
            listener2_state = utils.check_listener_status(
                overcloud_ep, overcloud_token, self.listener2_id)
        if loadbalancer2_state == "ACTIVE" and listener2_state == "ACTIVE":
            # create pool
            self.pool2_id = utils.search_and_create_pool(overcloud_ep, overcloud_token, settings.get("pool2_name"), 
            self.listener2_id, self.loadbalancer2_id, "HTTPS", "ROUND_ROBIN")
            # wait for pool creation
            utils.pool_build_wait(overcloud_ep, overcloud_token, [self.pool2_id], 
            settings.get("loadbalancer_pool_creation_retires"))
            # get pool status
            pool2_state = utils.check_pool_status(
                overcloud_ep, overcloud_token, self.pool2_id)
        assert self.loadbalancer1.get("lb_status") == "ACTIVE"
        # verify state of listener
        assert self.loadbalancer1.get("listener_status") == "ACTIVE"
        # verify state of pool
        assert self.loadbalancer1.get("pool_status") == "ACTIVE"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created Loadbalancer
        common_utils.delete_loadbalancer_pool(
            testbed_obj, self.loadbalancer1.get("pool_id"))
        common_utils.delete_loadbalancer_pool(testbed_obj, self.pool2_id)
        common_utils.delete_loadbalancer_listener(
            testbed_obj, self.loadbalancer1.get("listener_id"))
        common_utils.delete_loadbalancer_listener(
            testbed_obj, self.listener2_id)
        common_utils.delete_loadbalancer(
            testbed_obj, self.loadbalancer1.get("lb_id"))
        common_utils.delete_loadbalancer(testbed_obj, self.loadbalancer2_id)
        common_utils.delete_floating_ip(
            testbed_obj, self.loadbalancer1.get("floating_ip_id"))
