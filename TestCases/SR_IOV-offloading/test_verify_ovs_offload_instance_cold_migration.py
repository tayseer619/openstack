import logging
import sys
import os
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from nova import Nova
from neutron import Neutron
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class OffloadingInstanceColdMigration(BaseTestCase):
    """This testcase creates numa instance then migrates it"""

    name = "Offloading instance cold migration"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.compute0 = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("smart_nic")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        # create Offloading flavor
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "offloading", settings.get("flavor1_name"))
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        # create Offloading instance
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], 
            common_utils.ids.get("network1_id"), self.compute0, "No", "smart_nic", common_utils.ids.get("subnet1_id"))

    @pytest.mark.offloading
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        # verify creatin of flavor
        assert self.flavor_id is not None
        # verify creatin of instance
        assert self.instance.get("status") == "active"
        # get overcloud endpoint
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        # get overcloud token
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)

        # get host of instance
        host = Nova.get_server_baremetal_host(
            overcloud_ep, overcloud_token, self.instance.get("id"))
        # cold migrate instance
        response = common_utils.cold_migrate_instance(
            testbed_obj, self.instance.get("id"), self.instance.get("floating_ip"))
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
        # delete flavor and instance
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        # delete instance
        common_utils.delete_instance(testbed_obj, self.instance)
        # delete port
        common_utils.delete_port(testbed_obj, self.instance.get("port_id"))
