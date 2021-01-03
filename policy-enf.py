#!/usr/bin/python

#Policy enforcement script to baypass APPC
# CLAMP modules operate  on vFW instance byt  the ....

import json
import requests
import time
import subprocess
import os
import sys

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def action_up():
    url = 'http://10.254.185.17:8183/restconf/config/stream-count:stream-count/streams'
    payload = '{"streams": {"active-streams": 6}}'
    headers = {"Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json", "Cache-Control": "no-cache", "Postman-Token": "9005870c-900b-2e2e-0902-ef2009bb0ff7"}
    r = requests.put(url, data=payload, headers=headers)
    return r.status_code

def action_down():
    url = 'http://10.254.185.17:8183/restconf/config/stream-count:stream-count/streams'
    payload = '{"streams": {"active-streams": 4}}'
    headers = {"Authorization": "Basic YWRtaW46YWRtaW4=", "Content-Type": "application/json", "Cache-Control": "no-cache", "Postman-Token": "9005870c-900b-2e2e-0902-ef2009bb0ff7"}
    r = requests.put(url, data=payload, headers=headers)
    return r.status_code


#url = 'https://portal.api.simpledemo.onap.org:30226/events/APPC-CL/g1/c3?timeout=5000'
url = 'https://10.254.184.250:30226/events/APPC-CL/g1/c3?timeout=5000'
url1 = 'https://10.254.184.250:30226/events/unauthenticated.VES_MEASUREMENT_OUTPUT/g1/c3?timeout=5000'
url2 = 'https://10.254.184.250:30226/events/unauthenticated.DCAE_CL_OUTPUT/g1/c3?timeout=5000'
url3 = 'https://10.254.184.250:30226/events/POLICY-CL-MGT/g1/c3?timeout=5000'

headers = {'accept': 'application/json', 'cache-control': 'no-cache', 'postman-token': '61210824-faf0-d843-218d-28337bab5d87'}

requestID = None
requestID_old = None

# set diagnostic output granularity
verbose = False
vverbose = False # very verbose
vvverbose = False # extra verbose
if len(sys.argv) > 1:
    if sys.argv[1] == "vvv":
       vvverbose = True
       vverbose = True
       verbose = True
    if sys.argv[1] == "-vv":
       vverbose = True
       verbose = True
    elif sys.argv[1] == "-v":
       verbose = True

while True:
    time.sleep(10)

#==========================================
    # testing printouts for the message bus
    if verbose:
        print("\ntest Mesage bus")
        r = requests.get(url1, headers=headers, verify=False)
        x = r.json()
        if len(x) > 0:
            print("VES topic:", x[0])
            time.sleep(1)
        else:
            print("VES topic:", x)
    if vvverbose:
        r = requests.get(url2, headers=headers, verify=False)
        print("TCA topic:", r.json())
        time.sleep(1)

    if vverbose:
        r = requests.get(url3, headers=headers, verify=False)
        x = r.json()
        if len(x) > 0:
            print("POLICY MGT topic:", x[0])
        else:
            print("POLICY MGT topic:", x)
    # end message bus testing printouts
#===========================================

    r = requests.get(url, headers=headers, verify=False)

    event_json = r.json()
#    print(event_json)
    if verbose and len(event_json) > 0:
        print()
        print("APPC-CL topic length=",len(event_json))
    direction = 0
    #event_json='["{\\"CommonHeader\\":{\\"TimeStamp\\":1608547151210,\\"APIver\\":\\"1.01\\",\\"RequestID\\":\\"08dd8ebc-00ff-43c5-bfbe-ecf5cf60beec\\",\\"SubRequestID\\":\\"ab23127d-fe65-4ae0-afe6-034dd0769afb\\",\\"RequestTrack\\":[],\\"Flags\\":[]},\\"Action\\":\\"ModifyConfig\\",\\"Payload\\":{\\"streams\\":{\\"active-streams\\":6},\\"generic-vnf.vnf-id\\":\\"bd6af5c1-fc85-446d-bb59-553b0404075b\\"}}"]'

    #scan json array from the bus element by element (actually, messages from the inner list)
    validRequest = False
    for i in range(len(event_json)):

        validRequest = False

        try:
            event_dict = json.loads(event_json[i])
            if verbose:
               print("APPC-CL " + str(i) + ": " + str(event_dict))
        except:
            continue
        #continue

        #check if this is a request for resizing (to serve) or a confirmation message (to skip)
        value = None
        code = None

        try:
            value = event_dict["Status"]["Value"]
            code = event_dict["Status"]["Code"]
            if vvverbose:
                print("value, code "+"|"+value+"|"+code+"|")
            if value in ["ACCEPTED", "FAILURE"]:
                continue  #skip parsing, this is not a request
        except: #if no "status" or "code" field present, presumably a request - pass
            pass

        requestID_old = requestID #presumably a request, we can  store current ID as old
        if vvverbose:
            print("(r1) reqIDold, event", requestID_old, str(event_dict))
        try:
            requestID = event_dict["CommonHeader"]["RequestID"]
            if vvverbose:
                print("(r2) reqID, event", requestID_old, str(event_dict))
            if requestID == requestID_old:
                continue
            action = event_dict["Action"]
            vnf_id = event_dict["Payload"]["generic-vnf.vnf-id"]
            direction = event_dict["Payload"]["streams"]["active-streams"]
            if vvverbose:
                print("(r3) dir, event ", direction, str(event_dict))
            validRequest = True
            break
        except:
            pass

    if not validRequest:
        continue

    if action == "ModifyConfig" and direction == 6:

        print("\ntrigger from Policy:\n" + str(event_dict))
        print ("\nAction %s, direction %s => resize up >>>>>>>>>>>>>>>>>>>>" % (action, direction))
        #r = action_up() # this is only valid for packet generator in vFW use case
        #print ("Action response", r)

        shellCommand = "./test-resize.sh" + " " + "test-resizevm-db" + " " + "m2.large"
        print("starting: " + shellCommand)
##        proc = subprocess.Popen( ['/home/ubuntu/clamp/test-resize.sh', 'test-resizevm-db', 'm2.large'], stdout=subprocess.PIPE, shell=True)
##        proc = subprocess.call( ['/home/ubuntu/clamp/test-resize.sh', 'test-resizevm-db', 'm2.large'], shell=True)
        os.system("/bin/bash /home/ubuntu/clamp/resize.sh test-resizevm-db m2.large")
        print("Resize up: completed <<<<<<<<<<<<<<<<<<<<<<<<")

    if action == "ModifyConfig" and direction == 4:

        print("\ntrigger from Policy:\n" + str(event_dict))
        print ("\nAction %s, direction %s => resize down >>>>>>>>>>>>>>>>>>>>" % (action, direction))
        #r= action_down() # this is only valid for packet generator in vFW use case
        #print ("Action response", r)

        shellCommand = "./test-resize.sh" + " " + "test-resizevm-db" + " " + "m1.large"
        print("starting: " + shellCommand) 
##        proc = subprocess.call( ['/home/ubuntu/clamp/test-resize.sh', 'test-resizevm-db', 'm2.large'], shell=True)
        os.system("/bin/bash /home/ubuntu/clamp/resize.sh test-resizevm-db m1.large")
        print("Rsize down: completed <<<<<<<<<<<<<<<<<<<<<<<<")

