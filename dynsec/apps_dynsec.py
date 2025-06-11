import json
import logging
from typing import List
from models import NewIOTApp, MemberDevice
from dynsec.mqtt_conn import mqClient
from dynsec.topicBase import ACLBase
from environments import Settings, dynsec_get_client_role

settings = Settings()
logger = logging.getLogger("uvicorn")
logger.setLevel(settings.LOG_LEVEL)

def add_dynsec_app(app: NewIOTApp):
    # TODO: ensure $apps role exists
    rolename = '$apps'
    if app.restricted:
        rolename = f"$apps_{app.appId}"
        acl = ACLBase(rolename)
        dyn_cmd = {
            'commands': [
                {
                    'command': 'createRole',
                    'rolename': acl.get_id(),
                    'acls': [ ]
                }
            ]
        }
        mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(dyn_cmd));

    dyn_cmd = {
        'commands': [
            {
                'command': 'createClient',
                'username': app.appId,
                'password': app.password,
                'roles': [
                    {
                        'rolename': rolename,
                        'priority': -1
                    }
                ]
            }
        ]
    }

    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(dyn_cmd))
    logger.info(f'Creating App ID "{app.appId}".')

def delete_dynsec_app(appId: str):
    dyn_cmd = {
        'commands': [
            {
                'command': 'deleteClient',
                'username': appId
            }
        ]
    }
    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(dyn_cmd))
    logger.info(f'Deleting App ID "{appId}".')

def build_add_cmd(appId: str, devId: str, evt: bool, cmd: bool):
    return [
        {
            "command": "addRoleACL",
            "rolename": f"$apps_{appId}",
            "acltype": "subscribePattern",
            "topic": f"iot3/{devId}/evt/#",
            "priority": -1,
            "allow": evt
        },
        {
            "command": "addRoleACL",
            "rolename": f"$apps_{appId}",
            "acltype": "publishClientSend",
            "topic": f"iot3/{devId}/cmd/#",
            "priority": -1,
            "allow": cmd
        }
    ]

def build_del_cmd(appId: str, devId: str):
    return [
        {
            "command": "removeRoleACL",
            "rolename": f"$apps_{appId}",
            "acltype": "subscribePattern",
            "topic": f"iot3/{devId}/evt/#"
        },
        {
            "command": "removeRoleACL",
            "rolename": f"$apps_{appId}",
            "acltype": "publishClientSend",
            "topic": f"iot3/{devId}/cmd/#"
        }
    ]

def add_dynsec_member(appId: str, members: List[MemberDevice]):
    commands = []
    for d in members:
        commands += build_add_cmd(appId, d.devId, d.evt, d.cmd)

    dyn_cmd = {
        "commands": commands
    }

    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(dyn_cmd))
    logger.info(f'Adding members({members}) to App ID "{appId}".')

def remove_dynsec_member(appId: str, members: list):
    commands = []
    for d in members:
        commands += build_del_cmd(appId, d)

    dyn_cmd = {
        "commands": commands
    }

    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(dyn_cmd))
    logger.info(f'Removing members({members}) to App ID "{appId}".')

def update_dynsec_members(appId: str, members: List[MemberDevice]):
    add_list = []
    del_list = []

    current = dynsec_get_client_role(appId).get('members')
    for cur in current:
        keep = next((m for m in members if m.devId == cur.get('devId')), None)
        if keep:
            if keep != cur:
                del_list.append(cur.get('devId'))
                add_list.append(keep)
        else:
            del_list.append(cur.get('devId'))
    for m in members:
        if next((c for c in current if c['devId'] == m.devId), None) is None:
            add_list.append(m)

    if len(del_list) > 0:
        remove_dynsec_member(appId, del_list)

    if len(add_list) > 0:
        add_dynsec_member(appId, add_list)

    logger.info(f'Updateing member devices for App ID({appId}). Removed : {del_list}, Added : {add_list}')