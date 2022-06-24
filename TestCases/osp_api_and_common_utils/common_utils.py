import pytest
import logging
import paramiko
import os
import configparser
import glob
import time
import sys
from parameters import settings
from keystone import Keystone
from neutron import Neutron
from nova import Nova
from volume import Cinder
from loadbalancer import LoadBalancer
from barbican import Barbican
from parameters import settings
from automatos_framework.shell_manager import ShellManager
sys.path.insert(0, "OSP_test_automation/TestCases/Barbican")
import utils as barbican_utils

ids= {}

def validate_osp_environment(testbed_obj):
  #get SAH node from testbed object
  sah= get_sah(testbed_obj)
  #get shell manager of SAH node
  sah_shell_manager = get_shell_manager(sah)
  #get files path from testbed object
  files_path= get_files_path(testbed_obj)  
  #get features list from testbed object
  features= get_features(testbed_obj)
  #get overcloud public endpoint
  overcloud_ep= get_overcloud_endpoint(testbed_obj)
  #get overcloud token
  overcloud_token= get_overcloud_token(testbed_obj)
  
  #create private networks
  if features.global_mtu== "9000":
    #if mtu 900 is enabled     
    network1_id = Neutron.search_and_create_network(overcloud_ep, overcloud_token, settings["network1_name"], 9000, settings["network_provider_type"], False)
    network2_id = Neutron.search_and_create_network(overcloud_ep, overcloud_token, settings["network2_name"], 9000, settings["network_provider_type"], False)
  else:
    #if mtu 900 is not enabled  
    network1_id = Neutron.search_and_create_network(overcloud_ep, overcloud_token, settings["network1_name"], 1500, settings["network_provider_type"], False)
    network2_id = Neutron.search_and_create_network(overcloud_ep, overcloud_token, settings["network2_name"], 1500, settings["network_provider_type"], False)
  ids["network1_id"]= network1_id
  ids["network2_id"]= network2_id
    
  #cereate subnets
  subnet1_id= Neutron.search_and_create_subnet(overcloud_ep, overcloud_token, settings["subnet1_name"], network1_id, settings["subnet1_cidr"]) 
  subnet2_id= Neutron.search_and_create_subnet(overcloud_ep, overcloud_token, settings["subnet2_name"], network2_id, settings["subnet2_cidr"]) 
  ids["subnet1_id"]= subnet1_id
  ids["subnet2_id"]= subnet2_id

  #verify and create public network
  public_network_id= Neutron.search_network(overcloud_ep, overcloud_token, "public")
  if public_network_id is None:
    #read public network details from ini file
    external_network_settings= sah_shell_manager.run(["grep", "-e", "floating_ip_network_vlan=", "-e", "floating_ip_network=", "-e", "floating_ip_network_gateway=", "-e", "floating_ip_network_start_ip=", "-e", "floating_ip_network_end_ip=", files_path.ini_file]).output.split("\n")
    #create public network
    public_network_id = Neutron.search_and_create_network(overcloud_ep, overcloud_token, "public", 1500, "vlan", "true", "physext", external_network_settings[4].split('=')[1])
    #create public subnet
    public_subnet_id= Neutron.search_and_create_subnet(overcloud_ep, overcloud_token, "external_sub", public_network_id,  external_network_settings[0].split('=')[1], "true",  external_network_settings[3].split('=')[1],  external_network_settings[1].split('=')[1],  external_network_settings[2].split('=')[1])
  else:
    #if public network eist, get subnet id
    public_subnet_id= Neutron.search_subnet(overcloud_ep, overcloud_token, settings["external_subnet"])
    logging.info("Public network exists")
  
  #get id of admin project
  project_id= Keystone.find_admin_project_id(overcloud_ep, overcloud_token)
  ids["project_id"]= project_id
  #get id of default security group
  security_group_id= Neutron.get_default_security_group_id(overcloud_ep, overcloud_token, project_id)
 
  try:
    #add icmp rule to security group
    Neutron.add_icmp_rule_to_security_group(overcloud_ep, overcloud_token, security_group_id)
  except:
    pass
  try:
    #add ssh rule to security group
    Neutron.add_ssh_rule_to_security_group(overcloud_ep, overcloud_token, security_group_id)
  except:
    pass
  ids["security_group_id"]= security_group_id
  
  #search is router is created
  router_id= Neutron.search_router(overcloud_ep, overcloud_token, settings["router_name"])
  if router_id is None:      
    #create router
    router_id= Neutron.create_router(overcloud_ep, overcloud_token, settings["router_name"], public_network_id, public_subnet_id )
  try:
    #add network 1 to router
    Neutron.add_interface_to_router(overcloud_ep, overcloud_token, router_id, subnet1_id)
  except Exception as e:
    logging.debug("can not add port to router")
  try:   
    #add network 2 to router
    Neutron.add_interface_to_router(overcloud_ep, overcloud_token, router_id, subnet2_id)
  except Exception as e:
    logging.debug("can not add port to router")
  ids["router_id"]= router_id
  
  #search if keypair exists
  keypair_key= Nova.search_keypair(overcloud_ep, overcloud_token, settings["key_name"])
  logging.debug("searching ssh key")
  keyfile_name= os.path.expanduser(settings["key_file"])

  if (keypair_key == None):
      #create keypair
      keypair_private_key= Nova.create_keypair(overcloud_ep, overcloud_token, settings["key_name"])
      if os.path.exists(keyfile_name):
        try:
          #delete if .pem file already exists
          logging.debug("deleting old private file")
          #remove if keypair file already exists
          os.system("sudo rm "+keyfile_name)
        except OSError:
          pass
      logging.debug("creating key file")
      #create new .pem file
      keyfile = open(keyfile_name, "w")
      keyfile.write(keypair_private_key)
      keyfile.close()
      #set permissions to .pem file
      logging.debug("setting permission to private key file")
      command= "chmod 400 "+keyfile_name
      os.system(command)
 
  #get image file url and name from ini file
  home = os.path.expanduser('~')
  get_ini_file = glob.glob(os.path.join(home,"*.ini"))
  ini_file = get_ini_file[-1]
  inifile = configparser.ConfigParser()
  inifile.read(ini_file)
  sanity_image_url= inifile.get("Sanity Test Settings", ("sanity_image_url"))
  sanity_image_name= sanity_image_url.split("/")[-1]
  #if image is not already downloaded, download it
  if not os.path.isfile(sanity_image_name):
    os.system("wget {}".format(sanity_image_url)) 
  if features.barbican == "false":
    #if barbican is not enabled create simple image
    image_id= Nova.search_and_create_image(overcloud_ep, overcloud_token, settings["image_name"], "bare", "qcow2", "public", "")
    ids["image_id"] = image_id
    #get status of image
    status= Nova.get_image_status(overcloud_ep, overcloud_token, image_id)
    ids["image_id"] = image_id
    #if status is queued, upload qcow file 
    if status == "queued":
      image_file= open(os.path.expanduser(sanity_image_name), 'rb')
      Nova.upload_file_to_image(overcloud_ep, overcloud_token, image_file, image_id)   
  else:
        #create encrypted image if barbican is enabled
    image_id= Nova.search_image(overcloud_ep, overcloud_token, settings["image_name"])
    if(image_id is None):
      #sign image
      key= barbican_utils.create_ssl_certificate(settings)
      image_signature= barbican_utils.sign_image(settings, sanity_image_name)
      barbican_key_id= barbican_utils.add_key_to_store(overcloud_ep, overcloud_token, key)
      #create image
      image_id= Nova.create_barbican_image(overcloud_ep, overcloud_token, settings["image_name"], "bare", "qcow2", "public", image_signature, barbican_key_id)
    status= Nova.get_image_status(overcloud_ep, overcloud_token, image_id)
    #if status is queued, upload qcow file 
    if status== "queued":
      try:
        image_file= open(os.path.expanduser(sanity_image_name), 'rb')
        Nova.upload_file_to_image(overcloud_ep, overcloud_token, image_file, image_id)
      except Exception as e:
        pass
    
  ids["image_id"] = image_id
     
