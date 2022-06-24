import logging
import sys
import os
import time
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from nova import Nova
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_migration_of_dpdk_instance_with_attached_volume(BaseTestCase):
    """A test case for migration_of_dpdk_instance_with_attached_volume."""
    name = "migration_of_dpdk_instance_with_attached_volume"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.volume_id = ""
        self.compute0 = ""
        self.compute1 = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "ovs_dpdk_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "dpdk", settings.get("flavor1_name"))
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute1 = common_utils.get_compute_name(testbed_obj, "compute-1")
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))
        self.volume_id = common_utils.search_and_create_volume(testbed_obj, common_utils.ids.get(
            "project_id"), settings.get("volume1_name"), settings.get("volume_size"))

    @pytest.mark.dpdk
    @pytest.mark.volume
    @pytest.mark.all
    def run_test(self, testbed_obj):
        # importing get features function from common utils
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # checking volume status
        volume_status = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        assert volume_status != "error"
        # checking if instance is active and volume is available and attaching the volume to the instance
        if self.instance.get("status") == "active" and volume_status == "available":
            assert self.instance.get("status") == "active"
            common_utils.attach_volume(testbed_obj, common_utils.ids.get(
                "project_id"), self.instance.get("id"), self.volume_id)
        # Checking the volume status after attachment
        volume_status_after_attachment = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        assert volume_status_after_attachment == "in-use"
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
        # Deleting the flavor and instance and volume
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
        common_utils.delete_volume(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
