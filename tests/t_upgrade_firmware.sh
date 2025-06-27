#!/usr/bin/env bash
# initiating the firmware upgradeo
#
#   you need a Web server and put the firmware on it to test the OTA firmware updgrade, 
#   for example, 
#       let's assume you a dummy device with id 'thermo1' running
#       cd to firmware floder and run this
#
#         python -m http.server
#
#       you run this script to test the firmware. You can initiate it from the Management Web UI too.
#
pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
set -x
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

curl -X 'PUT' 'http://localhost:2009/devices/upgrade/thermo1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $token" \
  -d '{
  "fw_url": "http://localhost:8000/thermo.js"
}'