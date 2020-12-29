#!/bin/bash
vesURI='https://10.254.184.250:30417/eventListener/v5'
#vesURI='https://portal.api.simpledemo.onap.org:30417/eventListener/v5'
file="$1"
#curl -v -i -d @$file --header "Content-Type: application/json" $vesURI
curl -v -k -i $vesURI \
  -H 'accept: application/json' \
  -H 'cache-control: no-cache' \
  -H 'Content-type: application/json' \
  -H 'Authorization: Basic c2FtcGxlMTpzYW1wbGUx' \
  -H 'postman-token: e090a31d-b9e0-60e1-9b4d-0491005a0fe2' \
  -d @$file
