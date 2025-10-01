from environments import Database, Settings
from models import ConfigVar

import logging
settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

config_db = Database('config_var')

# utility function for configuratin variables
def get_config(key : str) -> str:
    if value:= config_db.getOne(config_db.qry.key == key):
        if value['key'] == key:
            return value['value']
    return None

# utility functions for logging to influxdb
influxLogParams = {
    "fieldsets" :  [f.strip() for f in get_config("monitored_fieldsets").split(',')],
    "monitored" : get_config("monitored_devices")
}

def is_monitored(device: str) -> bool:
    if influxLogParams["monitored"] == "*" or device in influxLogParams["monitored"]:
        return True
    return False

def get_fieldset() -> list:
    return influxLogParams["fieldsets"]

def set_fieldset(fields: str) -> bool:
    """
    fileds is a string like 'temperature, humidity, lux, brightness'
    if there is a blank in the name like 'room temperature, humidity, lux, brightness',
    it will be ignored
    """
    try:
        fieldsets = list(set([f.strip() for f in fields.split(',') if f.strip() != '' and ' ' not in f.strip()]))
        influxLogParams["fieldsets"] = fieldsets
        config_db.insert(ConfigVar(key='monitored_fieldsets', value=', '.join(fieldsets)))
        return True
    except Exception as e:
        return False

def set_monitored(devices: str) -> bool:
    """
    devices is a string like 'thermo1, thermo2, lux1'
    if there is a blank in the name like 'thermo sensor, thermo2',
    it will be ignored
    """
    logger.debug(f"devices {devices}")
    try:
        if devices == '*':
            config_db.insert(ConfigVar(key='monitored_devices', value='*'))
            influxLogParams['monitored'] = '*'
        else:
            monitored = list(set([d.strip() for d in devices.split(',') if d.strip() != '' and ' ' not in d.strip()]))
            influxLogParams['monitored'] = monitored
            config_db.insert(ConfigVar(key='monitored_devices', value=', '.join(monitored)))
        return True
    except Exception as e:
        return False