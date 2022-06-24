import logging
import sys
import numa_utils
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class NumaInstanceAllVcpusConsumedAndSuspended(BaseTestCase):
    """A Test case to verify all vcpus are consumed and suspended"""
    name = "verify all vcpus are consumed and suspended"

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
        self.check = common_utils.check_if_feature_is_enabled("numa_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "numa", settings.get("flavor1_name"))
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.compute0_ip = common_utils.get_compute_ip(
            testbed_obj, "compute-0")

    @pytest.mark.numa
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):

        instances_possible = numa_utils.get_possible_numa_instances(
            self.compute0_ip, 20)
        for i in range(0, instances_possible):
            self.instance = common_utils.create_instance(testbed_obj, self.flavor_id, 'server_test{}'.format(i), 
            settings["network1_name"], common_utils.ids.get("network1_id"), self.compute0, "Yes")
            self.instances_status.append(self.instance.get("status"))
            self.instances.append(self.instance)
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        self.instance2 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], 
            common_utils.ids.get("network1_id"), self.compute0, "Yes")
        self.instances.append(self.instance2)
        # performing Suspend on the server
        common_utils.perform_action_on_server(
            overcloud_ep, overcloud_token, self.instances, "suspend")
        assert "error" not in self.instances_status[:-1] and instances_possible > 0
        assert self.instance2.get("status") == "active"

    def post_testcase(self, testbed_obj):

        common_utils.post_check(self.check)
        # Deleting the created flavor and instances.
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        for self.instance in self.instances:
            common_utils.delete_instance(testbed_obj, self.instance)
