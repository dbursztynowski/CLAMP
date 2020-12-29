#!/usr/bin/python

#Policy enforcement script to baypass APPC
# CLAMP modules operate  on vFW instance byt  the ....

import json
import requests
import time
import subprocess
import os

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def action_gora():
    url = 'http://10.254.185.17:8183/restconf/config/stream-count:stream-count/streams'
    payload = '{"streams": {"active-streams": 6}}'
    headers = {"Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json", "Cache-Control": "no-cache", "Postman-Token": "9005870c-900b-2e2e-0902-ef2009bb0ff7"}
    r = requests.put(url, data=payload, headers=headers)
    return r.status_code

def action_dol():
    url = 'http://10.254.185.17:8183/restconf/config/stream-count:stream-count/streams'
    payload = '{"streams": {"active-streams": 4}}'
    headers = {"Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json", "Cache-Control": "no-cache", "Postman-Token": "9005870c-900b-2e2e-0902-ef2009bb0ff7"}
    r = requests.put(url, data=payload, headers=headers)
    return r.status_code


#url = 'https://portal.api.simpledemo.onap.org:30226/events/APPC-CL/g1/c3?timeout=5000'
#url = 'https://10.254.184.250:30226/events/POLICY-CL-MGT/g1/c3?timeout=5000'
url = 'https://10.254.184.250:30226/events/APPC-CL/g1/c3?timeout=5000'
headers = {'accept': 'application/json', 'cache-control': 'no-cache', 'postman-token': '61210824-faf0-d843-218d-28337bab5d87'}

requestID = None
requestID_old = None

while True:
    time.sleep(10)

    r = requests.get(url, headers=headers, verify=False)
    event_json = r.json()
    print(event_json)
    if len(event_json) > 0:
      print()
      print("length event_json=",len(event_json))
    direction = 0
    #event_json='["{\\"CommonHeader\\":{\\"TimeStamp\\":1608547151210,\\"APIver\\":\\"1.01\\",\\"RequestID\\":\\"08dd8ebc-00ff-43c5-bfbe-ecf5cf60beec\\",\\"SubRequestID\\":\\"ab23127d-fe65-4ae0-afe6-034dd0769afb\\",\\"RequestTrack\\":[],\\"Flags\\":[]},\\"Action\\":\\"ModifyConfig\\",\\"Payload\\":{\\"streams\\":{\\"active-streams\\":6},\\"generic-vnf.vnf-id\\":\\"bd6af5c1-fc85-446d-bb59-553b0404075b\\"}}"]'

    #scan json array from the bus element by element (actually, messages from the inner list)
    validRequest = False
    for i in range(len(event_json)):

        validRequest = False

        try:
            event_dict = json.loads(event_json[i])
            print("(0) event " + str(i) + ": " + str(event_dict))
        except:
            continue
        continue

        #check if this is a request for resizing (to serve) or a confirmation message (to skip)
        value = None
        code = None

        try:
            value = event_dict["Status"]["Value"]
            code = event_dict["Status"]["Code"]
#            print("value, code "+"|"+value+"|"+code+"|")
            if value in ["ACCEPTED", "FAILURE"]:
                continue  #skip parsing, this is not a request
        except: #if no "status" or "code" field present, presumably a request - pass
            pass

        requestID_old = requestID #presumably a request, we can  store current ID as old
#        print("(1) reqIDold, event", requestID_old, str(event_dict))
        try:
            requestID = event_dict["CommonHeader"]["RequestID"]
#            print("(2) reqID, event", requestID_old, str(event_dict))
            if requestID == requestID_old:
                continue
            action = event_dict["Action"]
            vnf_id = event_dict["Payload"]["generic-vnf.vnf-id"]
            direction = event_dict["Payload"]["streams"]["active-streams"]
#            print("(3) dir, event ", direction, str(event_dict))
            validRequest = True
            break
        except:
            pass

    if not validRequest:
        continue

    if action == "ModifyConfig" and direction == 6:

        print("\ntrigger from Policy:\n" + str(event_dict))
        print ("\nAction %s, direction %s => resize up >>>>>>>>>>>>>>>>>>>>" % (action, direction))
        #r = action_gora() #this is only valid for packet generator in vFW use case
        #print ("Action response", r)

        shellCommand = "./test-resize.sh" + " " + "test-resizevm-db" + " " + "m2.large"
        print("starting: " + shellCommand)
##        proc = subprocess.Popen( ['/home/ubuntu/clamp/test-resize.sh', 'test-resizevm-db', 'm2.large'], stdout=subprocess.PIPE, shell=True)
##        proc = subprocess.call( ['/home/ubuntu/clamp/test-resize.sh', 'test-resizevm-db', 'm2.large'], shell=True)
        os.system("/bin/bash /home/ubuntu/clamp/test-resize.sh test-resizevm-db m2.large")
        print("Resize up: completed <<<<<<<<<<<<<<<<<<<<<<<<")

    if action == "ModifyConfig" and direction == 4:

        print("\ntrigger from Policy:\n" + str(event_dict))
        print ("\nAction %s, direction %s => resize down >>>>>>>>>>>>>>>>>>>>" % (action, direction))
        #r= action_dol() #this is only valid for packet generator in vFW use case
        #print ("Action response", r)

        shellCommand = "./test-resize.sh" + " " + "test-resizevm-db" + " " + "m1.large"
        print("starting: " + shellCommand) 
##        proc = subprocess.call( ['/home/ubuntu/clamp/test-resize.sh', 'test-resizevm-db', 'm2.large'], shell=True)
        os.system("/bin/bash /home/ubuntu/clamp/test-resize.sh test-resizevm-db m1.large")
        print("Rsize down: completed <<<<<<<<<<<<<<<<<<<<<<<<")

