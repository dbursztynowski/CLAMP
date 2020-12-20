#!/bin/bash
z=$(ps aux)

#This script runs on MME, with SimpleHTTPServer enabled in a full version
# see the notes at the end

echo "# HELP mme_stats summary of mme statistics."
echo "# TYPE mme_stats summary"

#start HTTP server to retrieve the log with curl
nohup python -m SimpleHTTPServer 8888 &

while true
do

#Connected_enbs=$(grep -oP "Connected eNBs\K.*" /var/log/syslog | tail -1 | awk '{print "mme_stats{stat=\"Connected_eNBs\"}", $2}')
#Connected_ues=$(grep -oP "Connected UEs\K.*" /var/log/syslog | tail -1 | awk '{print "mme_stats{stat=\"Connected_UEs\"}", $2}')
#Attached_ues=$(grep -oP "Attached UEs\K.*" /var/log/syslog | tail -1 | awk '{print "mme_stats{stat=\"Attached_UEs\"}", $2}')
#Default_bearers=$(grep -oP "Default Bearers\K.*" /var/log/syslog | tail -1 | awk '{print "mme_stats{stat=\"Default_Bearers\"}", $2}')
#S1_U=$(grep -oP "S1-U Bearers\K.*" /var/log/syslog | tail -1 | awk '{print "mme_stats{stat=\"S1-U_Bearers\"}", $2}')

Connected_enbs=$(grep -oP "Connected eNBs\K.*" /var/log/syslog | tail -1 | awk '{print "Connected_eNBs", $2}')
Connected_ues=$(grep -oP "Connected UEs\K.*" /var/log/syslog | tail -1 | awk '{print "Connected_UEs", $2}')
Attached_ues=$(grep -oP "Attached UEs\K.*" /var/log/syslog | tail -1 | awk '{print "Attached_UEs", $2}')
Default_bearers=$(grep -oP "Default Bearers\K.*" /var/log/syslog | tail -1 | awk '{print "Default_Bearers", $2}')
S1_U=$(grep -oP "S1-U Bearers\K.*" /var/log/syslog | tail -1 | awk '{print "S1-U_Bearers", $2}')


MME_VM_NAME="MME_VM_NAME $HOSTNAME"
echo "echo MME_VN_NAME:" "MME_VM_NAME" "stats:" "$Connected_enbs" "$Connected_ues" "$Attached_ues" "$Default_bearers" "$S1_U"
#echo "$Connected_ues"
#echo "$Attached_ues"
#echo "$Default_bearers"
#echo "$S1_U"

cat > clampmme.log <<EOF
$MME_VM_NAME
$Connected_enbs
$Connected_ues
$Attached_ues
$Default_bearers
$S1_U
EOF

sleep 60

done

#NOTICE
#for this file to be downloable remotely using curl, run HTTP server on mme VM using, e.g.:
#python -m SimpleHTTPServer 8888
#or from ssh/command line so that the process is "long-rug", i.e., will not be killed on terminating the ssh session, use:
#nohup python -m SimpleHTTPServer 8888 &

#this process can be run long-lived with nohup as: nohup ./mme-clamp.sh.sh (with & for command line)
tail -f nohup.out

#but the best would be to additionally run it as startup script following this 
#https://transang.me/create-startup-scripts-in-ubuntu/ 
