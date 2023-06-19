from typing import List

from pydantic import BaseModel
from tinydb.queries import QueryLike
from environments import Settings
from models.devices import Device
import json

settings = Settings()
dynsec_json = settings.DynSecPath

def dynsec_role_exists(roleId: str) -> bool:
    with open(dynsec_json, 'r') as f:
        roles = json.load(f)['roles']
        for role in roles:
            if role['rolename'] == roleId:
                return True
    return False

def get_dynsec_admin() -> str:
    with open(dynsec_json, 'r') as f:
        clients = json.load(f)['clients']
        for client in clients:
            for role in client['roles']:
                if role['rolename'] == 'admin':
                    return client['username']
    return None
