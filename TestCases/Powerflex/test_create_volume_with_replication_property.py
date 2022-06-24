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

class TestVerifyPowerflexVolumeType(BaseTestCase):
    """A Basic Test Case for TestVerifyPowerflexVolumeType"""

    name = "Test Verify Powerflex VolumeType"

    def __init__(self):
        self.replicated_volume_id = ""
        self.volume_id = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "enable_powerflex_backend")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        # get powerflex volume type
        self.volume_id = common_utils.search_and_create_volume(testbed_obj, common_utils.ids.get(
            "project_id"), settings.get("volume1_name"), settings.get("volume_size"), "powerflex_backend")

    @pytest.mark.powerflex
    @pytest.mark.storage
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        volume_status = common_utils.check_volume_status(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        # replicate volume
        self.replicated_volume_id = utils.replicate_volume(overcloud_ep, overcloud_token, common_utils.ids.get(
            "project_id"), "testcase_replicated_volume", self.volume_id)
        if self.replicated_volume_id is not None:
            replicated_volume_status = common_utils.check_volume_status(
                testbed_obj, common_utils.ids.get("project_id"), self.replicated_volume_id)
        # validate volume deletion
        assert volume_status == "available"
        assert replicated_volume_status == "available"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # delete volume
        common_utils.delete_volume(
            testbed_obj, common_utils.ids.get("project_id"), self.volume_id)
        common_utils.delete_volume(testbed_obj, common_utils.ids.get(
            "project_id"), self.replicated_volume_id)