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

class test_search_barbican_secret(BaseTestCase):
    """testcase to create barbican secret"""

    name = "search barbican secret"

    def __init__(self):
        self.secret_id = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "barbican_enable")
        common_utils.validate_osp_environment(testbed_obj)

    @pytest.mark.barbican
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # Creating secret
        self.secret_id = utils.create_barbican_secret(
            overcloud_ep, overcloud_token)
        # Get payload
        get_payload = utils.get_payload(
            overcloud_ep, overcloud_token, self.secret_id)
        assert get_payload == "test_case payload"
        assert self.secret_id != "" or None

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        common_utils.delete_secret(testbed_obj, self.secret_id)
