import logging
import sys
import os
import pytest
import utils
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
from nova import Nova
import common_utils

LOGGER = logging.getLogger(__name__)

class test_create_barbican_image(BaseTestCase):
    """testcase to create barbican secret"""

    name = "create barbican image"

    def __init__(self):
        self.image_id = None
        self.check = ""

    def pre_testcase(self, testbed_obj):
        
        # check if feature is enabled
        self.check = common_utils.check_if_feature_is_enabled(
            "barbican_enable")
        common_utils.validate_osp_environment(testbed_obj)

    @pytest.mark.barbican
    @pytest.mark.functional
    @pytest.mark.all
    def run_test(self, testbed_obj):
        
        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        # get status of image
        if self.image_id is None:
            # sign image
            files_path = common_utils.get_files_path(testbed_obj)
            ini_file = files_path.ini_file
            self.image_id = Nova.search_and_create_image(
                overcloud_ep, overcloud_token, settings["image_name"], "bare", "qcow2", "public", "")
            key = utils.create_ssl_certificate(settings)
            image_signature = utils.sign_image(
                settings, ini_file.get("image_file_name"))
            barbican_key_id = utils.add_key_to_store(
                overcloud_ep, overcloud_token, key)
            # create image
            image_id = Nova.create_barbican_image(
                overcloud_ep, overcloud_token, settings["image_name"], "bare", "qcow2", "public", image_signature, barbican_key_id)
            status = Nova.get_image_status(
                overcloud_ep, overcloud_token, self.image_id)
            # if status is queued, upload qcow file
        if status == "queued":
            try:
                image_file = open(
                    os.path.expanduser(ini_file.get("image_file_name")), "rb")
                Nova.upload_file_to_image(
                    overcloud_ep, overcloud_token, image_file, self.image_id)
            except:
                pass
        assert image_status == "active"
        
    def post_testcase(self, testbed_obj):
        
        common_utils.post_check(self.check)
        common_utils.delete_image(
            endpoints.get("image"), overcloud_token, self.image_id)
