import json
import logging
from dynsec.topicBase import ACLBase, get_topics, get_mgmt_topic
from dynsec.mqtt_conn import mqClient
from environments import Settings

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

acl = ACLBase('+')

def add_apps_role():
    #topics = get_app_topics()
    cmd = {
        'commands': [
            {
                'command': 'createRole',
                'rolename': '$apps',
                'acls': [
                    acl.subTopic('appSubTopic'),
                    acl.pubTopic('appPubTopic')
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
                    acl.subTopic('gw_add'),
                    acl.subTopic('gw_query'),
                    acl.pubTopic('gw_list'),
                    acl.pubTopic('mgmtTopics')
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