def get_overcloud_token(testbed_obj):
  #get director node from testbed object
  director= get_director(testbed_obj)
  #get director shell manager 
  shell_manager = get_shell_manager(director)
  #get files path from testbed object
  files_path= get_files_path(testbed_obj)  
  #get username apssword and overcloud endpoint from overcloudrc file
  username, password, overcloud_ep= read_rc_files(shell_manager, files_path.overcloudrc_file)
  #get token from openstack API 
  token= Keystone.get_authentication_token(overcloud_ep, username, password)
  return token

def get_undercloud_token(testbed_obj):
  #get director node from testbed object
  director= get_director(testbed_obj)
  #get director shell manager 
  shell_manager = get_shell_manager(director)
  #get files path from testbed object
  files_path= get_files_path(testbed_obj)  
  #get username apssword and overcloud endpoint from overcloudrc file
  username, password, overcloud_ep= read_rc_files(shell_manager, files_path.stackrc_file)
  #get token from openstack API 
  token= Keystone.get_authentication_token(overcloud_ep, username, password)
  return token

def get_director(testbed_obj):
  #get openstack object from testbed object
  osp= testbed_obj.openstack_list[0]
  #get cluster object from openstack object
  osp_cluster= next(osp.clusters)
  #get nodes from cluster object
  node = next(osp_cluster.node)
  return node.director

