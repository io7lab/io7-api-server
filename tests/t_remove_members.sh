#!/usr/bin/env bash
# deleting the ACLs from the appId
if [ $# -lt 2 ] ; then
    echo Please Provide the appId
    echo t_remove_members.sh app3 '["lamp3", "lamp4"]'
    exit 1
fi
pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null


curl -X 'PUT' "http://localhost:2009/app-ids/$1/removeMembers" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $token" \
  -d "$2"