Multi Cloud Command Line API
This is a command line client and API for implementing various services in multiple Openstack cloud/regions

INSTALLATION:
This package can be installed using pip:

sudo pip install git+https://github.com/tomjosekal/python-multicloudclient.git

For upgrading use: 

sudo pip install git+https://github.com/tomjosekal/python-multicloudclient.git --upgrade

REQUIREMENTS:
For multi tenant services , the environment variables are specific to the regions in which operation needs to be provided. So for every region following environment variables needs to be created.

export OS_USERNAME_=

export OS_PASSWORD_=

export OS_TENANT_NAME_=

export OS_AUTH_URL_=

For example for region 1 R1:

export OS_USERNAME_R1=

export OS_PASSWORD_R1=

export OS_TENANT_NAME_R1=

export OS_AUTH_URL_R1=


COMMAND LINE ARGUMENT FOR CREATING TENANTS ACROSS MULTIPLE CLOUDS:

multi-cloud create-tenants --tenant_id multi --owner owner_name --email owner@email.com --regions R1,R2

The details for the command are:

usage: multi-cloud create-tenants --tenant_id tenant-id --owner user
                                  --email emailid --regions regions

help:

  -h, --help     :       show this help message and exit
  
  -D, --show-details  :   Show detailed information.
  
  --tenant_id tenant-id : 
                        The owner tenant ID.
                        
  --owner user     :     The owner
  
  --email emailid   :    The owner email
  
  --regions regions  :   The owner regions

COMMAND LINE ARGUMENT FOR UPDATING QUOTAS ACROSS MULTIPLE CLOUDS:

If it is needed to use ram and instances according to the number of cores, dont add tha attributes --instances and --rams.

For e.g: multi-cloud quota-update --cores 150 --regions R1,R2 --tenant tenant1 

.This will automatically calculate the number of instances and rams needed according to the number of the cores

But if it is required to add additional instances or ram, then use the attributes --instances and --ram

For e.g:
multi-cloud quota-update --instances 300 --cores 150 --key-pairs 30 --regions R1,R2 --tenant tenant1 

usage: multi-cloud quota-update [-h] [-D] [--overcommit <oversize ram>]
                                [--instances <instances>] [--cores <cores>]
                                [--ram <ram>] [--key-pairs <key-pairs>]
                                --regions regions --tenant <tenant-name>
                                [--user <user-id>] [--o] [--3X]
                                
help: 

  -h, --help     :       show this help message and exit
  
  -D, --show-details  :  Show detailed information.
  
  --overcommit <oversize ram> :
                        Oversizing ram 2:1, 3:1, 15:1
  
  --instances <instances> :
                        New value for the "instances" quota.
  
  --cores <cores>    :    New value for the "cores" quota.
  
  --ram <ram>        :   New value for the "ram" quota.
  
  --key-pairs <key-pairs> : 
                        New value for the "key-pairs" quota.
  
  --regions regions   :  The owner regions
  
  --tenant <tenant-id> : ID of tenant to set the quotas for.
  
  --user <user-id>   :   ID of user to set the quotas for.
  
  --o          :         Flag for overwriting quota
