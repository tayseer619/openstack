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

class test_verify_create_snapshot_from_Hugepage_instance(BaseTestCase):
    """A Test case for create_snapshot_from_Hugepage_instance"""

    name = "create_snapshot_from_hugepage_instance"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.instance_snapshot_id = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
        # Creating the hugepage flavor and instance
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "hugepage", settings.get("flavor1_name"))
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.hugepage
    @pytest.mark.volume
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        # Veifying the flavor creation and checking the status of created instance
        assert self.flavor_id is not None
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        if self.instance.get("status") == "active":
            assert self.instance.get("status") == "active"
            self.instance_snapshot_id = common_utils.create_server_snapshot(
                overcloud_ep, overcloud_token, self.instance.get("id"), settings["snapshot1_name"])
        assert self.instance_snapshot_id is not None

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instance and volume
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
        common_utils.delete_image(testbed_obj, self.instance_snapshot_id)
