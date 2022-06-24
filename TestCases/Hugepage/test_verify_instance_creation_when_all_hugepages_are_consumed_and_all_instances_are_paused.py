import logging
import sys
import pytest
import hpg_utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class hugepageInstanceAllHugepageConsumedAndPaused(BaseTestCase):
    """A Test case to verify all hugepages are consumed and paused"""
    name = "hugepage Instance All Hugepage Consumed And Paused"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.instance2 = None
        self.compute0 = ""
        self.instances = []
        self.instances_status = []
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "hugepage", settings.get("flavor1_name"))
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute0_ip = common_utils.get_compute_ip(
            testbed_obj, "compute-0")

    @pytest.mark.hugepage
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        instances_possible = hpg_utils.get_possible_hugepage_instances(
            self.compute0_ip, 30)
        for i in range(0, instances_possible):
            self.instance = common_utils.create_instance(testbed_obj, self.flavor_id, 'test_server{}'.format(i), 
            settings["network1_name"], common_utils.ids.get("network1_id"), self.compute0, "Yes")
            self.instances_status.append(self.instance.get("status"))
            self.instances.append(self.instance)
        assert "error" not in self.instances_status[:-1] and instances_possible > 0
        self.instance2 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"), self.compute0, "Yes")
        self.instances.append(self.instance2)
        assert self.instance2.get("status") == "active"
        # Pause the instances
        common_utils.perform_action_on_server(
            overcloud_ep, overcloud_token, self.instances, "pause")

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        # Deleting the created flavor and instances.
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        for self.instance in self.instances:
            common_utils.delete_instance(testbed_obj, self.instance)
