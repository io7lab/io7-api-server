import json
import logging
from models import NewIOTApp
from dynsec.mqtt_conn import mqClient
from environments import Settings

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

def add_dynsec_app(app: NewIOTApp):
    # TODO: ensure $apps role exists
    cmd = {
        'commands': [
            {
                'command': 'createClient',
                'username': app.appId,
                'password': app.password,
                'roles': [
                    {
                        'rolename': '$apps',
                        'priority': -1
                    }
                ]
            }
        ]
    }

    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))
    logger.info(f'Creating App ID "{app.appId}".')

def delete_dynsec_app(appId: str):
    cmd = {
        'commands': [
            {
                'command': 'deleteClient',
                'username': appId
            }
        ]
    }
    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))
    logger.info(f'Deleting App ID "{appId}".')