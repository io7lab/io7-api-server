import json
import random
from dynsec.mqtt_conn import mqClient
from environments import Settings

settings = Settings()

web_user = '$web'

def web_user_password():
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789$._+*@!&^') for i in range(10))

def get_mqttws_access():
    password = web_user_password()
    cmd = {
	    'commands': [
	        {
	            'command': 'setClientPassword',
	            'username': web_user,
                'password': password
	        }
	    ]
    }
    mqClient.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd));
    return  { 
        'user' : web_user,
        'password' : password
    }
