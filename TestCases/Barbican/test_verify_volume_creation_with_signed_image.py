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

class test_verify_volume_creation_with_signed_image(BaseTestCase):
    """A test case for test_verify_volume_creation_with_signed_image"""

    name = "test_verify_volume_creation_with_signed_image"

    def __init__(self):
        self.volume_id = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("barbican_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.volume_id = common_utils.search_and_create_volume(
            testbed_obj, common_utils.ids.get("project_id"), settings.get("volume1_name"), 
            settings.get("volume_size"), None, common_utils.ids.get("image_id"))

    @pytest.mark.barbican
    @pytest.mark.volume
    @pytest.mark.all
    def run_test(self, testbed_obj):
        # importing get features function from common utils
        
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        overcloud_ep = common_utils.get_overcloud_ep(testbed_obj)
        # checking volume status
        volume_status = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        assert volume_status != "error"
        # checking if instance is active and volume is available and attaching the volume to the instance
        if self.instance.get("status") == "active" and volume_status == "available":
            assert instance.get("status") == "active"
            common_utils.attach_volume(
                testbed_obj, common_utils.ids.get("project_id"), self.instance.get("id"), self.volume_id)
        # Checking the volume status after attachment
        volume_status_after_attachment = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        assert volume_status_after_attachment == "in-use"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the flavor and instance and volume
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
        common_utils.delete_volume(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
