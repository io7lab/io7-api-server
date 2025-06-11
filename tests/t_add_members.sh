#!/usr/bin/env bash
# adding the ACLs to the appId
if [ $# -lt 1 ] ; then
    echo Please Provide the appId
    exit 1
fi
pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

curl -X 'PUT' "http://localhost:2009/app-ids/$1/addMembers" \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "devId": "lamp2",
    "evt": "true",
    "cmd": "true"
  },
  {
    "devId": "lamp3",
    "evt": "true",
    "cmd": "true"
  },
  {
    "devId": "lamp5",
    "evt": "false",
    "cmd": "true"
  }
]'
