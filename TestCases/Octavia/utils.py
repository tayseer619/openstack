import logging
import math
import subprocess
import time
import os
import sys
import pytest
import paramiko
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from loadbalancer import LoadBalancer
from neutron import Neutron
from parameters import settings
import common_utils

def loadbalancer_build_wait(loadbal_ep, token, loadbalancer_ids, maximum_retries):
    retries = 0
    while True:
        for loadbalancer in loadbalancer_ids:
            status = LoadBalancer.check_loadbalancer_status(
                loadbal_ep, token, loadbalancer)
            logging.debug("loadbalancer status is: {}".format(status))
            if not (status == "ACTIVE" or status == "ERROR"):
                logging.debug("Waiting for loadbalancer/s to build")
                time.sleep(30)
        retries = retries+1
        if retries == maximum_retries:
            break

def search_and_create_listener(loadbal_ep, token, listener_name, loadbalancer_id, protocol, protocol_port):
    listener = LoadBalancer.search_and_create_listener(
        loadbal_ep, token, listener_name, loadbalancer_id, protocol, protocol_port)
    return listener

def listener_build_wait(loadbal_ep, token, listener_ids, maximum_retries):
    retries = 0
    while True:
        for listener in listener_ids:
            status = LoadBalancer.check_listener_status(
                loadbal_ep, token, listener)
            logging.debug("listener status is: {}".format(status))
            if not (status == "ACTIVE" or status == "ERROR"):
                logging.debug("Waiting for listener/s to build")
                time.sleep(30)
        retries = retries+1
        if retries == maximum_retries:
            break

def check_listener_status(loadbal_ep, token, listener_id):
    LoadBalancer.check_listener_status(loadbal_ep, token, listener_id)

def pool_build_wait(loadbal_ep, token, pool_ids, maximum_retries):
    retries = 0
    while True:
        for pool in pool_ids:
            status = LoadBalancer.check_pool_status(loadbal_ep, token, pool)
            logging.debug("pool status is: {}".format(status))
            if not (status == "ACTIVE" or status == "ERROR"):
                logging.debug("Waiting for pool/s to build")
                time.sleep(30)
        retries = retries+1
        if retries == maximum_retries:
            break

def install_http_packages_on_instance(instance, message, settings):
    try:
        logging.info("Installing packages on instance")
        client = paramiko.SSHClient()
        paramiko.AutoAddPolicy()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(instance, port=22, username="centos",
                       key_filename=os.path.expanduser(settings["key_file"]))
        channel = client.get_transport().open_session()
        logging.debug("SSH Session is established")
        logging.debug("Running command in a instance node")
        channel.invoke_shell()
        channel.send("sudo -i \n")
        time.sleep(2)
        channel.send("rm /etc/resolv.conf\n")
        time.sleep(2)
        channel.send("touch /etc/resolv.conf\n")
        time.sleep(2)
        channel.send("logging.debugf  'nameserver 10.8.8.8' > /etc/resolv.conf\n")
        time.sleep(2)
        stdin, stdout, stderr = client.exec_command(
            "sudo yum install -y epel-release")
        time.sleep(30)
        logging.debug("command {} successfully executed on instance {}".format(
            "sudo yum install -y epel-release", instance))
        logging.debug("stderr is: {}".format(stderr.read().decode('ascii')))
        stdin, stdout, stderr = client.exec_command(
            "sudo yum install -y nginx")
        time.sleep(30)
        logging.debug("command {} successfully executed on instance {}".format(
            "sudo yum install -y nginx", instance))
        logging.debug("stderr is: {}".format(stderr.read().decode('ascii')))
        stdin, stdout, stderr = client.exec_command(
            "sudo systemctl start nginx")
        time.sleep(30)
        logging.debug("command {} successfully executed on instance {}".format(
            "sudo systemctl start nginx", instance))
        logging.debug("stderr is: {}".format(stderr.read().decode('ascii')))
        channel.send("cd /usr/share/nginx/html/\n")
        channel.send("rm index.html\n")
        time.sleep(2)
        channel.send("touch index.html\n")
        time.sleep(2)
        channel.send("logging.debugf  '{}'> index.html\n".format(message))
        time.sleep(2)
        logging.debug("command {} successfully executed on instance {}".format(
            "sudo yum install nc.x86_64", instance))
        logging.debug("stderr is: {}".format(stderr.read().decode('ascii')))
        time.sleep(30)
        logging.debug("command {} successfully executed on instance {}".format(
            "nc -lp 23456", instance))
        logging.debug("stderr is: {}".format(stderr.read().decode('ascii')))
        time.sleep(30)

    except Exception as e:
        logging.exception(e)
        logging.error(
            "error ocurred when making ssh connection and running command on remote server")
    finally:
        client.close()
        logging.debug("Connection from client has been closed")

