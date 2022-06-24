import sys
import logging
import math
import subprocess
import pytest
import queue
import os
import time
import paramiko
from threading import Thread
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from neutron import Neutron
from parameters import settings
import common_utils

threads_output = queue.Queue()

def verify_dvr_agent_on_nodes(baremetal_nodes, node_type):
    command = "sudo cat /var/lib/config-data/puppet-generated/neutron/etc/neutron/l3_agent.ini | grep dvr"
    if node_type == "controller":
        agent_mode = "agent_mode=dvr_snat"
    else:
        agent_mode = "agent_mode=dvr"
    try:
        for node in baremetal_nodes:
            ssh_output = common_utils.ssh_into_node(node, command)
            logging.debug("agent mode of node {}, is {}".format(
                node, ssh_output[0].strip()))
            if ssh_output[0].strip() != agent_mode:
                logging.debug("Agent mode is: {}".format(ssh_output))
                return False
        else:
            return True
    except Exception as e:
        logging.exception(e)
        return False

def verify_traffic_on_namespace(controller_ip, router_namespace, ip, ping_ip, settings):

    logging.debug("starting threads")
    command = "ping -c 80 {}".format(ping_ip)
    ping_thread = Thread(target=ping_instances, args=(
        ip, ping_ip, settings, command))
    listen_tcpdump_thread = Thread(target=listen_tcpdump, args=(
        controller_ip, router_namespace, "qrouter"))
    listen_tcpdump_thread.start()
    ping_thread.start()
    logging.info("waiting for threads to finish")
    listen_tcpdump_thread.join()
    ping_thread.join()
    icmp_check = threads_output.get(block=False)
    tcpdump_message = threads_output.get(block=False)
    #ping_status= threads_output.get(block=False)
    return icmp_check

def listen_tcpdump(host_ip, namespace, namespace_type):
    try:
        logging.debug("Trying to connect with instance {}".format(host_ip))
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_session = ssh_client.connect(
            host_ip, username="heat-admin", key_filename=os.path.expanduser("~/.ssh/id_rsa"))
        logging.debug("SSH Session is established")
        logging.debug("running command in server {}".format(host_ip))
        channel = ssh_client.get_transport().open_session()
        channel.invoke_shell()
        channel.send("sudo ip netns exec {} /bin/bash\n".format(namespace))
        time.sleep(5)
        channel.send("ip a\n")
        time.sleep(5)
        interfaces = channel.recv(9999)
        interfaces = interfaces.decode("utf-8")
        interfaces = interfaces.split("\n")
        listen_interfaces = []
        string_to_search = ""
        if(namespace_type == "qrouter"):
            string_to_search = "rfp-"
        if(namespace_type == "floating_ip"):
            string_to_search = "fg-"
        if(namespace_type == "snat"):
            string_to_search = "qg-"
        interface_convention = ["rfp-"]
        for interface in interfaces:
            logging.info(interface)
            if ": " in interface[0:10]:
                logging.debug(interface)
                interface = interface.split(':')
                interface = interface[1]
                if "@" in interface:
                    interface = interface.split('@')
                    interface = interface[0]
                listen_interfaces.append(interface)
        logging.debug("Interfaces to listen are: {}".format(listen_interfaces))
        tcpdump_result = []
        for listen_interface in listen_interfaces:
            logging.info("lisening to interface " + listen_interface)
            channel.sendall(
                "timeout 10 tcpdump -i {}\n".format(listen_interface))
            time.sleep(5)
            tcpdump = channel.recv(9999)
            logging.info("tcpdump results: {}".format(tcpdump))
            tcpdump_result.append(tcpdump)
        return_result = ""
        temp_result = ""
        icmp_received = ""
        icmp_received_result = []
        for result in tcpdump_result:
            if "ICMP echo reply" in result.decode("utf-8") or "ICMP echo request" in result.decode("utf-8") or "vrrp.mcast.net" in result.decode("utf-8") or "IP" in result.decode("utf-8"):
                logging.info("ICMP packet received")
                result.decode("utf-8")
                return_result = result.decode("utf-8")
                temp_result = temp_result+result.decode("utf-8")
                icmp_received_result.append("True")
                break
        else:
            logging.info("No ICMP packet received")
            return_result = temp_result
            icmp_received_result.append("False")
        if "True" in icmp_received_result:
            icmp_received = True
        else:
            icmp_received = False
        threads_output.put(icmp_received)
        #threads_output.put(return_result )
        return icmp_received
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

def get_namespace_id(node_ip, namespace_type):
    command = "ip netns |grep {}".format(namespace_type)
    namespace = common_utils.ssh_into_node(node_ip, command)
    namespace = namespace[0]
    namespace = namespace.split(' ')
    namespace = namespace[0]
    return namespace

def verify_l3_ha_on_nodes(baremetal_nodes):
    command = "sudo cat /var/lib/config-data/puppet-generated/neutron/etc/neutron/neutron.conf |grep l3_ha"
    try:
        for node in baremetal_nodes:
            ssh_output = common_utils.ssh_into_node(node, command)
            ssh_output = ssh_output[0].strip()
            logging.debug("l3_ha node {}, is {}".format(node, ssh_output))
            if ssh_output != "l3_ha=False":
                return False
        else:
            return True
    except Exception as e:
        logging.exception(e)
        return False

def verify_l2_population_driver_on_nodes(baremetal_nodes):
    command = "sudo cat /var/lib/config-data/puppet-generated/neutron/etc/neutron/plugins/ml2/openvswitch_agent.ini | grep l2_population"
    try:
        for node in baremetal_nodes:
            ssh_output = common_utils.ssh_into_node(node, command)
            l2_driver = ssh_output[0].split("=")
            logging.debug("l2 population driver is {}, is {}".format(
                node, ssh_output[0].strip()))
            if l2_driver[1].strip() != "True":
                return False
        else:
            return True
    except Exception as e:
        logging.exception(e)
        return False

def get_agent_list(neutron_ep, token):
    agent = Neutron.get_agent_list(neutron_ep, token)
    return agent
    