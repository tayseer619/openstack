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

class test_hugepage_size_1GB_or_2MB_validation(BaseTestCase):
    # Checking the hugepage size
    name = "hugepage_size_1GB_or_2MB_validation"

    def __init__(self):
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
        common_utils.validate_osp_environment(testbed_obj)

    @pytest.mark.hugepage
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        hugepages = []
        # get ip adresses of all compute nodes
        baremetal_nodes = common_utils.baremetal_nodes(testbed_obj)
        compute_node_ips = [val for key,
                            val in baremetal_nodes.items() if "compute" in key]
        for compute in compute_node_ips:
            # getting the hugepage size in the deployed instance
            output = common_utils.ssh_into_node(
                compute, " grep Huge /proc/meminfo")
            huge_page_size = hpg_utils.parse_hugepage_size(
                output[0], "Hugepagesize:")
            hugepages.append(huge_page_size)
            # check that all copute nodes have same hugepages size
            verify_hugepages = hugepages.count(hugepages[0]) == len(hugepages)
            # getting the hugepage size in ini_file
            features = common_utils.get_features(testbed_obj)
            hugepagesize = features.hugepage_size
            assert(verify_hugepages == True)
            # checking if the hugepage size in ini_file == hugepage size in the instance
            if  hugepagesize == "1GB":
                assert hugepages[0] == "1048576"
            else:
                assert hugepages[0] == "2048"

    def post_testcase(self, testbed_obj):
        pass
