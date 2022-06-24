import logging
import sys
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class NumaInstanceValidation(BaseTestCase):
    """A Basic Test Case for Numa instance Validation"""

    name = "Numa instance validation"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
    
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("numa_enable")
        # verify creatin of flavor
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "numa", settings.get("flavor1_name"))
        # get overcloud endpoint
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.numa
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):

        # verify creatin of flavor
        assert self.flavor_id is not None
        # verify creatin of instance
        assert self.instance.get("status") != "error"

    def post_testcase(self, testbed_obj):

        # delete falvor and instance
        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
