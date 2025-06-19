#!/usr/bin/env bash
# initiating the firmware upgradeo
#
#   you need a Web server and put the firmware on it to test the OTA firmware updgrade, 
#   for example, you put the firmware under some folder, cd to that floder and run this
#       python -m http.server
#
pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
set -x
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

curl -X 'PUT' 'http://localhost:2009/devices/upgrade/thermo3' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $token" \
  -d '{
  "fw_url": "http://localhost:8000/thermo.js"
}'