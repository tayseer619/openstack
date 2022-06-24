import logging
import sys
import os
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from nova import Nova
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_live_migration_of_pool_member(BaseTestCase):
    """A Test case for live_migration_of_pool_member"""
    name = "live_migration_of_pool_member"

    def __init__(self):
        self.loadbalancer = None
        self.flavor_id = ""
        self.instance = None
        self.compute0 = ""
        self.compute1 = ""
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
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute1 = common_utils.get_compute_name(testbed_obj, "compute-1")
        self.loadbalancer = utils.create_lb(
            overcloud_ep, overcloud_token, "HTTPS", 80, "ROUND_ROBIN")
        if self.loadbalancer.get("lb_status") == "ACTIVE":
            self.flavor_id = common_utils.get_flavor_id(
                testbed_obj, "octavia", settings.get("flavor1_name"))
            self.instance = common_utils.create_instance(
                testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"), self.compute0)
            # add members to pool
            utils.add_members_to_pool(overcloud_ep, overcloud_token, self.loadbalancer.get(
                "pool_id"), common_utils.ids.get("subnet1_id"), 80, "TCP", [self.instance])
            # install packages
            utils.install_http_packages_on_instance(
                self.instance.get("floating_ip"), "1", settings)
            if self.instance.get("status") == "active":
                # get host of instance
                host = Nova.get_server_baremetal_host(
                    overcloud_ep, overcloud_token, self.instance.get("id"))
                # cold migrate instance
                response = Nova.live_migrate_server(
                    overcloud_ep, overcloud_token, self.instance.get("id"), self.compute1)
                assert response == 202
                # new host
                new_host = Nova.get_server_baremetal_host(
                    overcloud_ep, overcloud_token, self.instance.get("id"))
                assert host != new_host
                # ping test
                if self.instance.get("floating_ip") is not None:
                    ping_response = os.system(
                        "ping -c 3 " + self.instance.get("floating_ip"))
                assert ping_response == 0

        assert self.loadbalancer.get("lb_status") == "ACTIVE"
        # verify state of listener
        assert self.loadbalancer.get("listener_status") == "ACTIVE"
        # verify state of pool
        assert self.loadbalancer.get("pool_status") == "ACTIVE"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instance and loadbalancer
        common_utils.delete_loadbalancer_pool(
            testbed_obj, self.loadbalancer.get("pool_id"))
        common_utils.delete_loadbalancer_listener(
            testbed_obj, self.loadbalancer.get("listener_id"))
        common_utils.delete_loadbalancer(
            testbed_obj, self.loadbalancer.get("lb_id"))
        common_utils.delete_floating_ip(
            testbed_obj, self.loadbalancer.get("floating_ip_id"))
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
