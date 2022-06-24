# Utils file for HUGEPAGES
import sys
import logging
import math
import subprocess
import time
import pytest
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from volume import Cinder
from nova import Nova
import common_utils

def get_possible_hugepage_instances(compute_ip, flavor_ram):
    output = common_utils.ssh_into_node(compute_ip, " grep Huge /proc/meminfo")
    output = output[0]
    hugepg_free = parse_hugepage_size(output, "HugePages_Free:")
    instance_possible = math.floor(int(hugepg_free)/flavor_ram)
    return instance_possible-1

def parse_hugepage_size(huge_page_info, parameter):
    huge_page_info = huge_page_info.split('\n')
    for property in huge_page_info:
        line = property.split()
        if line[0] == parameter:
            return line[1]

def get_available_ram_of_node(compute_ip):
    ssh_output = common_utils.ssh_into_node(
        compute_ip, "grep MemTotal: /proc/meminfo")
    ssh_output = ssh_output[0]
    ssh_output = ssh_output.split("       ")
    ssh_output = ssh_output[1].split(" ")
    available_ram = int(ssh_output[0])/(1024*1024)
    return available_ram

def get_hugepages_consumed_by_instance(nova_ep, token, baremetal_nodes, instance):
    host = Nova.get_server_baremetal_host(nova_ep, token, instance.get("id"))
    instance_xml_name = Nova.get_server_instance_name(
        nova_ep, token, instance.get("id"))
    host = host.split(".")
    compoute_node_ip = [val for key,
                        val in baremetal_nodes.items() if host[0] in key]
    command = "sudo cat /etc/libvirt/qemu/{}.xml | grep size".format(
        instance_xml_name)
    output = common_utils.ssh_into_node(compoute_node_ip[0], command)
    output = output[0]
    hugepage_size = output.split('=')
    hugepage_size = hugepage_size[1].split("'")
    return hugepage_size[1]

def get_vcpus_count_of_instance(nova_ep, token, baremetal_nodes, instance):
    host = Nova.get_server_baremetal_host(nova_ep, token, instance.get("id"))
    instance_xml_name = Nova.get_server_instance_name(
        nova_ep, token, instance.get("id"))
    host = host.split(".")
    compoute_node_ip = [val for key,
                        val in baremetal_nodes.items() if host[0] in key]
    command = "sudo cat /etc/libvirt/qemu/{}.xml | grep vcpus".format(
        instance_xml_name)
    output = common_utils.ssh_into_node(compoute_node_ip[0], command)
    output = output[0]
    vcpus = output.split('>')
    return vcpus[1][0]

def server_resize_wait(nova_ep, token, server_ids):
    """wait for server to build."""
    while True:
        flag = 0
        status = Nova.check_server_status(nova_ep, token, server_ids)
        logging.debug(status)
        if not (status == "active" or status == "error"):
            logging.debug("Waiting for server/s to resize and active")
            flag = 1
            time.sleep(10)
        if flag == 0:
            break

def perform_action_on_server(nova_ep, token, server_id, action):
    resizing = Nova.perform_action_on_server(nova_ep, token, server_id, action)

def resize_server(nova_ep, token, server_id, flavor_id):
    resize_status = Nova.resize_server(nova_ep, token, server_id, flavor_id)

def create_server_snapshot(nova_ep, token, server_id, snapshot_name):
    server_snapshot = Nova.create_server_snapshot(
        nova_ep, token, server_id, snapshot_name)

def search_and_create_server(nova_ep, token, server_name, image_id, key_name, flavor_id,  
                             network_id, security_group_id, host=None, availability_zone=None):
    search_create_server = Nova.search_and_create_server(
        nova_ep, token, server_name, image_id, key_name, flavor_id,  network_id, security_group_id, host=None, availability_zone=None)
