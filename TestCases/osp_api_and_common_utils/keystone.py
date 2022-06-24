import requests
import json
import os
import time
import logging
import paramiko
from main_utils import Utils
from endpoints import OpenStackRestAPIs

class Keystone():
   
  def get_authentication_token(keystone_ep, username, password):
      """get authentication token from keystone."""
      logging.info("Getting authentication token")
      payload= {"auth": 
                  {"identity": 
                      {"methods": ["password"],"password":
                        {"user": 
                          {"name": username, 
                              "domain": {"name": "Default"},"password": password} }},
                           "scope": {"project": {"domain": {"id": "default"},"name": "admin"}
                      }
                  }
              }
      logging.debug("authenticating user")
      response= Utils.send_post_request("{}{}".format(keystone_ep, OpenStackRestAPIs.GetToken), None, payload)
      print(response)
      logging.debug("successfully authenticated") if response.ok else response.raise_for_status()
      logging.debug(response.text)
      return response.headers.get('X-Subject-Token')
  
  def find_admin_project_id(keystone_ep, token):
      """find project id of admin user."""
      response= Utils.send_get_request("{}{}".format(keystone_ep, OpenStackRestAPIs.GetProject), token)
      logging.debug("successfully received project details") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "projects", "name", "admin", "id")
