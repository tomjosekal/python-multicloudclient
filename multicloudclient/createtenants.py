import os
import logging
import keystoneclient
from pwgen import pwgen

# Set the display level for logger.Right now INFO will be printed in the logs.
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

tenant_passwords = []

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
    env_keystone = keystoneclient.v2_0.client.Client(username=OS_USERNAME, password=OS_PASSWORD, tenant_name=OS_TENANT_NAME, auth_url=OS_AUTH_URL)
    return (env_keystone)

# tenant exists
def tenant_exists(env_keystone, tenant):
    return tenant in [x.name for x in env_keystone.tenants.list()]

# user validation
def user_exits(env_keystone, user):
    """" Return True if user already exists"""
    return user in [x.name for x in env_keystone.users.list()]

# Tenant creation
def createtenant(env_keystone, tenant_name, description, enabled):
    env_keystone.tenants.create(tenant_name=tenant_name, description=description, enabled=enabled)

# User creation
def createuser(env_keystone, user_name, password, tenant_name, email_id):
    tenant_id=get_tenant_id(env_keystone, tenant_name)
    if (password == ''):
        log.info("Generating 25 character random password since password is blank")
        password=generate_pass(25)
    env_keystone.users.create(name=user_name, password=password, tenant_id=tenant_id, email=email_id)

#  Get tenant_id
def get_tenant_id(env_keystone, name):
    return get_tenant(env_keystone, name).id 

# Python Password Generator:
def password_generator():
    return pwgen(pw_length=25,no_symbols=True)
         
# blank, null checking function:
def is_blank_or_null(value):
    if ((value == '') or (len(value) == 0)):
        return True
    else:
        return False

# Get user_id:
def get_user_id(env_keystone, name):
    return get_user(env_keystone, name).id 

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
    
# Get user details:
def get_user(env_keystone, name):
    """ Retrieve a user by name"""
    users = [x for x in env_keystone.users.list() if x.name == name]
    count = len(users)
    if count == 0:
        raise KeyError("No keystone users with name %s" % name)
    elif count > 1:
        raise ValueError("%d users with name %s" % (count, name))
    else:
        return users[0]
           
def mainmethod(tenant_name, description, email_id, regions):
    try:
        for region in regions: 
                       
            log.info("Configuring tenant and user in "+region)
            log.info("connecting to open_stack")
            
	    check='region'
	    if check=='region':
                log.info("Fetching required region values from the file")
                env_keystone = get_openstack_connections(region)
		log.info("Successfully connected to open_stack")

                
                password=''
                tenant_password = ''
                
                log.info("Enusre the requested tenant not existing")
                if not tenant_exists(env_keystone, tenant_name):
                    log.info("Tenant with the name "+tenant_name+" doesn't exist, so proceeding with tenant creation")
                    # Tenant creation method invocation
                    createtenant(env_keystone, tenant_name, description, True)
                    
                    log.info("Ensure tenant created successfully")
                    if tenant_exists(env_keystone, tenant_name):
                        log.info("Tenant with the name "+tenant_name+" created successfully in regions "+region)
                        
                        log.info("Ensure the requested tenant user not exists")
                        if not user_exits(env_keystone, tenant_name):
                            
                            log.info("User with the name "+tenant_name+" doesn't exist, so proceeding with user creation")
                            
                            log.info("Generating random password for the user "+tenant_name)

                            # Generate random password for the user
                            password = password_generator()
                            
                            log.info("Verifying whether the system generated a valid password")
                            # Checking whether a valid password generate
                            if( is_blank_or_null(password)):
                                log.error("PASSWORD GENERATION LOGIC FAILED")
                                #return "Password generation logic failed"
                                continue
                                
                            else:
                                log.info("Generated a valid password for the user "+tenant_name)
                                log.info("User creation method invocation")
                                
                                # User creation:
                                createuser(env_keystone, tenant_name, password, tenant_name, email_id)
                                log.info("User creation method invocation completed")
                            
                            log.info("Ensure user with name "+tenant_name+" created successfully in region "+region)
                            # Validating the user creation completed successfully
                            if not user_exits(env_keystone, tenant_name):
                                log.error("USER CREATION FAILED SO EXISTING THE USER CREATION IN "+region)
                                # returning User creation failed so return"
                                
                                # TODO delete the tenant creation
                                continue
                            
                            else:
                                print("User with the name "+tenant_name+" created successfully in region "+region)
                                
                        else:
                            log.error("USER WITH NAME "+tenant_name+" ALREADY EXISTS IN "+region)
                            # Returning since user already exists
                            
                            # TODO delete the tenant creation
                            continue
                        
                    else:
                        
                        log.error("TENANT WITH NAME "+tenant_name+" NOT CREATED WHILE EXECUTING THE API METHOD") 
                        # Returning since tenant creation failed
                        
                        # TODO Ensure tenant is deleted
                        continue
                
                else:
                    log.error("TENANT WITH NAME "+tenant_name+" ALREADY EXISTS IN "+region)
                    continue
                
                tenant_password=(region+":"+tenant_name+":"+tenant_name+":").lower()+""+password
                print("PRINTING THE PASSWORD: "+tenant_password)
                is_gpg_file_update_required = True
                tenant_passwords.append(tenant_password)
            else:
                log.error("FILE WITH THE NAME "+completepath+" DOESN'T EXISTS. PLEASE CHANGE THE CODE OR FILE")
        
        
    except Exception, e:
        print e
        for tenant_password in tenant_passwords:
                print(tenant_password)
                
        
if __name__ == '__main__':
    
    mainmethod(tenant_name, description, email_id, regions)
