import json
import logging
from dynsec.mqtt_conn import mqClient
from environments import Settings

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

def reboot_device_action(device: str):
    cmd = { }
    mqClient.publish(f'iot3/{device}/mgmt/initiate/device/reboot', json.dumps(cmd))
    logger.info(f'Rebooting the device "{device}".')

def reset_device_action(device: str):
    cmd = { }
    mqClient.publish(f'iot3/{device}/mgmt/initiate/device/factory_reset', json.dumps(cmd))
    logger.info(f'Factory Resetting the device "{device}".')

def update_metadata_action(device: str, meta: dict):
    cmd = {
        'd' : {
            'fields': [
                {
                    'field': 'metadata',
                    'value': meta['metadata']
                }
            ]
        }
    }
    mqClient.publish(f'iot3/{device}/mgmt/device/update', json.dumps(cmd))
    logger.info(f'Updating Metadata on "{device}".')

def upgrade_firmware_action(device: str, fw_url: str):
    cmd = {
        'd' : {
            'upgrade': {
                'fw_url': fw_url
            }
        }
    }
    mqClient.publish(f'iot3/{device}/mgmt/initiate/firmware/update', json.dumps(cmd))
    logger.info(f'Upgrading Firmware on "{device}".')