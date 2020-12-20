#!/usr/bin/env python

import sys
#import requests

#test input params
#print("lensysargv= %i, argv[1]= %s" % (len(sys.argv), sys.argv[1]))
#print("lensysargv= %i, argv[2]= %s" % (len(sys.argv), sys.argv[2]))

#test requests
#response = requests.get('http://10.254.184.197:8888/clampmme.log')
#print(response.content)

f = open("VES_meas_template.json", "r").read()
#set reporting
i = f.find('reportingEntityName')
cl1= f.find(':',i)
cm1=f.find(',',cl1)

#set source
i = f.find('sourceName')
cl2= f.find(':',i)
cm2=f.find(',',cl2)

#set value
i = f.find('receivedTotalPacketsDelta')
cl3= f.find(':',i)
cm3=f.find(',',cl3)

evnt=f[:cl1] + ':\"' + sys.argv[1] + '\"' + f[cm1:cl2] + ':\"' + sys.argv[1] + '\"' + f[cm2:cl3] + ':' + str(sys.argv[2]) + f[cm3:]

print(evnt)

#format event string
#         "reportingEntityName":"vofwl01fwl-ad",
#         "sourceName":"vofwl01fwl-ad",
#         "startEpochMicrosec":1608136499825805,
#         "measurementInterval":10,
#               "receivedTotalPacketsDelta":1006.000000,


#send event string to VES
#response = requests.post('http://10.254.184.197:8888/clampmme.log')
#print(response.content)

print("VES envent sent")

