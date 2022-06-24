import logging
import sys
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class TestVerifyCreateSnapshotFromInstance(BaseTestCase):
    """A Basic Test Case for TestVerifyCreateSnapshotFromInstance"""

    name = "Test Verify Create Snapshot From Instance"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.instance_snapshot_id = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "enable_powerflex_backend")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        # create flavor
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "powerflex", settings["flavor1_name"])
        # create instance
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"],
            common_utils.ids.get("network1_id"), None, "Yes")

    @pytest.mark.powerflex
    @pytest.mark.storage
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # create snapshot
        if self.instance.get("status") == "active":
            self.instance_snapshot_id = common_utils.create_server_snapshot(
                overcloud_ep, overcloud_token, self.instance.get("id"), settings.get("snapshot1_name"))
        # check status of server is active or not
        assert self.instance.get("status") == "active"
        assert self.instance_snapshot_id != None

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # delete instance
        common_utils.delete_instance(testbed_obj, self.instance)
        # delete flavor
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        # delete snapshot
        common_utils.delete_image(testbed_obj, self.instance_snapshot_id)