def get_sah(testbed_obj):
  #get openstack object from testbed object
  osp= testbed_obj.openstack_list[0]
  #get cluster object from openstack object
  osp_cluster= next(osp.clusters)
  #get nodes from cluster object
  node = next(osp_cluster.node)
  return node.sah

def get_files_path(testbed_obj):
  #get openstack object from testbed object
  osp= testbed_obj.openstack_list[0]
  #get cluster object from openstack object
  osp_cluster= next(osp.clusters)
  return osp_cluster.filepath

def get_features(testbed_obj):
  #get openstack object from testbed object
  osp= testbed_obj.openstack_list[0]
  #get cluster object from openstack object
  osp_cluster= next(osp.clusters)
  return osp_cluster.feature

  
def read_rc_files(shell_manager, rcfile_path):
    #read user name from rc file
    username= shell_manager.run(["grep", "OS_USERNAME", rcfile_path]).output.strip().split('=')[1]
    #read user password from rc file
    password= shell_manager.run(["grep", "OS_PASSWORD", rcfile_path]).output.strip().split('=')[1]
    #read endpoint name from rc file
    endpoint= shell_manager.run(["grep", "OS_AUTH_URL", rcfile_path]).output.strip().split('=')[1][:-5]  
    return username, password, endpoint
 
def get_shell_manager(server):
        """Get Shell Manager object
        Args:
            node (required, ServerController): ServerController object from
             Automatos
        Returns:
            shell_manager: ShellManager object
        """
    
        shell_manager = ShellManager(name='openstack',
                                     address=server.ip_address,
                                     shell_type='ssh', port=22,
                                     username=server.username,
                                     password=server.password)
        return shell_manager