def roundrobin_traffic_test(loadbalancer_floating_ip, traffic_type):
    if traffic_type == "HTTPS":
        curl_command = "curl {}".format(loadbalancer_floating_ip)
    if traffic_type == "TCP":
        curl_command = "curl {}:{}".format(loadbalancer_floating_ip, 23456)
    output = []
    for i in range(0, 6):
        result = os.popen(curl_command).read()
        result = result.strip()
        output.append(result)
    logging.debug("output is:")
    logging.debug(output)
    logging.debug(output)
    if output[0] != output[1] and output[2] != output[3] and output[4] != output[5] and output[0] == output[3] and output[1] == output[4] and output[2] == output[5]:
        return True
    else:
        return False

def pool_build_wait(loadbal_ep, token, pool_ids, maximum_retries):
    retries = 0
    while True:
        for pool in pool_ids:
            status = LoadBalancer.check_pool_status(loadbal_ep, token, pool)
            logging.debug("pool status is: {}".format(status))
            if not (status == "ACTIVE" or status == "ERROR"):
                logging.debug("Waiting for pool/s to build")
                time.sleep(30)
        retries = retries+1
        if retries == maximum_retries:
            break

def create_lb(loadbalancer_ep, overcloud_token, traffic_type, port, algorithm, session=None):
    loadbalancer = {}
    # create load balancer
    loadbalancer_id = LoadBalancer.search_and_create_loadbalancer(
        loadbalancer_ep, overcloud_token, settings["loadbalancer1_name"], common_utils.ids.get("subnet1_id"))
    loadbalancer["lb_id"] = loadbalancer_id
    # wait for loadbalancer creation
    loadbalancer_build_wait(loadbalancer_ep, overcloud_token, [
                            loadbalancer_id], settings.get("loadbalancer_build_retires"))
    # get state of loadbalancer
    loadbalancer_state = LoadBalancer.check_loadbalancer_status(
        loadbalancer_ep, overcloud_token, loadbalancer_id)
    loadbalancer["lb_status"] = loadbalancer_state
    if loadbalancer_state == "ACTIVE":
        # create listener
        listener_id = LoadBalancer.search_and_create_listener(
            loadbalancer_ep, overcloud_token, settings.get("listener1_name"), loadbalancer_id, traffic_type, port)
        loadbalancer["listener_id"] = listener_id
        # wait for listener creation
        listener_build_wait(loadbalancer_ep, overcloud_token, [
                            listener_id], settings.get("loadbalancer_listener_creation_retires"))
        # get listener  state
        listener_state = LoadBalancer.check_listener_status(
            loadbalancer_ep, overcloud_token, listener_id)
        loadbalancer["listener_status"] = listener_state
    if loadbalancer_state == "ACTIVE" and listener_state == "ACTIVE":
        # create pool
        pool_id = LoadBalancer.search_and_create_pool(loadbalancer_ep, overcloud_token, settings.get(
            "pool1_name"), listener_id, loadbalancer_id, traffic_type, algorithm, session)
        loadbalancer["pool_id"] = pool_id
        # wait for pool creation
        pool_build_wait(loadbalancer_ep, overcloud_token, [
                        pool_id], settings.get("loadbalancer_pool_creation_retires"))
        # get pool status
        pool_state = LoadBalancer.check_pool_status(
            loadbalancer_ep, overcloud_token, pool_id)
        loadbalancer["pool_status"] = pool_state

    if loadbalancer_state == "ACTIVE":
        # Assign floating ip to loadbalancer
        lb_vipport = LoadBalancer.check_loadbalancer_vipport(
            loadbalancer_ep, overcloud_token, loadbalancer_id)
        #logging.info("vip port: {}".format(lb_vipport))
        public_network_id = Neutron.search_network(
            loadbalancer_ep, overcloud_token, settings["external_network_name"])
        lb_ip_id, lb_ip = LoadBalancer.create_loadbalancer_floatingip(
            loadbalancer_ep, overcloud_token, public_network_id)
        #logging.info("load balancer ip is: {}".format(lb_ip))
        LoadBalancer.assign_lb_floatingip(
            loadbalancer_ep, overcloud_token, lb_vipport, lb_ip_id)
        loadbalancer["floating_ip"] = lb_ip
        loadbalancer["floating_ip_id"] = lb_ip_id
    return loadbalancer

