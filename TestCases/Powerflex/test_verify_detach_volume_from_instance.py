import logging
import sys
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class TestVerifyDetachVolumeFromInstance(BaseTestCase):
    """TestVerifyDetachVolumeFromInstance"""

    name = "TestVerifyDetachVolumeFromInstance"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.volume_id = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "enable_powerflex_backend")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        # create flavor
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "powerflex", settings["flavor1_name"])
        # create self.instance
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"), None, "Yes")
        # create volume
        self.volume_id = common_utils.search_and_create_volume(testbed_obj, common_utils.ids.get(
            "project_id"), settings.get("volume1_name"), settings.get("volume_size"), "powerflex_backend")

    @pytest.mark.powerflex
    @pytest.mark.storage
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        # volume status
        volume_status = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        if self.instance.get("status") == "active" and volume_status == "available":
            common_utils.attach_volume(testbed_obj, common_utils.ids.get(
                "project_id"), self.instance.get("id"), self.volume_id)
        volume_status_after_attachment = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        # detach volume
        if volume_status_after_attachment == "in-use":
            common_utils.detach_volume(testbed_obj, common_utils.ids.get(
                "project_id"), self.instance.get("id"), self.volume_id)
        volume_status_after_deattachment = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        # check status of server is active or not
        assert self.instance.get("status") == "active"
        assert volume_status != "error"
        assert volume_status_after_attachment == "in-use"
        assert volume_status_after_deattachment == "available"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # delete self.instance
        common_utils.delete_instance(testbed_obj, self.instance)
        # delete flavor
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        # delete volume
        common_utils.delete_volume(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)