#create flavor and return id
def get_flavor_id(testbed_obj, feature, flavor_name, vcpus=None, ram=None, disks=None, mem_page_size="large" ):
    #get files path from testbed object
    files_path= get_files_path(testbed_obj)  
    #get features list from testbed object
    features= get_features(testbed_obj)
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #if vcpus is none then read from params.json
    if vcpus is None:
        vcpus= settings.get("flavor_vcpus")
    #if ram is none then read from params.json
    if ram is None:
        ram= settings.get("flavor_ram")
    #if disks is none then read from params.json
    if disks is None:
        disks= settings.get("flavor_disks")
    
    #create flavor
    flavor_id= Nova.search_and_create_flavor(overcloud_ep, overcloud_token, flavor_name, ram, vcpus, disks)
    #put numa specs in flavor
    if (feature=="numa"):
        Nova.put_extra_specs_in_flavor(overcloud_ep, overcloud_token, flavor_id, True)
    #put hugepage specs in flavor
    if (feature=="hugepage"):
        Nova.put_extra_specs_in_flavor(overcloud_ep, overcloud_token, flavor_id , False , mem_page_size)
    #put dpdk specs in flavor
    if (feature=="dpdk"):
        Nova.put_ovs_dpdk_specs_in_flavor(overcloud_ep, overcloud_token, flavor_id)
    #if numa is enabled with any otehr NFV or non NFV feature 
    if (feature=="sriov" or feature=="barbican" or feature=="dvr" or feature=="mtu9000" or feature=="dpdk" or feature=="offloading" or feature=="powerflex"):
        features= get_features(testbed_obj)
        if(features.numa == "true"):
            Nova.put_extra_specs_in_flavor(overcloud_ep, overcloud_token, flavor_id, True)
    return flavor_id
#delete flavor
def delete_flavor(testbed_obj, flavor_id):
    """delete flavor."""
    logging.info("deleting flavor")
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete flavor through openstack API
    Nova.delete_flavor(overcloud_ep, overcloud_token, flavor_id)

#delete instance    
def delete_instance(testbed_obj, instance):
    """delete flavor."""
    logging.info("deleting flavor")
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete instance through openstack API
    Nova.delete_server(overcloud_ep, overcloud_token, instance)

def delete_port(testbed_obj, port_id):
    """delete port."""
    logging.info("deleting port")
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete port through openstack API
    Neutron.delete_port(overcloud_ep, overcloud_token, port_id)
    
def delete_volume(testbed_obj, project_id , volume_id):
    """delete volume."""
    logging.info("deleting volume")
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete flavor through openstack API
    Cinder.delete_volume(overcloud_ep, overcloud_token, project_id, volume_id)
    
def delete_image(testbed_obj , image_id):
    """delete image."""
    logging.info("deleting image")
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete image through openstack API 
    Nova.delete_image(overcloud_ep, overcloud_token, image_id)
    
def delete_loadbalancer_pool(testbed_obj, pool_id):
    """delete loadbalancer pool."""
    logging.info("deleting loadbalancer pool")
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete LoadBalancer pool through openstack API
    LoadBalancer.delete_loadbalancer_pool(overcloud_ep, overcloud_token, pool_id) 

def delete_loadbalancer_listener(testbed_obj, listener_id):
    """delete loadbalancer listener."""
    logging.info("deleting loadbalancer listener")    
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete LoadBalancer Listener through openstack API
    LoadBalancer.delete_loadbalancer_listener(overcloud_ep, overcloud_token, listener_id)  
           
def delete_loadbalancer(testbed_obj, loadbalancer_id):
    """delete loadbalancer listener."""
    logging.info("deleting loadbalancer")    
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete LoadBalancer Listener through openstack API
    LoadBalancer.delete_loadbalancer(overcloud_ep, overcloud_token, loadbalancer_id)  
    
def delete_floating_ip(testbed_obj, floating_ip_id):
    """delete loadbalancer floating ip"""
    logging.info("deleting loadbalancer floating ip")    
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #delete LoadBalancer Listener through openstack API               
    Nova.delete_floating_ip(overcloud_ep, overcloud_token, floating_ip_id)    
        
