#!/bin/bash

# NOTICE:
# in ONAP environment, for long-living run this script with 'nohup', and as startup 
# script according to https://transang.me/create-startup-scripts-in-ubuntu/ 
# the best option is to prepare VM image with all these settings  present
# while logged in on the machine, trace current logs of the script using:
# tail -f nohup.out 
# if needed, one can clear nohup.out by: cat /dev/null > nohup.out
# use -v while running the script for detailed curl output

# URIs for use
testURI="http://10.254.184.197:8888"
vesURI='https://10.254.184.250:30417/eventListener/v5'
#vesURI='https://portal.api.simpledemo.onap.org:30417/eventListener/v

echo ""
echo "agent-wef.sh:: Use parameter -v for a detailed curl output."
echo ""

# MME fetching / VES reporting loop
while true
do

echo
echo "fetching statistics from WEF"

#==========================================================
# Fetch recent stats from MME
#==========================================================
# below, adjust the file name for the MME side appropriately to your goal (use the namer 
# mme-clamp-test.log for testing ousing fake MME machine and mme-clamp.log for real WEF cluster)
# for tesing purposes, on the MME side, set MME_VM_NAME field equal to "vofwl01fwl-ad"
# which is consistent with vFW use case settings

mme_clamp_log_name="mme-clamp-test.log" #fake for testing
#mme_clamp_log_name="mme-clamp.log"     #actual stats

if [ "$1" = "-v" ]
then
  curl -v http://10.254.184.197:8888/$mme_clamp_log_name --output mme-clamp.log
else
  curl http://10.254.184.197:8888/$mme_clamp_log_name --output mme-clamp.log
fi

# extract stats' values from the fetched log file
MME_VM_NAME=$(grep -oP "MME_VM_NAME\K.*" ./mme-clamp.log)
Connected_enbs=$(grep -oP "Connected_eNBs\K.*" ./mme-clamp.log)
Connected_ues=$(grep -oP "Connected_UEs\K.*" ./mme-clamp.log)
Attached_ues=$(grep -oP "Attached_UEs\K.*" ./mme-clamp.log)
Default_bearers=$(grep -oP "Default_Bearers\K.*" ./mme-clamp.log)
S1_U=$(grep -oP "S1-U_Bearers\K.*" ./mme-clamp.log)
#oryginal: S1_U=$(grep -oP "S1-U_Bearers\K.*" ./mme-clamp.log | tail -1 | awk '{print "S1-U_Bearers", $2}')

echo "agent-wf.sh > statistics fetched:: MME name:" $MME_VM_NAME "stats:" $Connected_enbs $Connected_ues $Attached_ues $Default_bearers $S1_U 

#=========================================================
# Send event to VES collector in two steps
#=========================================================
VESeventFile="VES_send_event.json"
echo "aget-wef.sh:: preparing and sending VES event"
# step 1. locally prepare a json file describing the event
./VESprepareSendEvent.py $MME_VM_NAME $Attached_ues $1
# step 2. send the event to VES using the prepared json file
if [ "$1" = "-v" ]
then
  curl -v -k -i $vesURI \
    -H 'accept: application/json' \
    -H 'cache-control: no-cache' \
    -H 'Content-type: application/json' \
    -H 'Authorization: Basic c2FtcGxlMTpzYW1wbGUx' \
    -H 'postman-token: e090a31d-b9e0-60e1-9b4d-0491005a0fe2' \
    -d @$VESeventFile
else
  curl -k -i $vesURI \
    -H 'accept: application/json' \
    -H 'cache-control: no-cache' \
    -H 'Content-type: application/json' \
    -H 'Authorization: Basic c2FtcGxlMTpzYW1wbGUx' \
    -H 'postman-token: e090a31d-b9e0-60e1-9b4d-0491005a0fe2' \
    -d @$VESeventFile
fi
echo
echo "agent-wef.sh:: VES event sent"

# for testing with POST in Python: here are links to a project for Python2/3 python HTTP server with GET and POSTS requests (Simple does not suuport POST): 
# - https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7

# wait 120 sec. for the next fetch of MME staus: (1) to allow for finishing MME VM resize procedure (it takes approx. 60 sec. altogether) and 
# (2) allow for additional guard time (60 sec.) to let MME stabilize its state on WEF cluster level
sleep 127

done
