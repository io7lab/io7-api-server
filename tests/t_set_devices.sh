#!/usr/bin/env bash
# adding io7 Devices
pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

curl -X 'POST' \
  'http://localhost:2009/config/monitored_devices' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
    "devices" : "thermo2, thermo1"
  }'
