import subprocess
import os
import queue
import logging
import time
import sys
from threading import Thread
import paramiko
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
import common_utils

threads_output = queue.Queue()

def get_last_created_presenter_port(node):
    command = "sudo ovs-dpctl show"
    presenter_ports = common_utils.ssh_into_node(node, command)
    presenter_ports = presenter_ports[0].split('\n')
    presenter_ports = presenter_ports[-2]
    presenter_ports = presenter_ports.split(":")
    return presenter_ports[1]

def listen_tcpdump(compute_ip):
    port_to_listen = get_last_created_presenter_port(compute_ip)
    command = "sudo timeout 30 tcpdump -vv -nnn -i {} | grep 'ICMP echo'".format(
        port_to_listen)
    try:
        user_name = "heat-admin"
        logging.info("Trying to connect with node {}".format(compute_ip))
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_session = ssh_client.connect(compute_ip, username="heat-admin", key_filename=os.path.expanduser("~/.ssh/id_rsa"))  # noqa
        logging.info("SSH Session is established")
        logging.info("Running command in a compute node")
        stdin, stdout, stderr = ssh_client.exec_command(command)
        logging.info("command {} successfully executed on compute node {}".format(
            command, compute_ip))
        output = stdout.read().decode('ascii')
        error = stderr.read().decode('ascii')
        threads_output.put(output)
    except Exception as e:
        logging.exception(e)
        logging.error(
            "error ocurred when making ssh connection and running command on remote server")
    finally:
        ssh_client.close()
        logging.info("Connection from client has been closed")

def ping_instances(instance1, instance2, settings, command):
    try:
        client = paramiko.SSHClient()
        paramiko.AutoAddPolicy()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(instance1, port=22, username="centos",
                       key_filename=os.path.expanduser(settings["key_file"]))
        logging.info("SSH Session is established")
        logging.info("Running command in a compute node")
        stdin, stdout, stderr = client.exec_command(command)
        logging.info("command {} successfully executed on compute node {}".format(
            command, instance2))
        output = stdout.read().decode('ascii')
        error = stderr.read().decode('ascii')
        threads_output.put(error)
        return output, error
    except Exception as e:
        logging.exception(e)
        logging.error(
            "error ocurred when making ssh connection and running command on remote instance")
    finally:
        client.close()
        logging.info("Connection from client has been closed")

def verify_offloading_on_representor_port(compute_ip, ip, ping_ip, settings):
    logging.debug("starting threads")
    command = "ping -c 20 {}".format(ping_ip)
    tcpdump_thread = Thread(target=listen_tcpdump, args=(compute_ip,))
    instance_ping_thread = Thread(
        target=ping_instances, args=(ip, ping_ip, settings, command))
    tcpdump_thread.start()
    time.sleep(5)
    instance_ping_thread.start()
    logging.info("waiting for threads to finish")
    instance_ping_thread.join(30)
    tcpdump_thread.join(30)
    tcpdump_message = tcpdump_message = ""
    try:
        ping_error = threads_output.get(block=False)
        tcpdump_message = threads_output.get(block=False)
    except:
        logging.debug("Queue is empty")

    if tcpdump_message.count("ICMP echo request") == 1 and tcpdump_message.count("ICMP echo request") and ping_error == "":
        return True
    else:
        return False

def get_sriov_enabled_interfaces(baremetal_nodes):
    # get sriov ports
    result = os.popen(
        "cat ~/pilot/templates/neutron-sriov.yaml |grep physint:").read()
    result = result.split('\n')
    interfaces = result[:-1]
    # for each compute node
    try:
        for node in baremetal_nodes:
            for interface in interfaces:
                interface = interface.split(':')
                command = "sudo ip link show {}".format(interface[1])
                result = common_utils.ssh_into_node(node, command)
                if ("state UP" not in result[0]):
                    return False
        else:
            return True
    except Exception as e:
        logging.exception(e)
        return False

def get_ovsoffload_status(baremetal_nodes):
    # get sriov ports
    command = "sudo ovs-vsctl get Open_vSwitch . other_config:hw-offload"
    # for each compute node
    try:
        for node in baremetal_nodes:
            result = common_utils.ssh_into_node(node, command)
            result = result[0].strip()
            if (result != '"true"'):
                return False
        else:
            return True
    except Exception as e:
        logging.exception(e)
        return False

def get_mode_of_pci_devices(baremetal_nodes):
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
            if ("mode switchdev inline-mode none encap enable" not in device_mode[0]):
                return False
        else:
            return True
    except Exception as e:
        logging.exception(e)
        return False
