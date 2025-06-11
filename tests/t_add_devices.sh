#!/usr/bin/env bash
# adding io7 Devices
pw=${io7pw:-strong!!!}    # it uses the environment variable io7pw, so set it to your io7 password
echo $pw
token=$(curl -X POST 'http://localhost:2009/users/login' -H 'Content-Type: application/json' -d "{ \"email\": \"io7@io7lab.com\", \"password\": \"$pw\" }"|jq '.access_token'|tr -d '"') 2>/dev/null

curl -X 'POST' 'http://localhost:2009/devices/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
  "devId": "lamp1",
  "password": "lamp1",
  "type": "device",
  "devDesc": "This is a type1 LED Lamp",
  "devMaker": "bright",
  "devSerial": "str",
  "devModel": "L1",
  "devHwVer": "str",
  "devFwVer": "str",
  "createdBy": "admin"
}'
curl -X 'POST' 'http://localhost:2009/devices/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
  "devId": "lamp2",
  "password": "lamp2",
  "type": "device",
  "devDesc": "This is a type1 LED Lamp",
  "devMaker": "bright",
  "devSerial": "str",
  "devModel": "L1",
  "devHwVer": "str",
  "devFwVer": "str",
  "createdBy": "admin"
}'
curl -X 'POST' 'http://localhost:2009/devices/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
  "devId": "lamp3",
  "password": "lamp3",
  "type": "device",
  "devDesc": "This is a type2 LED Lamp",
  "devMaker": "bright",
  "devSerial": "str",
  "devModel": "L2",
  "devHwVer": "str",
  "devFwVer": "str",
  "createdBy": "admin"
}'
curl -X 'POST' 'http://localhost:2009/devices/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
  "devId": "lamp4",
  "password": "lamp4",
  "type": "device",
  "devDesc": "This is a type3 LED Lamp",
  "devMaker": "Lux",
  "devSerial": "str",
  "devModel": "T1",
  "devHwVer": "str",
  "devFwVer": "str",
  "createdBy": "admin"
}'
curl -X 'POST' 'http://localhost:2009/devices/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
  "devId": "lamp5",
  "password": "lamp5",
  "type": "device",
  "devDesc": "This is a type3 LED Lamp",
  "devMaker": "Lux",
  "devSerial": "str",
  "devModel": "T1",
  "devHwVer": "str",
  "devFwVer": "str",
  "createdBy": "admin"
}'
curl -X 'POST' 'http://localhost:2009/devices/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
  "devId": "lamp6",
  "password": "lamp6",
  "type": "device",
  "devDesc": "This is a type 4 LED Lamp",
  "devMaker": "light",
  "devSerial": "str",
  "devModel": "B1",
  "devHwVer": "str",
  "devFwVer": "str",
  "createdBy": "admin"
}'
curl -X 'POST' 'http://localhost:2009/devices/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
  "devId": "lamp7",
  "password": "lamp7",
  "type": "device",
  "devDesc": "This is a type 5 LED Lamp",
  "devMaker": "light",
  "devSerial": "str",
  "devModel": "B2",
  "devHwVer": "str",
  "devFwVer": "str",
  "createdBy": "admin"
}'
curl -X 'POST' 'http://localhost:2009/devices/' \
  -H 'accept: application/json' \
  -H "Authorization: Bearer $token" \
  -H 'Content-Type: application/json' \
  -d '{
  "devId": "sw1",
  "password": "sw1",
  "type": "device",
  "devDesc": "This is a Switch",
  "devMaker": "light",
  "devSerial": "str",
  "devModel": "S2",
  "devHwVer": "str",
  "devFwVer": "str",
  "createdBy": "admin"
}'