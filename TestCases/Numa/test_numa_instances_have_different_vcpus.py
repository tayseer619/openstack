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

class test_numa_instances_have_different_vcpus(BaseTestCase):
    # Checking if instances have different Vcpus

    name = "Instance with different Vcpus"

    def __init__(self):
        self.flavor_id = ""
        self.instance1 = None
        self.instance2 = None
        self.compute0 = ""
        self.check = ""

    def pre_testcase(self, testbed_obj):

        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("numa_enable")
        # Creating the flavor ,instances. getting the compute node.
        common_utils.validate_osp_environment(testbed_obj)
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "numa", settings.get("flavor1_name"))
        self.compute0 = common_utils.get_compute_name(testbed_obj, "compute-0")
        self.instance1 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], 
            common_utils.ids.get("network1_id"), self.compute0, "yes")
        self.instance2 = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_2_name"], settings["network2_name"], 
            common_utils.ids.get("network2_id"), self.compute0, "yes")

    @pytest.mark.numa
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):

        # validating the instances status
        assert self.instance1.get("status") == "active"
        assert self.instance2.get("status") == "active"
        # storing the endpoint,token,baremental node into a variable
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        baremetal_nodes = common_utils.baremetal_nodes(testbed_obj)
        # Getting the Vcpu list of the vcpus on Instance 1 and Instance 2
        instance1_vcpus = numa_utils.get_vcpus_list_of_instance(
            overcloud_ep, overcloud_token, baremetal_nodes, self.instance1)
        instance2_vcpus = numa_utils.get_vcpus_list_of_instance(
            overcloud_ep, overcloud_token, baremetal_nodes, self.instance2)
        # Validating if the vcpus of instance 1 and instance 2 are same or not.
        validate = [vcpu for vcpu in instance1_vcpus if vcpu in instance2_vcpus]
        if not validate:
            validate = True

    def post_testcase(self, testbed_obj):

        common_utils.post_check(self.check)
        # Deleting the created flavor and instances.
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance1)
        common_utils.delete_instance(testbed_obj, self.instance2)
