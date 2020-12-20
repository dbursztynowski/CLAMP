#++++++++++++++++++++++++++++++++++++================================================
# resize2m1.sh - resize  to m1.large (see below)
# remember in OpenStack you can not resize to flavor with a smaller disk than 
# current size; disk can only bi scaled up (but no such constrints on CPU and memory)
#+++++++++++++++++++++++++++++++++++=================================================

#!/usr/bin/env bash

# This is OpenRC for OpenStack in OPL

# To use an OpenStack cloud you need to authenticate against the Identity
# service named keystone, which returns a **Token** and **Service Catalog**.
# The catalog contains the endpoints for all services the user/tenant has
# access to - such as Compute, Image Service, Identity, Object Storage, Block
# Storage, and Networking (code-named nova, glance, keystone, swift,;
# cinder, and neutron).
#
# *NOTE*: Using the 3 *Identity API* does not necessarily mean any other
# OpenStack API is version 3. For example, your cloud provider may implement
# Image API v1.1, Block Storage API v2, and Compute API v2.0. OS_AUTH_URL is
# only for the Identity API served through keystone.
export OS_AUTH_URL=http://192.168.186.11:5000/v3

# With the addition of Keystone we have standardized on the term **project**
# as the entity that owns the resources.
export OS_PROJECT_ID=91c65cbfd8d94538944415591e111ca7
export OS_PROJECT_NAME="CLAMP"
export OS_USER_DOMAIN_NAME="Default"
if [ -z "$OS_USER_DOMAIN_NAME" ]; then unset OS_USER_DOMAIN_NAME; fi

# unset v2.0 items in case set
unset OS_TENANT_ID
unset OS_TENANT_NAME

# In addition to the owning entity (tenant), OpenStack stores the entity
# performing the action as the **user**.
export OS_USERNAME="burszdar"

# With Keystone you pass the keystone password.
#echo "Please enter your OpenStack Password for project $OS_PROJECT_NAME as user $OS_USERNAME: "
#read -sr OS_PASSWORD_INPUT
#export OS_PASSWORD=$OS_PASSWORD_INPUT
export OS_PASSWORD=t6ygfr5

# If your configuration has multiple regions, we set that information here.
# OS_REGION_NAME is optional and only valid in certain environments.
export OS_REGION_NAME="RegionOne"
# Don't leave a blank variable, unset it if it was empty
if [ -z "$OS_REGION_NAME" ]; then unset OS_REGION_NAME; fi

export OS_INTERFACE=public
export OS_IDENTITY_API_VERSION=3

echo  Resize - initial VM status:
openstack server list | grep test-resizevm-db

echo Calling Nova to resize the VM.
nova resize test-resizevm-db m1.large --poll

if [ "$?" = "0" ] ; then
    echo
    echo Nova resize finished. Going to confirm...
    source confirm.sh
else
    echo "Exiting for Nova error notification."  1>&2
    exit 1
fi
