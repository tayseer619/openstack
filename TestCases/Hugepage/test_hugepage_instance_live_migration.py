import logging
import sys
import os
import time
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from nova import Nova
from neutron import Neutron
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class HugepageInstanceLiveMigration(BaseTestCase):
    """A Test case of live migration of hugepage instance"""
    name = "Hugepage Instance Live Migration"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.compute0 = ""
        self.compute1 = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
        # Creating flavor,instance , getting the node compute 0 and compute 1 and where the instance is created
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "hugepage", settings.get("flavor1_name"))
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute1 = common_utils.get_compute_name(testbed_obj, "compute-1")
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"), self.compute0)

    @pytest.mark.hugepage
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        assert self.flavor_id is not None
        assert self.instance.get("status") == "active"
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # get host of instance
        host = Nova.get_server_baremetal_host(
            overcloud_ep, overcloud_token, self.instance.get("id"))
        # live migrate instance
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

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instance
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
