#!/usr/bin/python
import json
import requests
import time
import subprocess

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


url = 'https://portal.api.simpledemo.onap.org:30226/events/APPC-CL/g1/c3?timeout=5000'
headers = {'accept': 'application/json', 'cache-control': 'no-cache', 'postman-token': '61210824-faf0-d843-218d-28337bab5d87'}

requestID = None
requestID_old = None

while True:
    time.sleep(5)
    r = requests.get(url, headers=headers, verify=False)
    event_json = r.json()
    print(event_json)

    direction = 0
    #event_json='["{\\"CommonHeader\\":{\\"TimeStamp\\":1608547151210,\\"APIver\\":\\"1.01\\",\\"RequestID\\":\\"08dd8ebc-00ff-43c5-bfbe-ecf5cf60beec\\",\\"SubRequestID\\":\\"ab23127d-fe65-4ae0-afe6-034dd0769afb\\",\\"RequestTrack\\":[],\\"Flags\\":[]},\\"Action\\":\\"ModifyConfig\\",\\"Payload\\":{\\"streams\\":{\\"active-streams\\":6},\\"generic-vnf.vnf-id\\":\\"bd6af5c1-fc85-446d-bb59-553b0404075b\\"}}"]'

    try:
        event_dict = json.loads(event_json[0])
    except:
        continue
        requestID_old = requestID

    try:
        requestID = event_dict["CommonHeader"]["RequestID"]
        
        if requestID == requestID_old:
            continue
                
        action = event_dict["Action"]
        vnf_id = event_dict["Payload"]["generic-vnf.vnf-id"]
        direction = event_dict["Payload"]["streams"]["active-streams"]

    except:
        None

    if direction == 6:
        
        print ("Action gora", direction)
        r = action_gora()
        print ("Action gora response", r)
    
        subprocess.Popen("resize2m2.sh", stdout=subprocess.PIPE, shell=True)
    
    if direction == 4:
        
        print ("Action dol", direction)
        r= action_dol()
        print ("Action dol response", r)

        subprocess.Popen("resize2m1.sh", stdout=subprocess.PIPE, shell=True)
    
