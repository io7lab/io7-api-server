from environments import Settings
import json

settings = Settings()
dynsec_file = settings.DynSecPath

def load_dynsec():
    try:
        with open(dynsec_file, "r") as file:
            dynsec_json = json.load(file)
        return dynsec_json
    except json.JSONDecodeError as e:
        with open(dynsec_file, "r") as file:
            dynsec_json = json.load(file)
        return dynsec_json

def dynsec_role_exists(roleId: str) -> bool:
    roles = load_dynsec()['roles']
    for role in roles:
        if role['rolename'] == roleId:
            return True
    return False

def dynsec_get_admin() -> str:
    clients = load_dynsec()['clients']
    for client in clients:
        for role in client['roles']:
            if role['rolename'] == 'admin':
                return client['username']
    return None

def dynsec_get_client(client_id):
    dynsec_json = load_dynsec()
    return next((c for c in dynsec_json.get("clients",[]) if c.get("username") == client_id), None)

def dynsec_get_role(role_id):
    dynsec_json = load_dynsec()
    return next((r for r in dynsec_json.get("roles",[]) if r.get("rolename") == role_id), None)

def dynsec_get_client_roleId(cliendId):
    if c_id := dynsec_get_client(cliendId):
        if role := next((r for r in c_id.get("roles",[])), None):
            return role.get('rolename', None)
    return None

def dynsec_get_client_role(clientId, detail=False):
    role_id = dynsec_get_client_roleId(clientId)
    if role_id is None:
        return None

    role = dynsec_get_role(role_id)
    acl_dict = {}
    for acl in role['acls']:
        acl_split = acl['topic'].split('/')
        if acl_dict.get(acl_split[1], None) is None:
            acl_dict[acl_split[1]] = {}
        acl_dict[acl_split[1]][acl_split[2]] = acl['allow']
    members = []
    for key, value in acl_dict.items():
        value['devId'] = key
        members.append(value)

    if (detail):
        role['members'] = members
        return role
    else:
        return {'members': members}

def dynsec_get_device(dev_id):
    if role := dynsec_get_client_roleId(dev_id) == dev_id:
        return dynsec_get_client(dev_id)
    return None

def dynsec_get_appId(app_id):
    if role := dynsec_get_client_roleId(app_id):
        if role.startswith('$apps'):
            return dynsec_get_client(app_id)
    return None

def dynsec_all_devices():
    dynsec_json = load_dynsec()
    return [c.get('username') for c in dynsec_json.get("clients",[]) if c.get("username") == c.get("roles")[0].get("rolename")]

def dynsec_all_appIds():
    dynsec_json = load_dynsec()
    return [c.get('username') for c in dynsec_json.get("clients",[]) if c.get("roles")[0].get("rolename").startswith('$apps')]