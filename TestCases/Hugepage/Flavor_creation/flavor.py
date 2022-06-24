from cgi import test
from tkinter import ACTIVE, TRUE
import requests
import json
import os
import time
import logging
import paramiko
import pytest
from main_utils import Utils
from endpoints import OpenStackRestAPIs
from automatos_framework.base_test_case import BaseTestCase, TestParameter
from automatos_framework.ctd_testbed import CTDTestbed


class test_flavor(BaseTestCase):

    def __init__(self):
        self.flavor_id = ""
        self.instance = None
        self.check = ""


@pytest.mark.hugepage
def pre_test(self, testbed_obj):

    #self.flavor_id = ""
    #name = "flavor1_name"
    #assert self.flavor_id != 'None'         # Chwck if flavour exist
    #assert self.flavor_id.status == ACTIVE  # check flavour status
    self.check = common_utils.check_if_feature_is_enabled("hpg_enable")
    self.flavor_id = common_utils.get_flavor_id(
    testbed_obj, "hugepage", settings.get("flavor1_name"))
    #assert name == getname      #checking flavour name against id

# check hugepage instance creation
def run_test(self, testbed_obj):
    assert self.flavor_id != 'None'
    assert self.check == TRUE


def del_flavour(self, testbed_obj):    #delete

    common_utils.post_check(self.check)
    common_utils.delete_flavor(testbed_obj, self.flavor_id)
    assert self.flavor_id == 'None'

def dpkd_test(self, testbed_obj): #dpkd

        overcloud_ep = common_utils.get_overcloud_endpoint(testbed_obj)
        overcloud_token = common_utils.get_overcloud_token(testbed_obj)
        assert self.flavor_id is not None
        if self.instance.get.status == "TRUE":
            assert self.instance.geT.status == "TRUE"

def del_dpkd(self, testbed_obj):

        common_utils.post_check(self.check)
        common_utils.delete_flavor(testbed_obj, self.flavor_id)
        common_utils.delete_instance(testbed_obj, self.instance)


def snapshot(self, testbed_obj):

    self.instance_snapshot_id = common_utils.create_server_snapshot(
    overcloud_ep, overcloud_token, self.instance.get("id"), settings["snapshot1_name"])
    assert self.instance_snapshot_id is not None



