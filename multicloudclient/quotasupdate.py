import os
import logging
from cStringIO import StringIO
from novaclient import client
import keystoneclient

# Define the Global Variables.
auditString = StringIO()

# Set the display level for logger.Right now INFO will be printed in the logs.
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Get nova and keystone client for access to API's
def get_openstack_connections(region):
    OS_USERNAME = os.environ.get('OS_USERNAME_' + region,'')
    if ( is_blank_or_null(OS_USERNAME)):
        log.error("No environment variable found with the name OS_USERNAME_" + region)
    OS_PASSWORD = os.environ.get('OS_PASSWORD_' + region,'')
    if ( is_blank_or_null(OS_PASSWORD)):
        log.error("No environment variable found with the name OS_PASSWORD_" + region)
    OS_TENANT_NAME = os.environ.get('OS_TENANT_NAME_'+ region,'')
    if ( is_blank_or_null(OS_TENANT_NAME)):
        log.error("No environment variable found with the name OS_TENANT_NAME_" + region)
    OS_AUTH_URL = os.environ.get('OS_AUTH_URL_' + region,'')
    if ( is_blank_or_null(OS_AUTH_URL)):
        log.error("No environment variable found with the name OS_AUTH_URL_"+ region)
    nova = client.Client("2",username=OS_USERNAME,api_key=OS_PASSWORD,project_id=OS_TENANT_NAME, auth_url=OS_AUTH_URL)
    keystone = keystoneclient.v2_0.client.Client(username=OS_USERNAME, password=OS_PASSWORD, tenant_name=OS_TENANT_NAME, auth_url=OS_AUTH_URL)
    log.debug("Nova and Keystone configured in " + region)
    return nova,keystone

#  Get tenant_id
def get_tenant_id(env_keystone, name):
    return get_tenant(env_keystone, name).id

# Get tenant details:
def get_tenant(env_keystone, name):
    """ Retrieve a tenant by name"""
    tenants = [x for x in env_keystone.tenants.list() if x.name == name]
    count = len(tenants)
    if count == 0:
        raise KeyError("No keystone tenants with name %s" % name)
    elif count > 1:
        raise ValueError("%d tenants with name %s" % (count, name))
    else:
        return tenants[0]

# Check if the value is null or not 
def is_blank_or_null(value):
    if ((value == '') or (len(value) == 0)):
        return True
    else:
        return False

def mainmethod(args):
    try:
        regions=args.regions.split(',')
        for region in regions:
            log.info("Configuring openstack connection in  "+region)
            nova,keystone = get_openstack_connections(region)
            tenantId= get_tenant_id(keystone,args.tenant)
            log.info("Tenant Id is   "+ tenantId)
            updates = {}

            #Get the current quota
            currentquota = nova.quotas.get(tenantId)
            # get quota update values from command line
            addcores = getattr(args,'cores')
            addinstances = getattr(args,'instances')
            addram  = getattr(args,'ram', 0)
            addkeypair= getattr(args,'key_pairs')
            isoverwrite= getattr(args,'o',False)
            is3xVM= getattr(args,'3X',False)
            overcommit= getattr(args,'overcommit',False)
            
            # if no instances and ram are added from the command , 
            # they will be calculated from number of cores.
            if addcores is not None:
                if addinstances is None:
                        addinstances = addcores/2
                if addram is None:
                    if(is3xVM==True):
                        addram = addcores * 180 * 1024
                    elif (overcommit=='2:1'):
                        addram = addcores * 2976
                    elif (overcommit=='3:1'):
                        addram = addcores * 2048
                    else:
                        addram = addcores * 2976

            # If overwrite flag is false, add the number of quota values to the current values
            # Else if overwrite flag is true , just overwrite the current values. 
            if(isoverwrite == False):
                if addcores is not None:
                    updates['cores'] = addcores + getattr(currentquota, 'cores', None)
                if addinstances is not None:
                    updates['instances'] = addinstances + getattr(currentquota, 'instances', None)
                if addram is not None:
                    updates['ram'] = addram + getattr(currentquota, 'ram', None)
                if addkeypair is not None:
                    updates['key_pairs'] = addkeypair + getattr(currentquota, 'key_pairs', None)
            else:
                updates['cores'] = addcores
                updates['instances']=addinstances
                updates['ram']=addram
                updates['key_pairs']=addkeypair

            addAudit("\nUpdating %s QUOTA in %s " %(str(args.tenant), str(region)))
            addAudit("\nBefore QUOTA-UPDATE\n %s" %str(nova.quotas.get(tenantId)))

            # Updating QUOTA
            nova.quotas.update(tenantId,**updates)

            addAudit("\nQUOTA_UPDATE\n %s" %str(updates))
            addAudit("\nAfter QUOTA-UPDATE\n %s" %str(nova.quotas.get(tenantId)))

        log.info("Quota updated")
        return auditString.getvalue()
    except Exception, e:
        log.error("%s", e)
        log.error("problem in updating quota")
        addAudit("\nERROR While updating QUOTA for tenant %s" %str(tenantId))
        return auditString.getvalue()

# Add Audit log
def addAudit( auditdata ):
    """
    """
    auditString.write(auditdata)

if __name__ == '__main__':

    mainmethod(args)
    auditString.close()

