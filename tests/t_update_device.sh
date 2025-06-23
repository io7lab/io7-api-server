#!/usr/bin/env bash
# adding io7 Devices
pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

curl -X 'PATCH' \
  'http://localhost:2009/devices/lamp1/update' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
    "type": "device",
    "devDesc": "good description !!!",
    "devMaker": "maker2",
    "devSerial": "456"
  }'
exit

curl -X 'PATCH' \
  'http://localhost:2009/devices/a/update' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
    "password":"dashboard"
  }'