def create_instance(testbed_obj, flavor_id, server_name, network_name, network_id, compute=None, skip_floaating_ip_assignment="No", feature=None, subnet_id=None):
    server={}
    logging.info("deleting flavor")
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    #get features list from testbed object
    features= get_features(testbed_obj)
    #if sriov or hardware offloading is enabled
    if feature == "sriov" or feature == "feature":
        if features == "smart_nic":
            #create port for offloading
            port_id, port_ip= Neutron.create_port(overcloud_ep, overcloud_token, network_id, subnet_id, settings["sriov_port_name"], "vflag")
        else:
            #create port for SRIOV
            port_id, port_ip= Neutron.create_port(overcloud_ep, overcloud_token, network_id, subnet_id, settings["sriov_port_name"])
        #create SRIOV enabled instance
        server_id= Nova.search_and_create_sriov_server(overcloud_ep, overcloud_token, server_name, ids.get("image_id"), settings["key_name"], flavor_id,  port_id, ids.get("security_group_id"), compute)
        server["port_id"]=port_id
    else:
        #create instance
        server_id= Nova.search_and_create_server(overcloud_ep, overcloud_token, server_name, ids.get("image_id"), settings["key_name"], flavor_id, network_id, ids.get("security_group_id"), compute)
    server["id"]=server_id
    #wait for server to build
    Nova.server_build_wait(overcloud_ep, overcloud_token, [server_id])
    #get status of server
    status= Nova.check_server_status(overcloud_ep, overcloud_token, server_id)
    server["status"]=status
   
    if(status=="active" and skip_floaating_ip_assignment=="No"):
        if feature !="sriov":
            #get ip of server
            server_ip= Nova.get_server_ip(overcloud_ep, overcloud_token, server_id, network_name)
            server["ip"]=server_ip
        else:
            server_ip= port_ip
            server["ip"]=port_ip
        #get floating ip of server
        floating_ip= Nova.get_server_floating_ip(overcloud_ep, overcloud_token, server_id, network_name)
        #get id of floating ip
        floating_ip_id= Neutron.get_floating_ip_id(overcloud_ep, overcloud_token, floating_ip)
        server["floating_ip_id"]=floating_ip_id
        #if floating ip is not assigned
        if floating_ip is None: 
            #get port id of server
            server_port= Neutron.get_ports(overcloud_ep, overcloud_token, network_id, server_ip)
            #get id of public network
            public_network_id= Neutron.search_network(overcloud_ep, overcloud_token, settings["external_network_name"])
            #get id of public subnet
            public_subnet_id= Neutron.search_subnet(overcloud_ep, overcloud_token, settings["external_subnet"])
            floating_ip, floating_ip_id= Neutron.create_floating_ip(overcloud_ep, overcloud_token, public_network_id, public_subnet_id, server_ip, server_port)
            #Wait for instance to complete boot
            Nova.wait_instance_boot(floating_ip, settings["instance_boot_wait_retires"])
        server["floating_ip"]=floating_ip
        server["floating_ip_id"]=floating_ip_id 
    return server
    
#get baremetal nodes    
def baremetal_nodes(testbed_obj):
  #get overcloud public endpoint
  undercloud_ep= get_undercloud_endpoint(testbed_obj)
  #get overcloud token
  undercloud_token= get_undercloud_token(testbed_obj)
  #get name and ip adress of baremetal nodes 
  baremetal_nodes_detail= Nova.get_baremeta_nodes_ip(undercloud_ep, undercloud_token)
  return baremetal_nodes_detail

#get compute host names
def compute_host_name(testbed_obj):
  #get overcloud public endpoint
  overcloud_ep= get_overcloud_endpoint(testbed_obj)
  #get overcloud token
  overcloud_token= get_overcloud_token(testbed_obj)
  #get names of compute hosts
  baremetal_nodes_detail= Nova.get_compute_host_list(overcloud_ep, overcloud_token)
  return baremetal_nodes_detail
  
def get_overcloud_endpoint(testbed_obj):
  #get director node from testbed object
  director= get_director(testbed_obj)
  #get shell manager of director node
  director_shell_manager = get_shell_manager(director)
  #get files path from testbed object
  files_path= get_files_path(testbed_obj)  
  #get overcloud endpoint 
  username, password, overcloud_ep= read_rc_files(director_shell_manager, files_path.overcloudrc_file)
  return overcloud_ep
  
def get_undercloud_endpoint(testbed_obj):
  #get director node from testbed object
  director= get_director(testbed_obj)
  #get shell manager of director node
  director_shell_manager = get_shell_manager(director)
  #get files path from testbed object
  files_path= get_files_path(testbed_obj)  
  #get overcloud endpoint 
  username, password, overcloud_ep= read_rc_files(director_shell_manager, files_path.stackrc_file)
  return overcloud_ep  

