import os
import sys
import logging
import math
import subprocess
import pytest
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
import common_utils

def get_sriov_enabled_interfaces(nodes_ips):
    command = "cat ~/pilot/templates/neutron-sriov.yaml |grep physint:"
    result = os.popen(command).read()
    result = result.split('\n')
    result = result[:-1]
    i = 0
    for interface in result:
        result[i] = interface.strip('      - physint:')
        i = i+1
    return result

def get_mode_of_sriov_pci_devices(baremetal_nodes):
    try:
        for node in baremetal_nodes:
            pci_devices = common_utils.ssh_into_node(
                node, 'lspci | grep "Virtual Function"')
            pci_devices = pci_devices[0].split()
            # remove last element of device
            pci_device = pci_devices[0][:-1]
            # append 0's in device name
            pci_device = "pci/0000:"+pci_device+"0"
            # now get switch mode
            device_mode = common_utils.ssh_into_node(
                node, 'sudo devlink dev eswitch show {}'.format(pci_device))
            # verify device mode
            if ("mode legacy inline-mode none encap disable" not in device_mode[0]):
                return False
        else:
            return True
    except Exception as e:
        logging.exception(e)
        return False
