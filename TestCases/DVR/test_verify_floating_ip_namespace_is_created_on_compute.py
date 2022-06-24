import logging
import os
import sys
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from neutron import Neutron
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class test_verify_flotaing_ip_namespace_is_created_on_compute(BaseTestCase):
    """A Basic Test Case for test_verify_flotaing_ip_namespace_is_created_on_compute"""

    name = "test_verify_flotaing_ip_namespace_is_created_on_compute"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.compute0_ip = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("dvr_enable")
        # validate environment
        common_utils.validate_osp_environment(testbed_obj)
        self.compute0_ip = common_utils.get_compute_ip(
            testbed_obj, "compute-0")
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "dvr", settings.get("flavor1_name"))
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.dvr
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        namespace_id = utils.get_namespace_id(self.compute0_ip, "fip-")
        assert namespace_id != ""
        assert self.flavor_id is not None
        assert self.instance.get("status") == "active"

    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)