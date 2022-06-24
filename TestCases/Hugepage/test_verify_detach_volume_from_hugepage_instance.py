import logging
import sys
import time
import pytest
import hpg_utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class DetachVolumeToHugepageInstance(BaseTestCase):
    """A test case for attaching the volume to hugepage instance"""
    name = "Attach volume to hugepage instance"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.volume_id = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "hugepage", settings.get("flavor1_name"))
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))
        self.volume_id = common_utils.search_and_create_volume(testbed_obj, common_utils.ids.get(
            "project_id"), settings.get("volume1_name"), settings.get("volume_size"))

    @pytest.mark.hugepage
    @pytest.mark.volume
    @pytest.mark.all
    def run_test(self, testbed_obj):
        # importing get features function from common utils
        
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # checking volume status
        volume_status = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        # checking if instance is active and volume is available and attaching the volume to the instance
        if self.instance.get("status") == "active" and volume_status == "available":
            common_utils.attach_volume(testbed_obj, common_utils.ids.get(
                "project_id"), self.instance.get("id"), self.volume_id)
        # Checking the volume status after attachment
        volume_status_after_attachment = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        # Checking if the volume is attached for detachment to process
        if volume_status_after_attachment == "in-use":
            common_utils.detach_volume(testbed_obj, common_utils.ids.get(
                "project_id"), self.instance.get("id"), self.volume_id)
        volume_status_after_detachment = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        assert self.instance.get("status") == "active"
        assert volume_status != "error"
        assert volume_status_after_attachment == "in-use"
        assert volume_status_after_detachment == "available"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the flavor and instance and volume
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
        common_utils.delete_volume(testbed_obj, common_utils.ids.get(
            "project_id"), self.instance.get("volume_id"))