def ssh_into_node(host_ip, command, user_name="heat-admin"):
    try:
        logging.debug("Trying to connect with node {}".format(host_ip))
        # ins_id = conn.get_server(server_name).id
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        #if username is root
        ssh_session = ssh_client.connect(host_ip, username=user_name, key_filename=os.path.expanduser("~/.ssh/id_rsa")) 
        logging.debug("Running command in a compute node")
        #run command
        stdin, stdout, stderr = ssh_client.exec_command(command)
        logging.debug("command {} successfully executed on node {}".format(command, host_ip))
        #decode output
        output= stdout.read().decode('ascii')
        error= stderr.read().decode('ascii')
        
        return output, error
    except Exception as e:
        logging.exception(e)
        logging.error("error ocurred when making ssh connection and running command on remote server") 
    finally:
        ssh_client.close()
        logging.debug("connection from client has been closed") 

  
def cold_migrate_instance(testbed_obj, instance_id, instance_floating_ip):
    #get overcloud endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud endpoint
    overcloud_token= get_overcloud_token(testbed_obj)
    #cold migrate server
    response=  Nova.perform_action_on_server(overcloud_ep, overcloud_token, instance_id, "migrate")
    logging.info("Waiting for migration")
    #wait for instance to start migration
    time.sleep(30)
    if response==202:
        logging.info("confirming migration")
        #confirm migration
        Nova.perform_action_on_server(overcloud_ep, overcloud_token, instance_id, "confirmResize")
        #wait for server to start migration
        time.sleep(30)
        #wait untill instance compeltes mif=gration
        Nova.wait_instance_boot(instance_floating_ip, settings["instance_boot_wait_retires"])
    return response 
  
def get_compute_name(testbed_obj, compute):
    #get compute nodes
    compute_nodes= compute_host_name(testbed_obj)
    #search specific compute host
    compute= [key for key in compute_nodes if compute in key] 
    return compute[0]
    
def get_compute_ip(testbed_obj, compute):
    #get baremetal nodes
    compute_nodes= baremetal_nodes(testbed_obj)
    #search ip adeess of specific compute node
    compute= [val for key, val in compute_nodes.items() if compute in key]
    return compute[0]
 
def get_controller_ip(testbed_obj, controller):
    #get baremetal nodes
    controller_nodes= baremetal_nodes(testbed_obj)
    #search ip adeess of specific compute node
    controller= [val for key, val in controller_nodes.items() if controller in key]
    return controller[0]        
    
def check_if_feature_is_enabled(testbed_obj,feature):
    #testcases_detail[currentFuncName(1)]= [feature, "Unknown", ""]
    #skip test if feature not enabled
    get_feature = get_features(testbed_obj)
    verify_feature_deployment= getattr(get_feature,"{}".format(feature))
    if verify_feature_deployment != "true":
        #logging.info("{} Test case : Skipped".format(feature))
        pytest.skip()


def check_if_feature_is_enabled(feature):
    #ini_get=[]
    home = os.path.expanduser('~')
    get_ini_file = glob.glob(os.path.join(home,"*.ini"))
    ini_file = get_ini_file[-1]
    get_inifile = configparser.ConfigParser()
    get_inifile.read(ini_file)
    if feature == "mtu_size_global_default":
        get_feature_info = get_inifile.get("MTU Settings", ("{}".format(feature)))
        if get_feature_info != "9000":
            pytest.skip()
        else:
            pass
    if feature == "enable_powerflex_backend":
        get_feature_info = get_inifile.get("Storage back-end Settings", ("{}".format(feature)))
        if get_feature_info != "true":
            pytest.skip()
        else:
            pass           
    else:
      get_feature_info = get_inifile.get("Dell NFV Settings", ("{}".format(feature)))
      if get_feature_info != "true":
          pytest.skip()
      else:
          pass
    return get_feature_info
    
