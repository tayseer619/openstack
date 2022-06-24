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

class test_verify_create_dvr_instance_from_snapshot(BaseTestCase):
    """A Test case for create_dvr_instance_from_snapshot"""

    name = "create_dvr_instance_from_snapshot"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.instance2 = ""
        self.instance_snapshot_id = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("dvr_enable")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "dvr", settings.get("flavor1_name"))
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.dvr
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
        if self.instance_snapshot_id is not None:
            self.instance2 = common_utils.search_and_create_server(overcloud_ep, overcloud_token, settings["server_2_name"],
                self.instance_snapshot_id, settings["key_name"], self.flavor_id,
                common_utils.ids.get("network1_id"), common_utils.ids.get("security_group_id"))
            common_utils.server_build_wait(
                overcloud_ep, overcloud_token, [self.instance2])
            instance2_status = common_utils.check_server_status(
                overcloud_ep, overcloud_token, self.instance2)

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instance
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
        common_utils.delete_server_with_id(testbed_obj, self.instance2)
        common_utils.delete_image(testbed_obj, self.instance_snapshot_id)