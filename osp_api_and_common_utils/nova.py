import requests
import json
import os
import time
import logging
import paramiko
from main_utils import Utils
from endpoints import OpenStackRestAPIs

class Nova():
  
  '''
  Flavor
  '''
  
  def search_flavor(nova_ep, token, flavor_name):
      """search flavor by name."""
      response= Utils.send_get_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaFlavors), token)
      logging.debug("successfully received flavor list") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "flavors", "name", flavor_name, "id")
  
  def create_flavor(nova_ep, token, flavor_name, flavor_ram, flavor_vcpus, flavor_disks):
      """create flavor.""" 
      logging.info("Creating flavor {}".format(flavor_name))
      payload={
          "flavor": {
              "name": flavor_name,
              "ram":  flavor_ram,
              "vcpus": flavor_vcpus,
              "disk": flavor_disks,
              "rxtx_factor" : "1",
              "os-flavor-access:is_public": "true"
          }
      }
      response= Utils.send_post_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaFlavors), token, payload)
      logging.debug("successfully created flavor") if response.ok else response.raise_for_status()
      data= response.json()
      return data['flavor']['id']
  
  def search_and_create_flavor(nova_ep, token, flavor_name, ram, vcpu, disks):
      """search flavor by name and create if not exists."""
      flavor_id= Nova.search_flavor(nova_ep, token, flavor_name)    
      if flavor_id is None:
          flavor_id= Nova.create_flavor(nova_ep, token, flavor_name, ram, vcpu, disks)   
      logging.debug("flavor id is: {}".format(flavor_id))
      return flavor_id
  
  def put_extra_specs_in_flavor(nova_ep, token, flavor_id,is_numa, mem_page_size="large"):
      """put extra specs to flavors."""
      logging.info("Putting extra specs in flavor")
      #put numa specs
      if is_numa== True:
          payload= {
              "extra_specs": {
                  "hw:cpu_policy": "dedicated", 
                  "hw:cpu_thread_policy": "prefer",
                  "hw:numa_nodes": "1", 
                  "hw:mem_page_size": "large"
                  }
          }
      else:
          #put hugepage specs 
          payload={
                  "extra_specs": {
                      "hw:cpu_policy": "dedicated",
                      "hw:mem_page_size": mem_page_size,
                      "hw:cpu_thread_policy": "prefer",
                      "hw:numa_nodes": "1",
                      #"hw:emulator_threads_policy": "isolate"
                  }  
  
          }
      response= Utils.send_post_request("{}{}/{}/os-extra_specs".format(nova_ep,OpenStackRestAPIs.NovaFlavors, flavor_id), token, payload)
      logging.debug(response.text)
      logging.debug("successfully added extra specs to  flavor {}".format(flavor_id)) if response.ok else response.raise_for_status()
  
  def put_ovs_dpdk_specs_in_flavor(nova_ep, token, flavor_id):
      """put ovs-dpdk specs in flavor"""
      logging.info("Putting OVSDPDK specs in flavor")
      payload={
                  "extra_specs": {
                      "hw:cpu_policy": "dedicated",
                      "hw:mem_page_size": "large",
                      "hw:cpu_thread_policy": "require",
                      "hw:numa_nodes": "1", 
                      "hw:numa_mempolicy":"preferred",
                      "hw:emulator_threads_policy":"isolate"
                  }
          }  
      response= Utils.send_post_request("{}{}/{}/os-extra_specs".format(nova_ep,OpenStackRestAPIs.NovaFlavors, flavor_id), token, payload)
      logging.debug("successfully added extra specs to  flavor {}".format(flavor_id)) if response.ok else response.raise_for_status()
  
  '''
  Keypair
  '''

  def search_keypair(nova_ep, token, keypair_name):
      """search kaypair."""
      response= Utils.send_get_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaKeypair), token)
      logging.debug("successfully received keypair list") if response.ok else response.raise_for_status()
      data= response.json()
      for res in (data["keypairs"]):
          if keypair_name in res["keypair"]["name"]:
              logging.debug("{} already exists".format(keypair_name))
              return res["keypair"]["public_key"]
              break      
      else:
          logging.debug("{} does not exist".format(keypair_name))
  
  def create_keypair(nova_ep, token, keypair_name, abc=None):
      """create keypair."""
      logging.info("Creating Keypair {}".format(keypair_name))
      payload={
          "keypair":{
              "name": keypair_name,
              }
          }
      response= Utils.send_post_request('{}{}'.format(nova_ep,OpenStackRestAPIs.NovaKeypair), token, payload)
      logging.debug("successfully created keypair {}".format(keypair_name)) if response.ok else response.raise_for_status()
      data= response.json()
      return data["keypair"]["private_key"]
  
  def search_and_create_kaypair(nova_ep, token, key_name):
      """search keypair and create if not exists."""
      keypair_public_key= Nova.search_keypair(nova_ep, token, key_name)
      if keypair_public_key is None:
          keypair_public_key= Nova.create_keypair(nova_ep, token, key_name)
      logging.debug("Keypair public key is: {}".format(keypair_public_key))
      return keypair_public_key
  
  '''
  Image
  '''
  def search_image(nova_ep, token, image_name):
      """search image by name."""
      response= Utils.send_get_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaImages), token)
      logging.debug("successfully received images list") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "images", "name", image_name, "id")
  
  def create_image(nova_ep, token, image_name, container_format, disk_format, image_visibility, image_url):
      """create image."""
      logging.info("creating image {}".format(image_name))
      payload ={
          "container_format": container_format,
          "disk_format":disk_format,
          "name": image_name,
          "visibility":  image_visibility,
          "location": image_url
      }
      response = Utils.send_post_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaImages), token, payload)
      logging.debug("successfully created image {}".format(image_name)) if response.ok else response.raise_for_status()
      data= response.json()
      return data["id"]
  def create_barbican_image(nova_ep, token, image_name, container_format, disk_format, image_visibility, image_signature, key_id):
      """create barbican image."""
      logging.info("Crerating barbican image {}".format(image_name))
      payload ={
          "container_format": container_format,
          "disk_format":disk_format,
          "name": image_name,
          "visibility":  image_visibility,
          "img_signature": image_signature,
          "img_signature_certificate_uuid": key_id,
          "img_signature_hash_method":"SHA-256",
          "img_signature_key_type": "RSA-PSS"
      }
      response = Utils.send_post_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaImages), token, payload)
      logging.debug("successfully created image {}".format(image_name)) if response.ok else response.raise_for_status()
      data= response.json()
      return data["id"]
      
  def get_image_status(nova_ep, token, image_id):
      """get status of image."""
      response= Utils.send_get_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaImages, image_id), token)
      logging.debug("successfully received image status") if response.ok else response.raise_for_status()
      data= response.json()
      return(data["status"])
  
  def upload_file_to_image(image_ep, token, image_file, image_id):
      """upload qcow file to image."""
      logging.debug("Uploading file to image")
      try:
        response= requests.put("{}{}/{}/file".format(image_ep,OpenStackRestAPIs.NovaImages, image_id), headers= {'content-type':"application/octet-stream", 'X-Auth-Token': token}, data=image_file)
        logging.debug(response.text)
      except Exception as e:
        logging.error( "request processing failure ", stack_info=True)
        logging.debug(e)
        #logging.debug("successfully uploaded file to image") if response.ok else response.raise_for_status()
  
  def search_and_create_image(image_ep, token, image_name, container_format, disk_format, image_visibility, location):
      """search image by name and create if not exists."""
      image_id= Nova.search_image(image_ep, token, image_name)
      if image_id is None:
          image_id= Nova.create_image(image_ep, token, image_name, container_format, disk_format, image_visibility, location)    
      #get image status
      '''
      status= Nova.get_image_status(image_ep, token, image_id)
      #if status is queued, upload qcow file 
      if status== "queued":
          logging.debug("Successfully Queued")
          image_file= open(image_file_path, 'rb')
          logging.debug("uploading image file")
          upload_file_to_image(image_ep, token, image_file, image_id)
          logging.debug("image id is: {}".format(image_id))
      '''
      return image_id
  
  '''
  Servers
  '''
  
  def receive_all_server(nova_ep, token):
      """receive list of servers."""
      response= Utils.send_get_request("{}{}/detail".format(nova_ep,OpenStackRestAPIs.NovaServers), token)
      logging.debug("successfully received server list") if response.ok else response.raise_for_status()
      return response.json()
  
  def search_server(nova_ep, token, server_name):
      """search for server by name."""
      response= Utils.send_get_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaServers), token)
      logging.debug("successfully received server list") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "servers", "name", server_name, "id")
  
  def create_server(nova_ep, token, server_name, image_id, keypair_name, flavor_id,  network_id, security_group_id, host=None, availability_zone= None):
      """create server."""
      logging.info("Creating Server {}".format(server_name))
      payload= {"server": {"name": server_name, "imageRef": image_id,
          "key_name": keypair_name, "flavorRef": flavor_id, 
          "max_count": 1, "min_count": 1, "networks": [{"uuid": network_id}], 
          "security_groups": [{"name": security_group_id}]}}   
      #if server is created on specific host
      payload_manual_host={
          "host": host
          }
      #if availability zone is defined other wise default zone will be selected.
      payload_availability_zone={
          "availability_zone": availability_zone
          }
      #merge payload_manual_host with payload
      if host is not None:
          payload= {"server":{**payload["server"], **payload_manual_host}}
      #merge availability_zone with payload
      if availability_zone is not None:
          payload= {"server":{**payload["server"], **payload_availability_zone}}

      response = Utils.send_post_request('{}{}'.format(nova_ep,OpenStackRestAPIs.NovaServers), token, payload)
      logging.debug(response.text)
      logging.debug("successfully created server {}".format(server_name)) if response.ok else  response.raise_for_status()
      data= response.json()
      return data["server"]["links"][0]["href"]  
  
  def create_sriov_server(nova_ep, token, server_name, image_id, keypair_name, flavor_id,  port_id ,security_group_id, host=None):
      """create sriov server."""
      logging.info("Creating SRIOV server {}".format(server_name))
      payload= {"server": {"name": server_name, "imageRef": image_id,
          "key_name": keypair_name, "flavorRef": flavor_id, "security_groups": [{"name": security_group_id}],
          "max_count": 1, "min_count": 1, "networks": [{"port": port_id}], 
           }}   
      #if server is created on specific host
      payload_manual_host={
          "host": host
          }
      #merge payload_manual_host with payload
      if host is not None:
          payload= {"server":{**payload["server"], **payload_manual_host}}
      response = Utils.send_post_request('{}{}'.format(nova_ep,OpenStackRestAPIs.NovaServers), token, payload)
      logging.debug(response.text)
      logging.debug("successfully created sriov server {}".format(server_name)) if response.ok else  response.raise_for_status()
      data= response.json()
      return data["server"]["links"][0]["href"]  
  
  def get_server_detail(token, server_url):
      """get details of server."""
      response = Utils.send_get_request(server_url, token)
      logging.debug("Successfully Received Server Details") if response.ok else response.raise_for_status()
      data= response.json()
      return data["server"]["id"]
  '''
  def get_server_host(nova_ep, token, server_id):
      """get host of server."""
      response = send_get_request("{}/v2.1/servers/{}".format(nova_ep, server_id) , token)
      logging.debug("Successfully Received Server Details") if response.ok else response.raise_for_status()
      data= response.json()
      return data["server"]["OS-EXT-SRV-ATTR:host"]
  '''
  def check_server_status(nova_ep, token, server_id):
      """check status of server."""
      response = Utils.send_get_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token)
      logging.debug(response.text)
      data= response.json()
      return data["server"]["OS-EXT-STS:vm_state"] if response.ok else response.raise_for_status()
  
  def get_server_baremetal_host(nova_ep, token, server_id):
      """get baremetal host of server."""
      response = Utils.send_get_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token)
      logging.debug(response.text)
      data= response.json()
      return data["server"]["OS-EXT-SRV-ATTR:host"] if response.ok else response.raise_for_status()
  
  def parse_server_ip(data, network, network_type):
      """parse IP address of server from API response."""
      #load response as json
      data=data.json()
      #search for ip adress in networks attached to server
      for networks in data["server"]["addresses"][str(network)]:
          if networks["OS-EXT-IPS:type"] == network_type:
              #logging.info("received {} ip address of server".format())
              return networks["addr"]
  
  def get_server_ip(nova_ep, token, server_id, network):
      """get IP address of server"""
      response = Utils.send_get_request('{}{}/{}'.format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token)
      logging.debug(response.text)
      logging.debug("received server network detail") if response.ok else response.raise_for_status()
      return Nova.parse_server_ip(response, network, "fixed")
  
  def get_server_floating_ip(nova_ep, token, server_id, network):
      """get floating IP adress of server."""
      response = Utils.send_get_request('{}{}/{}'.format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token)
      logging.debug("received server network detail") if response.ok else response.raise_for_status()
      return Nova.parse_server_ip(response, network, "floating")
  
  def get_server_instance_name(nova_ep, token, server_id):
      """get instance file name of a server."""
      response = Utils.send_get_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id) , token)
      logging.debug("Successfully Received Server Details") if response.ok else response.raise_for_status()
      data= response.json()
      return data["server"]["OS-EXT-SRV-ATTR:instance_name"]
  
  def perform_action_on_server(nova_ep,token, server_id, action):
      """perform operations on server e.g suspend, shutdown etc."""
      payload={
      action: None
      }
      response= Utils.send_post_request("{}{}/{}/action".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token, payload)
      return response.status_code
      
   
  def create_server_snapshot (nova_ep,token, server_id, snapshot_name):
      """create snapshot of server."""
      logging.info("Creating Snapshot {}".format(snapshot_name))
      payload={
      "createImage" : {
          "name" : snapshot_name,
          "metadata": {}
          }
      }
      response= Utils.send_post_request("{}{}/{}/action".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token, payload)
      logging.debug(response.text)
      if(response.status_code == 202):
          data= response.json()
          #wait for snapshot to become active
          time.sleep(60)
          return data["image_id"]
      else:
          return None
  
  def resize_server(nova_ep,token, server_id, flavor_id):
      """resize server."""
      logging.info("Resizing Server ")
      payload= {
      "resize" : {
          "flavorRef" : flavor_id,
          "OS-DCF:diskConfig": "AUTO"
          }
      }
      response= Utils.send_post_request("{}{}/{}/action".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token, payload)
      #logging.debug(response.text)
      #return response.status_code
  
  def reboot_server(nova_ep,token, server_id):
      """reboot server."""
      logging.info("Rebooting Server ")
      payload={
      "reboot" : {
          "type" : "HARD"
           }
      }
      response= Utils.send_post_request("{}{}/{}/action".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token, payload)
      logging.debug(response.text)
      time.sleep(10)
      return response.status_code
  
  def live_migrate_server(nova_ep,token, server_id, host=None, block_migration="auto"):
      """live migrate server."""
      logging.info("Live migration of  Server ")
      payload= {
          "os-migrateLive": {
              "block_migration": block_migration,
              "host": host
          }
          }
      response= Utils.send_post_request("{}{}/{}/action".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), token, payload)
      logging.debug(response.text)
      logging.info("Waiting for live migration")
      #wait for migration 
      time.sleep(60)
      return response.status_code
  
  def search_and_create_server(nova_ep, token, server_name, image_id, key_name, flavor_id,  network_id, security_group_id, host=None, availability_zone= None):
      """search server and create if not exists."""
      server_id= Nova.search_server(nova_ep, token, server_name)
      if server_id is None:
          time.sleep(5)
          server_url= Nova.create_server(nova_ep, token, server_name, image_id, key_name, flavor_id,  network_id, security_group_id, host, availability_zone)
          time.sleep(5)
          server_id= Nova.get_server_detail(token, server_url)
      logging.debug("Server id: "+server_id)    
      return server_id
  
  def search_and_create_sriov_server(nova_ep, token, server_name, image_id, key_name, flavor_id,  port_id, security_group_id, host=None):
      """search sriov server and create if not exists."""
      server_id= Nova.search_server(nova_ep, token, server_name)
      if server_id is None:
          server_url= Nova.create_sriov_server(nova_ep, token, server_name, image_id, key_name, flavor_id, port_id, security_group_id, host)
          server_id= Nova.get_server_detail(token, server_url)
      logging.debug("Server id: "+server_id)  
      return server_id
  
  def attach_volume_to_server( nova_ep, token, project_id, server_id, volume_id, mount_point):
      """attach volume to a server."""
      logging.info("Attach volume to server ")
      payload= {"volumeAttachment": {"volumeId": volume_id}}
      response= Utils.requests.post("{}{}/{}/os-volume_attachments".format(nova_ep,OpenStackRestAPIs.NovaServers, server_id), headers= {'content-type': "application/json", 'X-Auth-Token': token}, data=json.dumps(payload))
      logging.debug(response.text)
      logging.debug("volume successfully attached to server") if response.ok else response.raise_for_status()
  
  def get_baremeta_nodes_ip(nova_ep, undercloud_token):
      """get ip adress of baremetal nodes."""
      servers= Nova.receive_all_server(nova_ep, undercloud_token)
      server_ip={}
      for server in servers["servers"]:
          try:
              server_ip[server["name"]]= server["addresses"]["ctlplane"][0]["addr"]
          except:
              pass
      return server_ip
  
  def get_compute_host_list(nova_ep, token):
      """get list of baremetal compute hosts."""
      response = Utils.send_get_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaHostList), token)
      logging.debug("successfully received host list") if response.ok else response.raise_for_status()
      data= response.json()
      hosts=[]
      for host in data["hosts"]:
          hosts.append(host["host_name"])
      return hosts
  
  def set_quota(nova_ep, token, project_id, vcpus, instances, ram):
      """set default quota."""
      payload= {"quota_set": {
          "instances": instances,
          "cores": vcpus,
          "ram": ram
          }}
      response= Utils.requests.put("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaQuotaSets, project_id),  headers= {'content-type': "application/json", 'X-Auth-Token': token}, data=json.dumps(payload))
      logging.debug("successfully updated quota") if response.ok else response.raise_for_status()
      
  def get_availability_zones(nova_ep, token):
      """get availibility zone list."""
      response= Utils.send_get_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaOsAggregates), token)
      logging.debug("successfully received availibility zones list") if response.ok else response.raise_for_status()
      data= response.json()   
      return data["aggregates"][0]["id"]
      
  def create_availability_zones(nova_ep, token, name):
      """create availability zone."""
      logging.info("Creating availaility zone {}".format(name))
      payload= {
      "aggregate":
          {
          "name": name,
          "availability_zone": name
          }
      }
      response= Utils.send_post_request("{}{}".format(nova_ep,OpenStackRestAPIs.NovaOsAggregates), token, payload)
      logging.debug("successfully created availibility zone") if response.ok else response.raise_for_status()
      data= response.json()   
      return data["aggregate"]["id"]
  
  def remove_host_from_zone(nova_ep, token, zone_id, host_name):
      """remove host from availability zone."""
      payload= {
      "remove_host": {
          "host": host_name
          }
      }
      response= Utils.send_post_request("{}{}/{}/action".format(nova_ep,OpenStackRestAPIs.NovaOsAggregates,zone_id), token, payload)
      logging.debug("successfully removed host from availability zones ") if response.ok else response.raise_for_status()
  
  def add_host_to_zone(nova_ep, token, zone_id, host_name):
      """add host to availability zone."""
      payload= {
      "add_host": {
          "host": host_name
          }
      }
      response= Utils.send_post_request("{}{}/{}/action".format(nova_ep,OpenStackRestAPIs.NovaOsAggregates,zone_id), token, payload)
      logging.debug("successfully added host to availability zones ") if response.ok else response.raise_for_status()
  
  def add_property_availability_zones(nova_ep, token, zone_id):
      """add property to availability zone."""
      payload= {"set_metadata": {"metadata": {"dpdk": "true"}}}
      response= Utils.send_post_request("{}{}/{}/action".format(nova_ep,OpenStackRestAPIs.NovaOsAggregates, zone_id), token, payload)
      logging.debug("successfully added property availability zone") if response.ok else response.raise_for_status()
  
  
  def server_build_wait(nova_ep, token, server_ids):
      """wait for server to build."""
      while True:
          flag=0
          for server in server_ids:
              status= Nova.check_server_status(nova_ep, token, server)
              logging.debug(status)
              if not (status == "active" or status=="error"):
                  logging.debug("Waiting for server/s to build")
                  flag=1
                  time.sleep(10)
          if flag==0:
              break
  
  def wait_instance_boot(ip, maximum_retries):
      """wait for server to complete boot process."""
      retries=0
      while(1):
          response = os.system("ping -c 3 " + ip)
          if response == 0:
              logging.debug ("Ping successfull!") 
              return True
          logging.debug("Waiting for server to boot")
          time.sleep(30)
          retries=retries+1
          if(retries == maximum_retries):
              return False
  
  def delete_server(nova_ep, token, server):
      """delete server."""
      logging.info("deleting server")
      response= Utils.send_delete_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaServers,server.get("id")), token)
      logging.debug(response)
      time.sleep(5)
      Nova.delete_floating_ip(nova_ep, token, server.get("floating_ip_id"))
  
  def delete_server_with_id(nova_ep, token, server_id):
      """delete server by id"""
      logging.info("deleting server")
      response= Utils.send_delete_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaServers,server_id), token)
      logging.debug(response)
      time.sleep(5)
  
  def delete_flavor(nova_ep, token, flavor_id):
      """delete flavor."""
      logging.info("deleting flavor")
      response= Utils.send_delete_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaFlavors,flavor_id), token)
      logging.debug(response)
  
  def delete_image(nova_ep, token, image_id):
      """delete image."""
      logging.info("deleting image")
      response= Utils.send_delete_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaImages,image_id), token)
      logging.debug(response)
  
  def delete_kaypair(nova_ep, token, keypair_name):
      """delete kaypair."""
      logging.info("deleting keypair")
      response= Utils.send_delete_request("{}{}/{}".format(nova_ep,OpenStackRestAPIs.NovaKeypair,keypair_name), token)
      logging.debug(response)
  
  def delete_floating_ip(neutron_ep, token, floating_ip_id):
      """delete floating IP."""
      logging.info("deleting floating ip")
      response= Utils.send_delete_request("{}{}/{}".format(neutron_ep,OpenStackRestAPIs.NeutronFloatingIps, floating_ip_id), token)
      logging.debug(response)
