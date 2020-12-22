#!/bin/bash

#NOTICE:
#in ONAP environment, for long-living run this script with 'nohup', and as startup script according to https://transang.me/create-startup-scripts-in-ubuntu/ 
#the best option is to prepare VM image with all these settings  present
#while logged in on the machine, trace current logs of the script using:
#tail -f nohup.out 
#if needed, one can clear nohup.out by: cat /dev/null > nohup.out

URI="http://10.254.184.197:8888"
#URI=$"real VES uri here"
#a better form of VES URI: http://localhost:8080/eventListener/v5 -k

echo ""
echo "Use parameter -v for a more detailed  output."
echo ""

while true
do

echo "xxxxxxxx"

#fetch recent stats from MME
if [ "$1" = "-v" ]
then 
  curl -v  http://10.254.184.197:8888/mme-clamp.log --output mme-clamp.log
else
  curl     http://10.254.184.197:8888/mme-clamp.log --output mme-clamp.log
fi

#extract stats' values from thwe fetched log file
MME_VM_NAME=$(grep -oP "MME_VM_NAME\K.*" ./mme-clamp.log)
Connected_enbs=$(grep -oP "Connected_eNBs\K.*" ./mme-clamp.log)
Connected_ues=$(grep -oP "Connected_UEs\K.*" ./mme-clamp.log)
Attached_ues=$(grep -oP "Attached_UEs\K.*" ./mme-clamp.log)
Default_bearers=$(grep -oP "Default_Bearers\K.*" ./mme-clamp.log)
S1_U=$(grep -oP "S1-U_Bearers\K.*" ./mme-clamp.log)
#oryginal: S1_U=$(grep -oP "S1-U_Bearers\K.*" ./mme-clamp.log | tail -1 | awk '{print "S1-U_Bearers", $2}')

echo "MME name:" $MME_VM_NAME "stats:" $Connected_enbs $Connected_ues $Attached_ues $Default_bearers $S1_U 

#Send event to VES collector in two steps
#=======================================

#step 1. prepare a json file describing the event
./VESprepareSendEvent.py $MME_VM_NAME $Attached_ues $1

#step 2. send the event from prepared json file to VES

if [ "$1" = "-v" ]
then
  curl -i  -X POST -d @VES_send_event.json --header "Content-Type: application/json" $URI 
else
  curl -s -o -i  -X POST -d @VES_send_event.json --header "Content-Type: application/json" $URI  
fi
echo "VES event sent"
#for testing with POST in Python: here are links to a project for Python2/3 python HTTP server with GET and POSTS requests (Simple does not suuport POST): 
#  https://gist.github.com/mdonkers/63e115cc0c79b4f6b8b3a6b797e485c7

sleep 120

done
