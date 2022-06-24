import pytest
import logging
import os
import sys
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
from automatos_framework.shell_manager import ShellManager
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class NumaFlavorValidation(BaseTestCase):
    """Test creation of numa flavor creation"""
    name = "Test creation of numa flavor creation"

    def __init__(self):
        self.flavor_id = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):

        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("numa_enable")
        # validate OSP environment
        common_utils.validate_osp_environment(testbed_obj)
        # create Numa flavor
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "numa", settings.get("flavor1_name"))

    @pytest.mark.numa
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        # verify creatin of flavor
        assert self.flavor_id is not None

    def post_testcase(self, testbed_obj):    
        common_utils.post_check(self.check)
        # delete flavor
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
