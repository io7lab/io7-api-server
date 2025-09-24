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
    "fieldsets" : None,
    "monitored" : None
}

def is_monitored(device: str) -> bool:
    if influxLogParams["monitored"] is None:
        devices = get_config("monitored_devices") or '*'
        if type(device) is str and devices == '*':
            config_db.insert(ConfigVar(key="monitored_devices", value=devices))
            influxLogParams["monitored"] = '*'
        else:
            influxLogParams["monitored"] = [item.strip() for item in devices.split(',')]
    if influxLogParams["monitored"] == "*" or device in influxLogParams["monitored"]:
        return True
    return False

def get_fieldset() -> list:
    if influxLogParams["fieldsets"] is None:
        fields = get_config("monitored_fieldsets")
        if fields is None:
            fields = 'temperature, humidity, lux, brightness'
            config_db.insert(ConfigVar(key="monitored_fieldsets", value=fields))
        influxLogParams['fieldsets'] = [f.strip() for f in fields.split(',') if ' ' not in f.strip()]
    return influxLogParams["fieldsets"]

def set_fieldset(fields: str) -> bool:
    """
    fileds is a string like 'temperature, humidity, lux, brightness'
    if there is a blank in the name like 'room temperature, humidity, lux, brightness',
    it will be ignored
    """
    try:
        influxLogParams['fieldsets'] = [f.strip() for f in fields.split(',') if ' ' not in f.strip()]
        value=str(influxLogParams['fieldsets']).replace('[', '').replace(']', '').replace("'", '')
        config_db.insert(ConfigVar(key='monitored_fieldsets', value=value))
        return True
    except Exception as e:
        return False

def set_monitored(devices: str) -> bool:
    """
    devices is a string like 'thermo1, thermo2, lux1'
    if there is a blank in the name like 'thermo sensor, thermo2',
    it will be ignored
    """
    logger.debug(f"devices ${devices}")
    try:
        influxLogParams['monitored'] = [d.strip() for d in devices.split(',') if ' ' not in d.strip()]
        value=str(influxLogParams['monitored']).replace('[', '').replace(']', '').replace("'", '')
        config_db.insert(ConfigVar(key='monitored_devices', value=value))
        return True
    except Exception as e:
        return False