import json
import logging
from dynsec.topicBase import get_app_topics, get_topics, get_mgmt_topic
from dynsec.mqtt_conn import mqClient
from environments import Settings

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

def add_apps_role():
    topics = get_app_topics()
    cmd = {
        'commands': [
            {
                'command': 'createRole',
                'rolename': '$apps',
                'acls': [
                    {
                        'acltype': 'subscribePattern',
                        'topic': topics['subTopic'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'publishClientSend',
                        'topic': topics['pubTopic'],
                        'priority': -1,
                        'allow': True
                    }
                ]
            }
        ]
    }

    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd));
    logger.info('Creating App Role $apps.')
    
def add_io7_adm_role():
    topics = get_topics('+')
    topic2 = get_mgmt_topic()
    cmd = {
        'commands': [
            {
                'command': 'createRole',
                'rolename': '$io7_adm',
                'acls': [
                    {
                        'acltype': 'subscribePattern',
                        'topic': topics['gw_add'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'subscribePattern',
                        'topic': topics['gw_query'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'publishClientSend',
                        'topic': topics['gw_list'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'publishClientSend',
                        'topic': topic2['mgmtTopic'],
                        'priority': -1,
                        'allow': True
                    }
                ]
            }
        ]
    }

    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd));
    logger.info('Creating Gateway Admin Role $io7_adm.')
    
def assign_role(device: str, role: str):
    cmd = {
        "commands": [
            {
                "command": "addClientRole",
                "username": device,
                "rolename": role,
                "priority": -1
            }
        ]
    }
    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd));
    logger.info(f'Assigning Role {role} to device/app {device}.')