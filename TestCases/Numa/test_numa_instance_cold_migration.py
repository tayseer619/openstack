import logging
import sys
import os
import pytest
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from neutron import Neutron
from nova import Nova
from parameters import settings
import common_utils

LOGGER = logging.getLogger(__name__)

class NumaInstanceColdMigration(BaseTestCase):
    """This testcase creates numa instance then migrates it"""

    name = "Numa instance cold migration"

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.check = ""

    def pre_testcase(self, testbed_obj):

        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("numa_enable")
        # validate OSP environment
        common_utils.validate_osp_environment(testbed_obj)
        # create Numa flavor
        self.flavor_id = common_utils.get_flavor_id(
            testbed_obj, "numa", settings.get("flavor1_name"))
        # create Numa instance
        self.instance = common_utils.create_instance(
            testbed_obj, self.flavor_id, settings["server_1_name"], settings["network1_name"], common_utils.ids.get("network1_id"))

    @pytest.mark.numa
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):

        # verify creatin of flavor
        assert self.flavor_id is not None
        # verify creatin of instance
        assert self.instance.get("status") == "active"
        # get overcloud endpoint
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        # get overcloud token
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # get host of instance
        host = Nova.get_server_baremetal_host(
            overcloud_ep, overcloud_token, self.instance.get("id"))
        # cold migrate instance
        response = common_utils.cold_migrate_instance(
            testbed_obj, self.instance.get("id"), self.instance.get("floating_ip"))
        assert response == 202
        # new host
        new_host = Nova.get_server_baremetal_host(
            overcloud_ep, overcloud_token, self.instance.get("id"))
        assert host != new_host
        # ping test
        if self.instance.get("floating_ip") is not None:
            ping_response = os.system(
                "ping -c 3 " + self.instance.get("floating_ip"))
        assert ping_response == 0

    def post_testcase(self, testbed_obj):

        # delete flavor and instance
        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)
