#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# script confirm.sh to confirm RESIZE operatiomn to Nova controller 
# remember adapt the OPENRC credentials to your account 
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#!/usr/bin/env bash

# This is OpenRC for OpenStack in OPL

# To use an OpenStack cloud you need to authenticate against the Identity
# service named keystone, which returns a **Token** and **Service Catalog**.
# The catalog contains the endpoints for all services the user/tenant has
# access to - such as Compute, Image Service, Identity, Object Storage, Block
# Storage, and Networking (code-named nova, glance, keystone, swift,
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

# With Keysto

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

# NOTE: adjust MAX_COUNTER and SLEEP_TIME to your environment
# (they control the waiting time for entering VERIFY_RESIZE and ACTIVE states)
COUNTER=0
MAX_COUNTER=10
SLEEP_TIME="2"

# wait for entering VERIFY_RESIZE state and send resize confirm afterwards
echo VERIFY_RESIZE being awaited. VM current status:
while [  $COUNTER -lt  $MAX_COUNTER ]; do
    let COUNTER=COUNTER+1
    openstack server list | grep "| test-resizevm-db | VERIFY_RESIZE |"
    if openstack server list | grep -q "| test-resizevm-db | VERIFY_RESIZE |" ; then
        # VERIFY_RESIZE state entered, now Nova expects resize confirm
        openstack server resize confirm test-resizevm-db
        echo "VERIFY_RESIZE entered, resize confirm sent. ACTIVE being awaited..."
        #sleep ${SLEEP_TIME+2}
        let COUNTER=MAX_COUNTER+1
        break
    else
        echo "VERIFY_RESIZE being awaited..."
        sleep ${SLEEP_TIME}
    fi
done

# wait for entering ACTIVE state after sending resize confirm
ACTIVE=1
COUNTER=0
while [  $COUNTER -lt  $MAX_COUNTER ]; do
    let COUNTER=COUNTER+1
    openstack server list | grep "| test-resizevm-db | ACTIVE |"
    if openstack server list | grep -q "| test-resizevm-db | ACTIVE |" ; then
        echo "ACTIVE entered, finishing. VM final status:"
        let ACTIVE=0
        break
    else
        echo "ACTIVE being awaited..."
        sleep ${SLEEP_TIME}
    fi
done

#final result info
if [ $ACTIVE -eq 1 ]; then
    echo "ACTIVE not entered, finishing. VM final status:"
else
    echo "VM final status:"
    openstack server list | grep "test-resizevm-db"
fi
