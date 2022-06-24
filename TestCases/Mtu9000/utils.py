import sys
import logging
import math
import subprocess
import queue
import pytest
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
import common_utils

def get_interfaces_mtu_size(baremetal_nodes):
    try:
        for node in baremetal_nodes:
            command = "ifconfig | grep mtu"
            interfaces_mtu = common_utils.ssh_into_node(node, command)
            interfaces_mtu = interfaces_mtu[0].split('\n')
            # remove empty element from list
            del interfaces_mtu[-1]
            for interface in interfaces_mtu:
                mtu = interface.split(" ")
                if mtu[len(mtu)-1] != str(9000):
                    if mtu[0] != "lo:" and mtu[0] != "bt-int:" and mtu[0] != "br-tun:":
                        return True
        else: 
            return False
    except Exception as e:
        logging.exception(e)
        return False

def ping_nodes_on_custom_mtu(baremetal_nodes, mtu_size):
    try:
        for node in baremetal_nodes:
            for node_to_ping in baremetal_nodes:
                if node != node_to_ping:
                    command = "ping -c 3 -s {} -M do {}".format(
                        mtu_size, node_to_ping)
                    ping_status, error = common_utils.ssh_into_node(
                        node, command)
                    if error or "icmp_seq=3 Destination Host Unreachable" in ping_status or "ttl=" not in ping_status:
                        return False
        else:
            return True

    except Exception as e:
        logging.exception(e)
        return False
