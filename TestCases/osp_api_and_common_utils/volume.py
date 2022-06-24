import requests
import json
import os
import time
import logging
import paramiko
from main_utils import Utils
from endpoints import OpenStackRestAPIs

class Cinder():

  def send_post_request(api_url, token, payload, header='application/json'):
        """ send post request."""
        try:
            return requests.post(api_url, headers={'content-type':header, 'X-Auth-Token': token}, data=json.dumps(payload))
        except Exception as e:
           logging.error( "request processing failure")
           logging.exception(e)
  
  def attach_volume_to_server( nova_ep, token, project_id, server_id, volume_id, mount_point):
      payload= {"volumeAttachment": {"volumeId": volume_id}}
      response= Cinder.send_post_request("{}{}/{}/os-volume_attachments".format(nova_ep,OpenStackRestAPIs.GetServers, server_id), token, payload)
      logging.debug(response.text)
      logging.info("volume successfully attached to server") if response.ok else response.raise_for_status()
  
  def detach_volume_from_server( nova_ep, token, project_id, server_id, volume_id, mount_point):
      response= Utils.send_delete_request("{}{}/{}/os-volume_attachments/{}".format(nova_ep,OpenStackRestAPIs.GetServers, server_id, volume_id), token)
      logging.debug(response)
  
  def search_volume(storage_ep, token, volume_name, project_id):
      response= Utils.send_get_request("{}{}/{}/volumes".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id), token)
      logging.debug(response.text)
      logging.info("successfully received volume list") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "volumes", "name",volume_name, "id")
  
  def get_volume_metadata(storage_ep, token, volume_id, project_id):
      response= Utils.send_get_request("{}{}/{}/volumes/{}".format(storage_ep, OpenStackRestAPIs.GetVolumes,project_id,volume_id), token)
      logging.debug(response.text)
      logging.info("successfully received volume list") if response.ok else response.raise_for_status()
      data= response.json()
      print(data)
      return data["volume"]["volume_image_metadata"]
  
  def create_volume(storage_ep, token, project_id, volume_name, volume_size, backend=None, image_id=None):
      payload= {"volume":{
                  "size": volume_size,
                  "project_id":project_id,
                  "name": volume_name
                  }
              }
      image_payload={
          "imageRef": image_id
      }
      if image_id is not None:
          payload= {"volume":{**payload["volume"], **image_payload}}
      #if backend defined
      
      beckend_payload={
          "volume_type": backend
      }
      if backend is not None:
          payload= {"volume":{**payload["volume"], **backend_payload}}
      response= Cinder.send_post_request("{}{}/{}/volumes".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id),token, payload)
      logging.info("successfully created volume {}".format(volume_name)) if response.ok else response.raise_for_status()
      data= response.json()
      time.sleep(30)
      return data["volume"]["id"]
  
  def upscale_voume(storage_ep, token, project_id, volume_id, volume_size):
      payload= {"os-extend": {"new_size": volume_size}}
      response= Cinder.send_post_request("{}{}/{}/volumes/{}/action".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id, volume_id),token, payload)
      logging.debug(response.text)
      if(response.status_code ==202):
          logging.debug(response.text)
          #print(response.text)
          logging.info("successfully updated  volume") if response.ok else response.raise_for_status()
          return True
      else:
          return False
  
  def migrate_voume(storage_ep, token, project_id, volume_id):
      payload={
      "os-migrate_volume": {
          "host":"r185-controller-2"
          }
      }
      #payload= {"os-extend": {"new_size": volume_size}}
      response= Cinder.send_post_request("{}{}/{}/volumes/{}/action".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id, volume_id),token, payload)
      logging.debug(response.text)
      if(response.status_code ==202):
          logging.debug(response.text)
          #print(response.text)
          logging.info("successfully migrated  volume") if response.ok else response.raise_for_status()
          return True
      else:
          return False
  
  def search_and_create_volume(storage_ep, token, project_id, volume_name, volume_size, backend=None, image_id=None):
      volume_id= Cinder.search_volume(storage_ep, token, volume_name, project_id)
      if volume_id is None:
          volume_id= Cinder.create_volume(storage_ep, token, project_id, volume_name, volume_size, backend, image_id )
      logging.debug("Volume id: "+volume_id)    
      return volume_id
  def check_volume_status(storage_ep, token, project_id, volume_id):
      response = Utils.send_get_request("{}{}/{}/volumes/{}".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id, volume_id), token)
      data= response.json()
      return data["volume"]["status"] if response.ok else response.raise_for_status()
  
  def create_volume_snapshot(storage_ep, token, project_id, volume_id, snapshot_name):
      payload= {"snapshot": {"volume_id": volume_id, 
      "force": "false", 
      "name": snapshot_name }
              }
      response= Cinder.send_post_request("{}{}/{}/snapshots".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id),token, payload)
      logging.debug(response.text)
      time.sleep(30)
      #print(response.text)
      if(response.status_code == 202):
          logging.info("successfully created snapshot {}".format(snapshot_name)) if response.ok else response.raise_for_status()
          data= response.json()
          return data["snapshot"]["id"]
      else:
          return None
      
  
  def replicate_volume(storage_ep, token, project_id, volume_name, source_id):
      payload= {"volume":{
                  "source_volid": source_id,
                  "name": volume_name
                  
                  }
              }
      response= Cinder.send_post_request("{}{}/{}/volumes".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id),token, payload)
      logging.debug(response.text)
      #print(response.text)
      if(response.status_code== 202):
          logging.info("successfully replicated volume {}".format(volume_name)) if response.ok else response.raise_for_status()
          data= response.json()
          time.sleep(30)
          return data["volume"]["id"]
      else: 
          return None
  
  def create_volume_from_snapshot(storage_ep, token, project_id, volume_name, snapshot_id):
  
      payload= {"volume":{
                  "snapshot_id": snapshot_id,
                  "name": volume_name
                  }
              }
      response= Cinder.send_post_request("{}{}/{}/volumes".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id),token, payload)
      logging.debug(response.text)
      #print(response.text)
      if(response.status_code== 202):
          logging.info("successfully created volume {}".format(volume_name)) if response.ok else response.raise_for_status()
          data= response.json()
          return data["volume"]["id"]
      else: 
          return None
  
  def get_volume_type_list(storage_ep, token, project_id, volume_type):
      response= Utils.send_get_request("{}{}/{}/types".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id), token)
      logging.debug(response.text)
      logging.info("successfully received volume list") if response.ok else response.raise_for_status()
      data= response.json()
      return Utils.parse_json_to_search_resource(response, "volume_types", "name",volume_type, "id")
  
  def get_volume_service_list(storage_ep, token, project_id, service_name):
      response= Utils.send_get_request("{}{}/{}/os-services".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id), token)
      logging.debug(response.text)
      logging.info("successfully received volume list") if response.ok else response.raise_for_status()
      data= response.json()
      return Utils.parse_json_to_search_resource(response, "services", "host", service_name, "state")
  
  def create_image_from_volume(storage_ep, token, project_id, volume_id, image_name):
      payload= {"os-volume_upload_image": {
                  "force": "false", 
                  "image_name": image_name, 
                  "container_format": "bare", 
                  "disk_format": "qcow2"
                  }
              }
      response= Cinder.send_post_request("{}{}/{}/volumes/{}/action".format(storage_ep,OpenStackRestAPIs.GetVolumes, project_id, volume_id),token, payload)
      logging.debug(response.text)
      data= response.json()
      print(response.text)
      return data["os-volume_upload_image"]["image_id"]
      
  def delete_volume(cinder_ep, token, project_id, volume_id):
      logging.info("deleting volume")
      response= Utils.send_delete_request("{}{}/{}/volumes/{}".format(cinder_ep,OpenStackRestAPIs.GetVolumes,project_id,volume_id), token)
  
  def delete_snapshot(cinder_ep, token, project_id, snapshot_id):
      logging.info("deleting volume")
      response= Utils.send_delete_request("{}{}/{}/snapshots/{}".format(cinder_ep,OpenStackRestAPIs.GetVolumes,project_id,snapshot_id), token)