def post_check(feature_condition):
    if feature_condition != "true":
        pytest.skip()            
       
def get_all_baremtal_nodes_ip(testbed_obj, baremetal):
    #get baremetal nodes
    compute_nodes= baremetal_nodes(testbed_obj)
    #search ip adeess of specific compute node
    compute= [val for key, val in compute_nodes.items() if baremetal in key]
    return compute
    
def restart_service_on_node(node, service):
    command= "sudo systemctl restart {}".format(service)
    ssh_into_node(node, command)
    time.sleep(3)    
 
def reboot_server(nova_ep,token, server_id):
    Nova.reboot_server(nova_ep,token, server_id)
    
def server_build_wait(nova_ep, token, server_ids):
    Nova.server_build_wait(nova_ep, token, server_ids)   
    
#Volume functions    
   
def check_volume_status(testbed_obj, project_id, volume_id):
    overcloud_token = get_overcloud_token(testbed_obj)
    overcloud_ep = get_overcloud_endpoint(testbed_obj)
    status= Cinder.check_volume_status(overcloud_ep, overcloud_token, project_id, volume_id)
    return status

def attach_volume(testbed_obj, project_id , server1_id, volume_id):
    overcloud_token = get_overcloud_token(testbed_obj)
    overcloud_ep = get_overcloud_endpoint(testbed_obj)
    Cinder.attach_volume_to_server(overcloud_ep, overcloud_token, project_id , server1_id, volume_id, "/dev/vdd")

def detach_volume(testbed_obj, project_id , server1_id, volume_id):
    overcloud_token = get_overcloud_token(testbed_obj)
    overcloud_ep = get_overcloud_endpoint(testbed_obj)
    Cinder.detach_volume_from_server(overcloud_ep, overcloud_token, project_id , server1_id, volume_id, "/dev/vdd")
             
def create_volume(testbed_obj, project_id, volume_name, volume_size, backend=None, image_id=None):
    overcloud_token = get_overcloud_token(testbed_obj)
    overcloud_ep = get_overcloud_endpoint(testbed_obj)    
    Cinder.create_volume(overcloud_ep, overcloud_token, project_id, volume_name, volume_size, backend=None, image_id=None)
    
def search_and_create_volume(testbed_obj, project_id, volume_name, volume_size, backend=None, image_id=None):
    overcloud_token = get_overcloud_token(testbed_obj)
    overcloud_ep = get_overcloud_endpoint(testbed_obj)    
    volume_id= Cinder.search_volume(overcloud_ep, overcloud_token, volume_name, project_id)
    if volume_id is None:
        volume_id= Cinder.create_volume(overcloud_ep, overcloud_token, project_id, volume_name, volume_size, None, None)
    logging.debug("Volume id: "+volume_id)    
    return volume_id    
    
#********** Volume *******************        

def ping_test_between_instances(ip, ping_ip, settings, command=None):
    if command is None:
        command="ping  -c 3 {}".format(ping_ip)
    try:
        remove_key= "ssh-keygen -R {}".format(ip)
        os.system(remove_key)
    except:
        pass
    retries=0
    while(1):
        try:
            client= paramiko.SSHClient()
            paramiko.AutoAddPolicy()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=22, username="centos", key_filename=os.path.expanduser(settings["key_file"]))
            logging.debug("SSH Session is established")
            logging.debug("Running command in a compute node")
            stdin, stdout, stderr = client.exec_command(command)
            logging.info("command {} successfully executed on instance")
            output= stdout.read().decode('ascii')
            error= stderr.read().decode('ascii')
            logging.info("command {} successfully executed on instance".format(command))

            if error =="" and "icmp_seq=3 Destination Host Unreachable" not in output and "ttl=" in output:
                return True, output, error
            else:
                return False, output, error
            client.close()
        except Exception as e:
            logging.exception(e)
            logging.error("error ocurred when making ssh connection and running command on remote server") 
            time.sleep(30)
        retries=retries+1
        if(retries==settings["instance_ssh_wait_retires"]):
            break

