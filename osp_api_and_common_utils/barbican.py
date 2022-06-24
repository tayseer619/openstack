import requests
import json
import os
import time
import logging
import paramiko
from main_utils import Utils
from endpoints import OpenStackRestAPIs

class Barbican():
         
  def add_key_to_store(barbican_ep, token, key):
      """add key to barbican store."""
      payload= {"name": "signing-cert", 
                  "algorithm": "RSA", 
                  "mode": "cbc", 
                  "bit_length": 256,
                  "secret_type": "certificate", 
                  "payload": key,
                  "payload_content_type": "application/octet-stream", 
                  "payload_content_encoding": "base64"}
  
      response= Utils.send_post_request("{}{}".format(barbican_ep,OpenStackRestAPIs.GetBarbicanSecrets), token, payload)
      #parse the response
      if (response.status_code==201):
        key_id= str(response.text)
        key_id= key_id.split("/")
        key_id= key_id[-1]
        key_id= key_id.strip('"}')  
      logging.debug("successfully add key to barbican") if response.ok else response.raise_for_status()
      return key_id
  
  def add_symmetric_key_to_store(barbican_ep, token):
      """add symmetric key to barbican store."""
      payload= {"type": "key", 
              "meta": {"name": "swift_key", 
              "algorithm": "aes", 
              "bit_length": 256, 
              "payload_content_type": "application/octet-stream", 
              "mode": "ctr"}
              }
      response= Utils.send_post_request("{}{}".format(barbican_ep,OpenStackRestAPIs.GetBarbicanOrders), token, payload)
      #parse response
      if (response.status_code==202):
          key_id= str(response.text)
          key_id= key_id.split("/")
          key_id= key_id[-1]
          key_id= key_id.strip('"}')
      logging.debug("Key is: "+key_id)
      logging.debug("successfully add key to barbican") if response.ok else response.raise_for_status()
      return key_id
  
  def create_secret(barbican_ep, token, name, payload):
      """create barbican secret."""
      logging.info("Creating barbican secret")
      key_id=""
      payload= {"name": name, 
                  "algorithm": "aes", 
                  "mode": "cbc", 
                  "bit_length": 256, 
                  "secret_type": "opaque" ,
                  "payload": payload, 
                  "payload_content_type": "text/plain"
              }
      response= Utils.send_post_request("{}{}".format(barbican_ep,OpenStackRestAPIs.GetBarbicanSecrets), token, payload)
      logging.debug(response.text)
      logging.debug(response.status_code)
      #"parse response"
      if (response.status_code==201):
          key_id= str(response.text)
          key_id= key_id.split("/")
          key_id= key_id[-1]
          key_id= key_id.strip('"}')
          logging.debug("successfully add secret to barbican") if response.ok else response.raise_for_status()
      else:
          logging.debug("failed to create secret")
      return key_id
  
  def update_secret(barbican_ep, token, url, data):
      """update a barbican secret."""
      payload= {"data"}
      response=""
      try:
         response= Utils.requests.put("{}{}".format(barbican_ep,OpenStackRestAPIs.GetBarbicanSecrets), headers= {"Accept":"text/plain", 'X-Auth-Token': token}, data=json.dumps(payload))
      except Exception as e:
          logging.error( "request processing failure ", stack_info=True)
          logging.exception(e)
      logging.debug(response)
      if (response.status_code==201):
          logging.debug("successfully updated secret to barbican") if response.ok else response.raise_for_status()
          return True
      else:
          logging.debug("failed to update secret")
          return False
  
  def get_secret(barbican_ep, token, secret_id):
      """get barbican secret by secret id."""
      response= Utils.send_get_request("{}{}/{}".format(barbican_ep,OpenStackRestAPIs.GetBarbicanSecrets,secret_id), token)
      logging.debug(response.text)
      if response.status_code==200:
          return response.text
      else:
          return None 
  
  def get_key(barbican_ep, token, secret_id):
      """get barbican secret key by secret id."""
      response= Utils.send_get_request("{}{}/{}".format(barbican_ep,OpenStackRestAPIs.GetBarbicanOrders,secret_id), token)
      logging.debug(response.text)
      if response.status_code==200:
          return response.text
      else:
          return None 
  
  def get_payload(barbican_ep, token, secret_id):
      """get payload of barbican secret."""
      response= Utils.send_get_request("{}{}/{}/payload".format(barbican_ep,OpenStackRestAPIs.GetBarbicanSecrets,secret_id), token)
      logging.debug(response.text)
      return response.text
  
  def delete_secret(barbican_ep, secret_id, token):
      """delete barbican secret"""
      def delete_resource(api_url, token):
        Utils.send_delete_request(api_url, token)
      delete_resource("{}{}/{}".format(barbican_ep,OpenStackRestAPIs.GetBarbicanSecrets,secret_id), token)
  
