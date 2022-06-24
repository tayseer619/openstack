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

class test_create_pool_with_the_source_ip_algorithm_and_verify_the_http_request_flow(BaseTestCase):
    """A Test case for create_pool_with_the_source_ip_algorithm_and_verify_the_http_request_flow"""
    name = "create_pool_with_the_source_ip_algorithm_and_verify_the_http_request_flow.py"

    def __init__(self):
        self.loadbalancer = None
        self.flavor_id = ""
        self.instance1 = None
        self.instance2 = None
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
            overcloud_ep, overcloud_token, "HTTPS", 80, "SOURCE_IP")

        if self.loadbalancer.get("pool_status") == "ACTIVE":
            self.flavor_id = common_utils.get_flavor_id(
                testbed_obj, "octavia", settings.get("flavor1_name"))
            self.instance1 = common_utils.create_instance(
                testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))
            self.instance2 = common_utils.create_instance(
                testbed_obj, self.flavor_id, settings["server_2_name"], settings["network1_name"], common_utils.ids.get("network1_id"))
            # install packages on instances
            utils.install_http_packages_on_instance(
                self.instance1.get("floating_ip"), "1", settings)
            utils.install_http_packages_on_instance(
                self.instance2.get("floating_ip"), "2", settings)
            # add members to pool
            utils.add_members_to_pool(overcloud_ep, overcloud_token, self.loadbalancer.get(
                "pool_id"), common_utils.ids.get("subnet1_id"), 80, "HTTPS", [self.instance1, self.instance2])
            curl_command = "curl {}".format(
                self.loadbalancer.get("floating_ip"))
            output = []
            for i in range(0, 6):
                result = os.popen(curl_command).read()
                # parse result
                result = result.strip()
                output.append(result)

        assert self.loadbalancer.get("lb_status") == "ACTIVE"
        # verify state of listener
        assert self.loadbalancer.get("listener_status") == "ACTIVE"
        # verify state of pool
        assert self.loadbalancer.get("pool_status") == "ACTIVE"
        assert len(output) > 0

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created Loadbalancer , flavor and instance
        common_utils.delete_loadbalancer_pool(
            testbed_obj, self.loadbalancer.get("pool_id"))
        common_utils.delete_loadbalancer_listener(
            testbed_obj, self.loadbalancer.get("listener_id"))
        common_utils.delete_loadbalancer(
            testbed_obj, self.loadbalancer.get("lb_id"))
        common_utils.delete_floating_ip(
            testbed_obj, self.loadbalancer.get("floating_ip_id"))
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance1)
        common_utils.delete_instance(testbed_obj, self.instance2)
