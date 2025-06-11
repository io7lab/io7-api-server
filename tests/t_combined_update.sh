#!/usr/bin/env bash
# Updating the ACLs for the appId
# It sets the members to see the update function add and delete
t_add_members.sh app3
t_remove_members.sh app3 '["lamp5", "lamp7"]'
t_update_members.sh app3
#!/usr/bin/env bash
# Updating the ACLs for the appId
if [ $# -lt 1 ] ; then
    echo Please Provide the appId
    exit 1
fi

pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

curl -X 'PUT' "http://localhost:2009/app-ids/app3/updateMembers" \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $token" \
  -d '[
    {
        "devId": "lamp1",
        "evt": "true",
        "cmd": "true"
    },
    {
        "devId": "lamp2",
        "evt": "true",
        "cmd": "true"
    },
    {
        "devId": "lamp5",
        "evt": "true",
        "cmd": "true"
    },
    {
        "devId": "sw1",
        "evt": "true",
        "cmd": "true"
    },
    {
        "devId": "lamp7",
        "evt": "true",
        "cmd": "true"
    }
  ]'