def perform_action_on_server(nova_ep,token, server_id, action):
    for instance in server_id:
      if instance == "error":
        pass
      else:          
        Nova.perform_action_on_server(nova_ep,token, instance.get("id"), action)
        time.sleep(10)
    
def resize_server(nova_ep,token, server_id, flavor_id):
    resize_status = Nova.resize_server(nova_ep,token, server_id, flavor_id) 

def instance_ssh_test(ip, settings):
    """
    """
    try:
        remove_key= "ssh-keygen -R {}".format(ip)
        os.system(remove_key)
    except:
        pass
    retries=0
    ssh=False
    while(1):
        try:
            client= paramiko.SSHClient()
            paramiko.AutoAddPolicy()
            client.load_system_host_keys()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(ip, port=22, username="centos", key_filename=os.path.expanduser(settings["key_file"]))
            ssh= True
            break
        except Exception as e:
            logging.exception(e)
            logging.debug("Waiting for server to ssh")
            time.sleep(30)
        retries=retries+1
        if(retries==settings["instance_ssh_wait_retires"]):
            break
    return ssh    
    
def create_server_snapshot(overcloud_ep,overcloud_token, server_id, snapshot_name):
    snapshot=Nova.create_server_snapshot(overcloud_ep,overcloud_token, server_id, snapshot_name)
    return snapshot
    
def search_and_create_sriov_server(nova_ep, token, server_name, image_id, key_name, flavor_id,  port_id, security_group_id, host=None):
    server_id= Nova.search_server(nova_ep, token, server_name)
    if server_id is None:
        server_url= Nova.create_sriov_server(nova_ep, token, server_name, image_id, key_name, flavor_id, port_id, security_group_id, host)
        server_id= Nova.get_server_detail(token, server_url)
    logging.debug("Server id: "+server_id)  
    return server_id 

def check_server_status(nova_ep, token, server_id):
    status = Nova.check_server_status(nova_ep, token, server_id)
    return status 
    
def delete_secret(testbed_obj, secret_id):
    """delete secret."""
    logging.info("deleting secret")
    #get overcloud public endpoint
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    #get overcloud token
    overcloud_token= get_overcloud_token(testbed_obj)
    Barbican.delete_secret(overcloud_ep, overcloud_token , secret_id)
    
    
def restart_baremetal_node(baremetal_node, settings):
    #reboot node
    ssh_output= ssh_into_node(baremetal_node, "sudo reboot")    
    #wait for system to shutdown
    time.sleep(30)
    #wait for node to restart
    retries=0
    while(1):
        response = os.system("ping -c 3 " + baremetal_node)
        if response == 0:
            logging.debug ("Ping successfull!") 
            return True
        logging.debug("Waiting for server to boot")
        time.sleep(30)
        retries=retries+1
        if(retries == settings.get("bare_metal_node_wait_retires")):
            return False                  

def start_service_on_node(node, service):
    command= "sudo systemctl start {}".format(service)
    ssh_into_node(node, command)
    time.sleep(3)
        
def stop_service_on_node(node, service):
    command= "sudo systemctl stop {}".format(service)
    ssh_into_node(node, command)
    time.sleep(3)
    
def check_server_status(overcloud_ep, overcloud_token, server_id):
    Nova.check_server_status(overcloud_ep, overcloud_token, server_id)
 
def delete_server_with_id(testbed_obj, server_id):
    overcloud_ep= get_overcloud_endpoint(testbed_obj)
    overcloud_token= get_overcloud_token(testbed_obj)
    Nova.delete_server_with_id(overcloud_ep, overcloud_token, server_id)
    
def search_and_create_server(nova_ep, token, server_name, image_id, key_name, flavor_id,  network_id, security_group_id, host=None, availability_zone= None):
    server=Nova.search_and_create_server(nova_ep, token, server_name, image_id, key_name, flavor_id,  network_id, security_group_id, host=None, availability_zone= None)
    return server
                        