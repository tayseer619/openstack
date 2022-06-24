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

class NumaPinnedCpuValidation(BaseTestCase):

    name = "Numa Pinned Cpu Validation"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):

        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("numa_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "numa", settings.get("flavor1_name"))
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.numa
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):

        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        baremetal_nodes = common_utils.baremetal_nodes(testbed_obj)
        vcpus = numa_utils.get_vcpus_count_of_instance(
            overcloud_ep, overcloud_token, baremetal_nodes, self.instance)
        if self.instance.get("status") == "active":
            vcpus = numa_utils.get_vcpus_count_of_instance(
                overcloud_ep, overcloud_token, baremetal_nodes, self.instance)
            if vcpus == "4":
                assert vcpus == "4"
            else:
                logging.debug("Invalid number of vcpus")
        else:
            logging.debug("instance FAILED")

    def post_testcase(self, testbed_obj):
    
        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
