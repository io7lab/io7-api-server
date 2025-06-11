#!/usr/bin/env bash
# Getting all the ACLs for the appId
if [ $# -lt 1 ] ; then
    echo Please Provide the appId
    exit 1
fi

pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

detail=$([ "$2" = "True" ] && echo "True" || echo "False")
curl -X 'GET'  "http://localhost:2009/app-ids/$1/members?detail=$detail" -H 'accept: application/json' -H "Authorization: Bearer $token" | jq .
