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

class Powerflex_Service_Status(BaseTestCase):

    name = "Test Verify Powerflex Service Status"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.powerflex_status = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "enable_powerflex_backend")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # get powerflex service status
        self.powerflex_status = utils.get_volume_service_list(
            overcloud_ep, overcloud_token, common_utils.ids.get("project_id"), "hostgroup@tripleo_dellemc_powerflex")

    @pytest.mark.powerflex
    @pytest.mark.storage
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        # validate powerflex service
        assert self.powerflex_status == "up"

    def post_testcase(self, testbed_obj):
        pass