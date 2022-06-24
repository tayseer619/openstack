import logging
import sys
import time
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_instance_creation_with_hugepage_2MB_flavor_and_1GB_deployment(BaseTestCase):
    """Test case to check the compatibility of 2MB hugepage flavor with 1GB Hugepage deployment."""
    name = "instance_creation_with_hugepage_2MB_flavor_and_1GB_deployment"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "hugepage", settings.get("flavor1_name"), None, None, None, "2048")
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.hugepage
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        # checking hugepage size in ini_file
        features = common_utils.get_features(testbed_obj)
        ini_hugepagesize = features.hugepage_size
        
        assert self.flavor_id is not None
        # verifying hugepage size in ini_file is same as in the created instance
        if ini_hugepagesize == "1GB":
            assert self.instance.get("status") == "error"
        else:
            assert self.instance.get("status") == "active"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instance
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
