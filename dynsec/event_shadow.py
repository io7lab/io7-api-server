import json
from concurrent.futures import ThreadPoolExecutor
import redis
import requests
import time
import logging
from environments import Settings, get_config, get_fieldset, is_monitored

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

executor = ThreadPoolExecutor(max_workers=30)
redisClient = redis.Redis(
    host=getattr(settings, 'REDIS_HOST', 'redis'),
    port=getattr(settings, 'REDIS_PORT', 6379), db=0)

influxdb_host=getattr(settings, 'INFLUXDB_HOST', 'influxdb')
influxdb_port=getattr(settings, 'INFLUXDB_PORT', 8086)
influxdb_proto=getattr(settings, 'INFLUXDB_PROTOCOL', 'http')
influxdb_url = f'{influxdb_proto}://{influxdb_host}:{influxdb_port}/write?db=bucket01'
influxdb_token=get_config('influxdb_token')
influxdb_header = {"Authorization": f"Token {influxdb_token}"}
cert_verify = False if influxdb_proto == "http" else "../certs/ca.pem"

def isNumber(n):
    try:
        float(n)
        return True
    except:
        return False

def add_field_set(msg_json):
    field_set = ''
    for field in get_fieldset():
        if field in msg_json['d'] and isNumber(msg_json['d'][field]):
            field_set += ',' if len(field_set) > 0 else ''
            field_set += f"{field}={msg_json['d'][field]}"
    return field_set

def shadow_event_thread(device, msg):
    msg_json = json.loads(msg.payload)
    msg_json['t'] = int(time.time())
    redisClient.set(device, json.dumps(msg_json))

    if is_monitored(device) is False:      # retrun if the device is not listed for logging
        return

    line_data = ''
    if 'd' in msg_json:
        line_data += add_field_set(msg_json)

    if len(line_data) == 0:     # no data to log, just return
        return
    line_data=f"alldevices,device={device} " + line_data
    rc= requests.post(url=influxdb_url, data=line_data, headers=influxdb_header, verify=cert_verify)
    #logger.debug(f"Logging : {device} => {line_data}")

def shadow_event(device, msg):
    executor.submit(shadow_event_thread, device, msg)