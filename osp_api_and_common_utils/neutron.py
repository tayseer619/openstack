import requests
import json
import os
import time
import logging
import paramiko
from main_utils import Utils
from endpoints import OpenStackRestAPIs

class Neutron():
  
  '''
  Networks
  '''
  def search_network(neutron_ep, token, network_name):
      """get list of networks."""
      response= Utils.send_get_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronNetworks), token)
      logging.debug("successfully received networks list") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "networks", "name", network_name, "id")
  
  def get_network_detail(neutron_ep, token, network_id):
      """get details of a networks."""
      response= Utils.send_get_request("{}{}/{}".format(neutron_ep,OpenStackRestAPIs.NeutronNetworks, network_id), token)
      logging.debug("successfully received networks list") if response.ok else response.raise_for_status()
      response= response.json()
      return response
  
  def create_network(neutron_ep, token, network_name, mtu_size, network_provider_type, is_external, provider_physical_network="physint", provider_segment      =None):
      """create network."""
      logging.info("Creating Network {}".format(network_name))
      payload= {
          "network": {
              "name": network_name,
              "admin_state_up": True,
              "mtu": mtu_size,
              "provider:network_type": network_provider_type,
              "router:external": is_external,
              "provider:physical_network": provider_physical_network
              }
          }
  
      #if creatig public network    
      payload_public_network={
          "provider:segmentation_id": provider_segment,
          }
      #merge payload_public_network json into payload
      if provider_segment is not None:
          payload= {"network":{**payload["network"], **payload_public_network}}
  
      response= Utils.send_post_request('{}{}'.format(neutron_ep,OpenStackRestAPIs.NeutronNetworks), token, payload)
      logging.debug(response.text)
      logging.debug("successfully created network {}".format(network_name)) if response.ok else response.raise_for_status()
      data=response.json()
      return data['network']['id']
  
  def search_and_create_network(neutron_ep, token, network_name, mtu_size, network_provider_type, is_external,  provider_physical_network="physint", provider_segment=None):
      """search network by name and create if do not exists."""
      network_id= Neutron.search_network(neutron_ep, token, network_name)    
      if network_id is None:
          network_id =Neutron.create_network(neutron_ep, token, network_name, mtu_size, network_provider_type, is_external, provider_physical_network, provider_segment)  
      logging.debug("network id is: {}".format(network_id))
      return network_id
  
  def create_port(neutron_ep, token, network_id, subnet_id, name, property=None ):
      """create port on network."""
      logging.info("Creating Network Port {}".format(name))
      payload= {"port": {
          "binding:vnic_type": "direct", 
          "network_id": network_id, 
  	    "admin_state_up": 'true', 
          "fixed_ips": [{"subnet_id": subnet_id}], "name": name}}
      
      #if creationg port for sriov-vflag instance
      payload_port_property= {"binding:profile": {"capabilities": ["switchdev"]},
      }
      #merge payload_port_property into payload
      if property is not None:
          payload= {"port":{**payload["port"], **payload_port_property}}
      response= Utils.send_post_request('{}{}'.format(neutron_ep,OpenStackRestAPIs.NeutronPorts), token, payload)
      logging.debug(response.text)
      logging.debug("successfully created port") if response.ok else response.raise_for_status()
      data=response.json()
      return data["port"]["id"], data["port"]["fixed_ips"][0]["ip_address"]
  
  '''
  Subnets
  '''
  def search_subnet(neutron_ep, token, subnet_name):
      """search subnet."""
      response= Utils.send_get_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronSubnets), token)
      logging.debug("Successfully Received Subnet List") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "subnets", "name", subnet_name, "id")
  
  def create_subnet(neutron_ep, token, subnet_name, network_id, cidr, external= False, gateway=None, pool_start= None, pool_end= None):
      """crerate subnet."""
      logging.info("Creating Subnet {}".format(subnet_name))
      payload= {
          "subnet": {
              "name": subnet_name,
              "network_id": network_id,
              "ip_version": 4,
              "cidr": cidr
              }
          }
      #if creating external subnet
      payload_external_subnet={
          "enable_dhcp": "true",
          "gateway_ip": gateway,
          "allocation_pools": [{"start": pool_start, "end": pool_end}]
          }
      #merge payload_external_subnet with payload
      if external== "true":
          payload= {"subnet":{**payload["subnet"], **payload_external_subnet}}
      response= Utils.send_post_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronSubnets), token, payload)
      logging.debug("successfully created subnet") if response.ok else response.raise_for_status()
      data= response.json()
      return data['subnet']['id']
  
  def search_and_create_subnet(neutron_ep, token, subnet_name, network_id, subnet_cidr, external= False, gateway=None, pool_start= None, pool_end= None):
      """search subnet by name and create if not found."""
      subnet_id= Neutron.search_subnet(neutron_ep, token, subnet_name)    
      if subnet_id is None:
          subnet_id = Neutron.create_subnet(neutron_ep, token, subnet_name, network_id, subnet_cidr, external, gateway, pool_start, pool_end) 
      logging.debug("subnet id is: {}".format(subnet_id)) 
      return subnet_id
  
  '''
  Router
  '''
  def search_router(neutron_ep, token, router_name):
      """ search router by name."""
      response= Utils.send_get_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronRouters), token)
      logging.debug("successfully received router list") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "routers", "name", router_name, "id")
  
  def create_router(neutron_ep, token, router_name, network_id, subnet_id):
      """create router."""
      logging.info("Creating Router {}".format(router_name))
      payload={"router":
          {"name": router_name,
          "admin_state_up":" true",
          "external_gateway_info": {
              "network_id": network_id,
              "enable_snat": "true",
              "external_fixed_ips": [
                  {
                      "subnet_id": subnet_id
                  }
              ]
          }
          }
  
      }
      response= Utils.send_post_request('{}{}'.format(neutron_ep,OpenStackRestAPIs.NeutronRouters), token, payload)
      logging.debug(response.text)
      logging.debug("successfully created router {}".format(router_name)) if response.ok else response.raise_for_status()  
      data= response.json()
      return data['router']['id']
  
  def set_router_gateway(neutron_ep, token, router_id, network_id):
      """set external gateway of router."""
      payload={"router": {"external_gateway_info": {"network_id": network_id}}}
      response= Utils.send_post_request("{}{}/{}".format(neutron_ep,OpenStackRestAPIs.NeutronRouters,router_id), token, payload)
      logging.debug(response.text)
      logging.debug("successfully set gateway to router {}".format(router_id)) if response.ok else response.raise_for_status()  
  
  def add_interface_to_router(neutron_ep, token, router_id, subnet_id):
      """add interface to router."""
      logging.debug("Adding interface to router Network")
      payload={
      "subnet_id": subnet_id
      }    
      response= Utils.send_put_request('{}{}/{}/add_router_interface'.format(neutron_ep,OpenStackRestAPIs.NeutronRouters,router_id), token, payload)
      logging.debug(response.text)
      logging.debug("successfully added interface to router {}".format(router_id)) if response.ok else response.raise_for_status()  
  
  def remove_interface_from_router(neutron_ep, token, router_id, subnet_id):
      """remove interface router from router."""
      payload={
      "subnet_id": subnet_id
      }
      response= Utils.send_put_request('{}{}/{}/remove_router_interface'.format(neutron_ep,OpenStackRestAPIs.NeutronRouters,router_id), token, payload)
      logging.debug(response.text)
      logging.debug("successfully removed interface from router {}".format(router_id)) if response.ok else response.raise_for_status()  
      #wait for interface to remove
      time.sleep(3)
  
  '''
  Security Groups
  '''
  def get_default_security_group_id(neutron_ep, token, project_id):
      """returns id of admin default security group."""
      response= Utils.send_get_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronSecurityGroups), token)
      logging.debug("successfully received security group list") if response.ok else response.raise_for_status()
      data= response.json()
      for res in (data["security_groups"]):
          if(res["name"]== "default" and res["tenant_id"]== project_id):
              return res["id"]
              break
  
  def search_security_group(neutron_ep, token, security_group_name):
      """seqarch security group by name."""
      response= Utils.send_get_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronSecurityGroups), token)
      logging.debug("successfully received security group list") if response.ok else response.raise_for_status()
      return Utils.parse_json_to_search_resource(response, "security_groups", "name", security_group_name, "id")
  
  def create_security_group(neutron_ep, token, security_group_name):
      """create security group."""
      payload= {
      "security_group": {
          "name": security_group_name,
          }
      }
      response = Utils.send_post_request('{}{}'.format(neutron_ep,OpenStackRestAPIs.NeutronSecurityGroups), token, payload)
      logging.debug("successfully created security Group {}".format(security_group_name)) if response.ok else response.raise_for_status()
      data= response.json()
      return data["security_group"]["id"]
  
  def search_and_create_security_group(neutron_ep, token, security_group_name):
      """search security group and create if not exists."""
      security_group_id= Neutron.search_security_group(neutron_ep, token, security_group_name) 
      if security_group_id is None:
          security_group_id= Neutron.create_security_group(neutron_ep, token, security_group_name)
      logging.debug("security group id is: {}".format(security_group_id)) 
      return security_group_id
  
  def add_icmp_rule_to_security_group(neutron_ep, token, security_group_id):
      """add icmp rule to security group."""
      logging.debug("Adding icmp rules to security group")
      payload= {"security_group_rule":{
              "direction": "ingress",
              "ethertype":"IPv4",
              "direction": "ingress",
              "remote_ip_prefix": "0.0.0.0/0",
              "protocol": "icmp",
              "security_group_id": security_group_id
          }
      }
      response= Utils.send_post_request('{}{}'.format(neutron_ep, OpenStackRestAPIs.NeutronSecurityGroupRules), token, payload)
      logging.debug("Successfully added ICMP rule to Security Group") if response.ok else response.raise_for_status()
  
  def add_ssh_rule_to_security_group(neutron_ep, token, security_group_id):
      """add ssh rule to security group."""
      logging.info("Adding ssh rule to security group")
      payload= {"security_group_rule": {
          "direction": "ingress",
          "ethertype":"IPv4",
          "direction": "ingress",
           "remote_ip_prefix": "0.0.0.0/0",
          "protocol": "tcp",
          "port_range_min": "22",
          "port_range_max": "22",
          "security_group_id": security_group_id
          }
          }
      response= Utils.send_post_request('{}{}'.format(neutron_ep,OpenStackRestAPIs.NeutronSecurityGroupRules), token, payload)
      logging.debug("Successfully added SSH rule to Security Group") if response.ok else response.raise_for_status()
  
  '''
  Floating Ips
  '''
  def parse_port_response(data, server_fixed_ip):
      """parse ports from API response."""
      data= data.json()
      for port in data["ports"]:
          if port["fixed_ips"][0]["ip_address"] == server_fixed_ip:
              return port["id"]   
  
  def get_ports(neutron_ep, token, network_id, server_ip):
      """return ports created on a network."""
      response= Utils.send_get_request("{}{}?network_id={}".format(neutron_ep,OpenStackRestAPIs.NeutronPorts, network_id), token)
      logging.debug("successfully received ports list ") if response.ok else response.raise_for_status()
      return Neutron.parse_port_response(response, server_ip)
  
  def create_floating_ip(neutron_ep, token, network_id, subnet_id, server_ip_address, server_port_id):
      """create floating ip and attach to server port."""
      payload= {"floatingip": 
               {"floating_network_id":network_id,
                "subnet_id": subnet_id,
                "fixed_ip_address": server_ip_address,
                 "port_id": server_port_id
                }
               }
      #wait for creation of floating ip 
      time.sleep(10)
      response= Utils.send_post_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronFloatingIps), token, payload)
      logging.debug(response.text)
      logging.debug("successfully assigned floating ip to server") if response.ok else response.raise_for_status()
      data= response.json()
      return data["floatingip"]["floating_ip_address"], data["floatingip"]["id"]
  
  def create_floatingip_wo_port(neutron_ep, token, network_id ):
      """create floating ip with out attaching to a port."""
      payload= {
          "floatingip": {
              "floating_network_id": network_id
              }
          }
      response= Utils.send_post_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronFloatingIps), token, payload)
      #wait for creation of floating ip 
      time.sleep(10)
      logging.debug(response.text)
      data=response.json()
      logging.debug("successfully created floating ip") if response.ok else response.raise_for_status()
      return data["floatingip"]["floating_ip_address"], data["floatingip"]["id"]
  
  def assign_ip_to_port(neutron_ep, token, port_id, floatingip_id ):
      """attach floating ip with a port."""
      payload= {
          "floatingip": {
              "port_id": port_id
              }
          }
      response= Utils.send_put_request("{}{}/{}".format(neutron_ep,OpenStackRestAPIs.NeutronFloatingIps, floatingip_id), token, payload)
      logging.debug(response.text)
      #wait for floating ip assignement to a port 
      time.sleep(10)
      logging.debug("successfully assigned floating to port") if response.ok else response.raise_for_status()
  
  def get_floating_ip_id(neutron_ep, token, floating_ip):
      """get id of floating ip."""
      response= Utils.send_get_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronFloatingIps), token)
      logging.debug("successfully received floating ips list") if response.ok else response.raise_for_status()
      data= response.json()
      for ips in data["floatingips"]:
          if ips["floating_ip_address"] == floating_ip:
              return ips["id"]
  
  def get_agent_list(neutron_ep, token):
      """get list of agents"""
      response= Utils.send_get_request("{}{}".format(neutron_ep,OpenStackRestAPIs.NeutronAgents), token)
      response= str(response.text)
      return response
  
  def delete_network(neutron_ep, token, network_id):
      """delete network."""
      logging.info("deleting network")
      response= Utils.send_delete_request("{}{}/{}".format(neutron_ep,OpenStackRestAPIs.NeutronNetworks,network_id), token)
      logging.debug(response)
  
  def delete_router(neutron_ep, token, router_id):
      """delete router."""
      logging.info("deleting router")
      response= Utils.send_delete_request("{}{}/{}".format(neutron_ep,OpenStackRestAPIs.NeutronRouters,router_id), token)
      logging.debug(response)
  
  def delete_port(neutron_ep, token, port_id):
      """delete port."""
      logging.info("deleting port")
      response= Utils.send_delete_request("{}{}/{}".format(neutron_ep,OpenStackRestAPIs.NeutronPorts,port_id), token)
      logging.debug(response)