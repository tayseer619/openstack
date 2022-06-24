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

class CorrectHugepageConsumed(BaseTestCase):
    """A Basic Test Case for verification of CorrectHugepageConsumed"""
    name = "CorrectHugepageConsumed"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
        common_utils.validate_osp_environment(testbed_obj)
        # Creating the flavor and instance
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "hugepage", settings.get("flavor1_name"))
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.hugepage
    @pytest.mark.volume
    @pytest.mark.all
    def run_test(self, testbed_obj):
        # importing get features function from common utils
        
        assert self.flavor_id is not None

        if self.instance.get("status") == "active":
            # initializing the overcloud endpoint , token , baremetal node
            overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
            overcloud_token = common_utils.get_overcloud_token(testbed_obj)
            baremetal_nodes = common_utils.baremetal_nodes(testbed_obj)
        # hugepages_consumed will get the hugepages consumed by the created instance
            hugepage_consumed = hpg_utils.get_hugepages_consumed_by_instance(
                overcloud_ep, overcloud_token, baremetal_nodes, self.instance)
        # Getting the hugepage size from ini_file
            features = common_utils.get_features(testbed_obj)
            hugepagesize = features.hugepage_size
        # Verifying if hugepage in ini_file == hugepage in instance
        if hugepagesize == "1GB":
            assert hugepage_consumed == "1048576"
        else:
            assert hugepage_consumed == "2048"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the flavor and instance and volume
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
        common_utils.delete_volume(testbed_obj, common_utils.ids.get(
            "project_id"), self.instance.get("volume_id"))
