from environments import Database

config_db = Database('config_var')

def get_config(key : str) -> str:
    if value:= config_db.getOne(config_db.qry.key == key):
        if value['key'] == key:
            return value['value']
    return None