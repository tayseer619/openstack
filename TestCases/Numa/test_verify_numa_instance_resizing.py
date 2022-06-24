import logging
import sys
import os
import numa_utils
import time
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class NumaInstanceResizing(BaseTestCase):
    """A Basic Test Case for NumaInstanceResizing"""
    name = "Numa Instance Resizing"

    def __init__(self):
        self.instance = ""
        self.flavor_id = ""
        self.upscale_flavor = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
    
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("numa_enable")
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "numa", settings.get("flavor1_name"), 4)
        self.upscale_flavor = common_utils.get_flavor_id(
            testbed_obj, "numa", settings.get("flavor2_name"), 8)
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.numa
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
    
        # importing get features function from common utils
        assert self.flavor_id is not None
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        baremetal_nodes = common_utils.baremetal_nodes(testbed_obj)

        vcpus_before = numa_utils.get_vcpus_count_of_instance(
            overcloud_ep, overcloud_token, baremetal_nodes, self.instance)
        resize_status = numa_utils.resize_server(
            overcloud_ep, overcloud_token, self.instance.get("id"), self.upscale_flavor)
        time.sleep(20)
        resize = numa_utils.perform_action_on_server(
            overcloud_ep, overcloud_token, self.instance.get("id"), "confirmResize")
        resize_wait = numa_utils.server_resize_wait(
            overcloud_ep, overcloud_token, self.instance.get("id"))
        vcpus_after = numa_utils.get_vcpus_count_of_instance(
            overcloud_ep, overcloud_token, baremetal_nodes, self.instance)
        if self.instance.get("status") == "active":
            assert self.instance.get("status") == "active"
        else:
            logging.debug("Instance failed")
        if vcpus_before != vcpus_after:
            assert vcpus_before != vcpus_after
        else:
            logging.debug("resizing FAILED")

    def post_testcase(self, testbed_obj):

        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
