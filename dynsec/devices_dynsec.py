import json
import logging
from models import NewDevice, Device
from dynsec.topicBase import get_topics, get_mgmt_topic, get_app_topics, get_role_name
from dynsec.mqtt_conn import mqClient
from environments import Settings

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

def add_dynsec_device(device: NewDevice):
    topics = get_topics(device.devId)
    cmd = {
        'commands': [
            {
                'command': 'createRole',
                'rolename': topics['rolename'],
                'acls': [
                    {
                        'acltype': 'subscribePattern',
                        'topic': topics['cmdTopic'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'subscribePattern',
                        'topic': topics['updateTopic'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'subscribePattern',
                        'topic': topics['rebootTopic'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'subscribePattern',
                        'topic': topics['resetTopic'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'subscribePattern',
                        'topic': topics['upgradeTopic'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'publishClientSend',
                        'topic': topics['logTopic'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'publishClientSend',
                        'topic': topics['metaTopic'],
                        'priority': -1,
                        'allow': True
                    }, {
                        'acltype': 'publishClientSend',
                        'topic': topics['evtTopic'],
                        'priority': -1,
                        'allow': True
                    }
                ]
            }
        ]
    }

    if device.type == 'gateway':
        cmd['commands'][0]['acls'].append({
            'acltype': 'publishClientSend',
            'topic': topics['gw_query'],
            'priority': -1,
            'allow': True
        })
        cmd['commands'][0]['acls'].append({
            'acltype': 'publishClientSend',
            'topic': topics['gw_add'],
            'priority': -1,
            'allow': True
        })
        cmd['commands'][0]['acls'].append({
            'acltype': 'subscribePattern',
            'topic': topics['gw_list'],
            'priority': -1,
            'allow': True
        })
    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd));

    if device.type == 'edge':
        cmd = {
            'commands': [
                {
                    'command': 'addClientRole',
                    'username': device.createdBy,
                    'rolename': device.devId
                }
            ]
        }
        logger.info(f'Creating Edge Client "{topics["id"]}".')
    else:
        cmd = {
            'commands': [
                {
                    'command': 'createClient',
                    'username': topics['id'],
                    'password': device.password,
                    'roles': [
                        {
                            'rolename': topics['rolename'],
                            'priority': -1
                        }
                    ]
                }
            ]
        }
        logger.info(f'Creating Client "{topics["id"]}".')
        
    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))

def delete_dynsec_role(role: str):
    if role in ['admin', '$web', '$apps', '$io7_adm']:
        logger.info(f'Cannot delete system role "{role}".')
        return
    cmd = {
	    'commands': [
	        {
	            'command': 'deleteRole',
	            'rolename': get_role_name(role)
	        }
	    ]
    }
    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))
    logger.info(f'Deleting Role "{role}".')

def delete_dynsec_device(device: str):
    cmd = {
        'commands': [
            {
                'command': 'deleteClient',
                'username': device
            }
        ]
    }
    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))
    logger.info(f'Deleting Device "{device}".')