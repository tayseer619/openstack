import logging
import os
import time
import math
import pexpect
import sys
import paramiko
from subprocess import Popen, PIPE
import subprocess
sys.path.insert(0, "OSP_test_automation/osp_api_and_common_utils")
from parameters import settings
from nova import Nova
from barbican import Barbican
import common_utils

def create_ssl_certificate(settings):
    logging.info("Generating Certificate")
    logging.debug("Generating Certificate")
    os.popen("openssl genrsa -out ~/testcase_private_key.pem 1024")
    time.sleep(2)
    os.popen(
        "openssl rsa -pubout -in ~/testcase_private_key.pem -out ~/testcase_public_key.pem")
    time.sleep(2)
    proc = subprocess.Popen(
        "openssl req -new -key ~/testcase_private_key.pem -out ~/testcase_cert_request.csr",
        shell=True, stdin=PIPE)
    time.sleep(2)
    s = "aa\naa\naa\naa\naa\naa\naa\naaaa\naaaa\n"
    s = s.encode("utf-8")
    proc.communicate(s)
    time.sleep(10)
    os.popen(
        "openssl x509 -req -days 14 -in ~/testcase_cert_request.csr -signkey ~/testcase_private_key.pem -out ~/x509_testcase_signing_cert.crt")
    time.sleep(4)
    private_key = os.popen("base64 ~/x509_testcase_signing_cert.crt")
    time.sleep(4)
    private_key = private_key.read()
    return private_key

def sign_image(settings, file_name):
    # Sign image with Private Key
    logging.info("Signing image with private key")
    logging.debug("Signing image with private key")
    command = "openssl dgst -sha256 -sign ~/testcase_private_key.pem -sigopt rsa_padding_mode:pss -out ~/testcase_cirros-0.4.0.signature {}".format(
        os.path.expanduser(file_name))
    os.popen(command)
    time.sleep(4)
    os.popen(
        "base64 -w 0 ~/testcase_cirros-0.4.0.signature  > ~/testcase_cirros-0.4.0.signature.b64")
    time.sleep(4)
    image_signature = os.popen("cat ~/testcase_cirros-0.4.0.signature.b64")
    image_signature = image_signature.read()
    return image_signature

def create_barbican_secret(barbican_ep, token):
    secret_id = Barbican.create_secret(
        barbican_ep, token, "testcase_secret", "test_case payload")
    return secret_id

def create_barbican_image(nova_ep, token, image_name, container_format, disk_format, image_visibility, image_signature, key_id):
    Nova.create_barbican_image(nova_ep, token, image_name, container_format, disk_format, image_visibility, image_signature, key_id)

def get_image_status(nova_ep, token, image_id):
    Nova.get_image_status(nova_ep, token, image_id)

def add_key_to_store(overcloud_ep, overcloud_token, key):
    store_key = Barbican.add_key_to_store(overcloud_ep, overcloud_token, key)
    return store_key

def add_symmetric_key_to_store(overcloud_ep, overcloud_token):
    Barbican.add_symmetric_key_to_store(overcloud_ep, overcloud_token)

def update_secret(overcloud_ep, overcloud_token, url, data):
    Barbican.update_secret(overcloud_ep, overcloud_token, url, data)

def get_secret(overcloud_ep, overcloud_token, secret_id):
    secret = Barbican.get_secret(overcloud_ep, overcloud_token, secret_id)
    return secret

def get_key(overcloud_ep, overcloud_token, secret_id):
    key = Barbican.get_key(overcloud_ep, overcloud_token, secret_id)
    return key

def get_payload(overcloud_ep, overcloud_token, secret_id):
    payload = Barbican.get_payload(overcloud_ep, overcloud_token, secret_id)
    return payload
