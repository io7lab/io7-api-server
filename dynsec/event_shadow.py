import json
from concurrent.futures import ThreadPoolExecutor
import redis
import requests
import time
import logging
from environments import Settings, get_config

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

executor = ThreadPoolExecutor(max_workers=30)
redisClient = redis.Redis(
    host=getattr(settings, 'REDIS_HOST', 'redis'),
    port=getattr(settings, 'REDIS_PORT', 6379), db=0)

influxdb_host=getattr(settings, 'INFLUXDB_HOST', 'influxdb')
influxdb_port=getattr(settings, 'INFLUXDB_PORT', 8086)
influxdb_url = f'http://{influxdb_host}:{influxdb_port}/write?db=bucket01'
influxdb_token=get_config('influxdb_token')
influxdb_header = {"Authorization": f"Token {influxdb_token}"}
# TODO:
# http/https
# bucket info
# header
# dataselection

def isNumber(n):
    try:
        float(n)
        return True
    except:
        return False

def shadow_event_thread(device, msg):
    msg_json = json.loads(msg.payload)
    msg_json['t'] = int(time.time())
    redisClient.set(device, json.dumps(msg_json))
    data=f"alldevices,device={device} "
    if 'd' in msg_json:
        if 'temperature' in msg_json['d'] and isNumber(msg_json['d']['temperature']):
            data += f"temperature={msg_json['d']['temperature']}"
        if 'humidity' in msg_json['d'] and isNumber(msg_json['d']['humidity']):
            data += f",humidity={msg_json['d']['humidity']}"

    rc= requests.post(url=influxdb_url, data=data, headers=influxdb_header)
    #logger.debug(f"Shadowing and Logging : {device} => {json.dumps(msg_json)}")

def shadow_event(device, msg):
    executor.submit(shadow_event_thread, device, msg)