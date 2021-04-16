#!/usr/bin/env python

import sys, time
#import requests

#test input params
print("lensysargv= %i, argv[1]= %s" % (len(sys.argv), sys.argv[1]))
print("lensysargv= %i, argv[2]= %s" % (len(sys.argv), sys.argv[2]))
if len(sys.argv) == 4:
  print("lensysargv= %i, argv[3]= %s" % (len(sys.argv), sys.argv[3]))

print("preparing VES telemetry event")

#test requests
#response = requests.get('http://10.254.184.197:8888/clampmme.log')
#print(response.content)

fil = open("VES_send_template.json", "r")
f=fil.read()

#set lastEpochMicrosec
i = f.find('lastEpochMicrosec')
cl0= f.find(':',i)
cm0=f.find(',',cl0)
lastEpoch = int(time.time()*1000000)

#set reporting
i = f.find('reportingEntityName')
cl1= f.find(':',i)
cm1=f.find(',',cl1)

#set source
i = f.find('sourceName')
cl2= f.find(':',i)
cm2=f.find(',',cl2)

#set value receivedPackets
i = f.find('receivedTotalPacketsDelta')
cl4= f.find(':',i)
cm4=f.find(',',cl4)

#set startEpochMicrosec
i = f.find('startEpochMicrosec')
cl3= f.find(':',i)
cm3=f.find(',',cl3)
startEpoch = int(time.time()*1000000)

#set value receivedTotalPackets
i = f.find('receivedTotalPacketsDelta')
cl4= f.find(':',i)
cm4=f.find(',',cl4)

evnt = f[:cl0] + ':' + str(lastEpoch) + \
       f[cm0:cl1] + ':\"' + sys.argv[1] + '\"' + f[cm1:cl2] + ':\"' + sys.argv[1] + '\"' + \
       f[cm2:cl3] + ':' + str(startEpoch) + \
       f[cm3:cl4] + ":" + sys.argv[2] + f[cm4:]

if (len(sys.argv) == 4) and (sys.argv[3] == '-v'):
  print("VESprepareSendEvent.py:: prepared event:") 
  print(evnt)

fil.close()

fil = open("VES_send_event.json", "w+")
fil.write(evnt)
fil.close

print("VESprepareSendEvent.py:: VES send event prepared")

