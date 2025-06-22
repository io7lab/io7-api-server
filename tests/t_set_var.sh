#!/usr/bin/env bash
# adding io7 Devices
pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

curl -X 'PATCH' \
  'http://localhost:2009/config/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '[
  {
    "key":"dashboard", "value": "http://localhost"
  },
  {
    "key":"gf_token", "value": "gggg"
  }
]'