def add_members_to_pool(loadbalancer_ep, overcloud_token, pool_id, subnet_id, port, traffic_type, instances):
    for instance in instances:
        LoadBalancer.add_instance_to_pool(
            loadbalancer_ep, overcloud_token, pool_id, instance.get("ip"), subnet_id, port)

def down_pool_member(loadbal_ep, token, pool_id, member_id):
    LoadBalancer.down_pool_member(loadbal_ep, token, pool_id, member_id)

def get_pool_member(loadbal_ep, token, pool_id):
    member = LoadBalancer.get_pool_member(loadbal_ep, token, pool_id)
    return member

def search_and_create_loadbalancer(loadbal_ep, token, loadbalancer_name, subnet_id):
    lb = LoadBalancer.search_and_create_loadbalancer(
        loadbal_ep, token, loadbalancer_name, subnet_id)
    return lb

def check_loadbalancer_status(loadbal_ep, token, loadbalancer_id):
    LoadBalancer.check_loadbalancer_status(loadbal_ep, token, loadbalancer_id)

def check_loadbalancer_vipport(loadbal_ep, token, loadbalancer_id):
    LoadBalancer.check_loadbalancer_vipport(loadbal_ep, token, loadbalancer_id)

def search_and_create_pool(loadbal_ep, token, pool_name, listener_id, loadbalancerid, protocol, algorithm, session=None):
    LoadBalancer.search_and_create_pool(
        loadbal_ep, token, pool_name, listener_id, loadbalancerid, protocol, algorithm, session=None)

def check_pool_status(loadbal_ep, token, listener_id):
    LoadBalancer.check_pool_status(loadbal_ep, token, listener_id)

def disable_loadbalancer(loadbal_ep, token, loadbalancer_id):
    LoadBalancer.disable_loadbalancer(loadbal_ep, token, loadbalancer_id)

def check_loadbalancer_operating_status(loadbal_ep, token, loadbalancer_id):
    LoadBalancer.check_loadbalancer_operating_status(
        loadbal_ep, token, loadbalancer_id)

def enable_loadbalancer(loadbal_ep, token, loadbalancer_id):
    LoadBalancer.enable_loadbalancer(loadbal_ep, token, loadbalancer_id)

def create_l7policy(loadbal_ep, token, listener_id):
    policy = LoadBalancer.create_l7policy(loadbal_ep, token, listener_id)
    return policy

def create_l7policy_rule(loadbal_ep, token, policy_id):
    policy_rule = LoadBalancer.create_l7policy_rule(
        loadbal_ep, token, policy_id)
    return policy_rule
