

class OpenStackRestAPIs():  # pylint: disable=too-few-public-methods
    """Class of supported PowerFlex Rest API base paths"""
    
    #Barbican
    GetBarbicanSecrets=':9311/v1/secrets'
    GetBarbicanOrders=':9311/v1/orders'
    
    #Keystone
    GetToken = ':5000/v3/auth/tokens'
    GetProject= ':5000/v3/projects'
    
    #Neutron
    NeutronNetworks= ':9696/v2.0/networks'
    NeutronPorts= ':9696/v2.0/ports'
    NeutronSubnets= ':9696/v2.0/subnets'
    NeutronRouters= ':9696/v2.0/routers'
    NeutronSecurityGroups= ':9696/v2.0/security-groups'
    NeutronSecurityGroupRules= ':9696/v2.0/security-group-rules'
    NeutronFloatingIps= ':9696/v2.0/floatingips'
    NeutronAgents= ':9696/v2.0/agents'
    
    #Nova
    NovaFlavors= ':8774/v2.1/flavors'
    NovaKeypair= ':8774/v2.1/os-keypairs'
    NovaImages= ':9292/v2.1/images'
    NovaServers=':8774/v2.1/servers'
    NovaQuotaSets=':8774/v2.1/os-quota-sets'
    NovaOsAggregates=':8774/v2.1/os-aggregates'
    NovaHostList=':8774/v2.1/os-hosts'
    
    #Volume(Cinder)
    GetServers=':8774/v2.1/servers'
    GetVolumes=':8776/v3'
    
    #Load Balancer
    LoadBalancers=':9876/v2.0/lbaas/loadbalancers'
    Listeners=':9876/v2.0/lbaas/listeners'
    Pools=':9876/v2.0/lbaas/pools'
    HealthMonitors=':9876/v2.0/lbaas/healthmonitors'
    FloatingIps=':9696/v2.0/floatingips'
    Policies=':9876/v2.0/lbaas/l7policies'
    
    
