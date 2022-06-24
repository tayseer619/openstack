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

class HugepageInstanceResizing(BaseTestCase):
    """A Test case for resizing the instance flavor and creating instance with it"""
    name = "Resizing the instance with upscaled flavor"

    def __init__(self):
        self.flavor_id = ""
        self.upscale_flavor = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):

        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
        # Creating 4 vcpu flavor, 8 vcpu flavor and instance
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "hugepage", settings.get("flavor1_name"), 4)
        self.upscale_flavor = common_utils.get_flavor_id(
            testbed_obj, "hugepage", settings.get("flavor2_name"), 8)
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.hugepage
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        # importing get features function from common utils

        assert self.flavor_id is not None
        # initializing the overcloud endpoint , token , baremetal node
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        baremetal_nodes = common_utils.baremetal_nodes(testbed_obj)
        # getting the Vcpus before , resizing the instance and rechecking the instance with upscaled flavor
        vcpus_before = hpg_utils.get_vcpus_count_of_instance(
            overcloud_ep, overcloud_token, baremetal_nodes, self.instance)
        resize_perform = hpg_utils.resize_server(
            overcloud_ep, overcloud_token, self.instance.get("id"), self.upscale_flavor)
        time.sleep(20)
        resize_confirm = hpg_utils.perform_action_on_server(
            overcloud_ep, overcloud_token, self.instance.get("id"), "confirmResize")
        resize_wait = hpg_utils.server_resize_wait(
            overcloud_ep, overcloud_token, self.instance.get("id"))
        vcpus_after = hpg_utils.get_vcpus_count_of_instance(
            overcloud_ep, overcloud_token, baremetal_nodes, self.instance)
        # verifying the instance is active after upscaling the flavor of the instance and vcpus are not equal to default vcpus
        assert self.instance.get("status") == "active"
        assert vcpus_before != vcpus_after

    def post_testcase(self, testbed_obj):

        common_utils.post_check(self.check)
        # Deleting the flavor and instance
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
