import random
import click
import json
import os
import paho.mqtt.client as mqtt
from topicBase import get_topics
import time

web_user = '$web'
web_user_password = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789$._+*@!&^') for i in range(8))

def delete_dynsec_web_user():
    cmd = {
	    'commands': [
	        {
	            'command': 'deleteRole',
	            'rolename': web_user
	        }
	    ]
    }
    client.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))

    cmd = {
        'commands': [
            {
                'command': 'deleteClient',
                'username': web_user
            }
        ]
    }
    client.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))

def on_connect(client, userdata, flags, rc):
    client.disconnect()

client = mqtt.Client()
client.on_connect = on_connect
    
# python dynsec/create_web_user.py -u ddf -P adf -h -p -cert -key
# BEGIN MAIN FUNCTION
@click.command(context_settings=dict(help_option_names=["--help"]))
@click.option("--user", "-u", prompt="Username", help="mqtt username")
@click.option("--pass", "-P", prompt="Password", help="mqtt password")
@click.option("--host", "-h", default="127.0.0.1", help="mqtt host")
@click.option("--port", "-p", default=None, help="mqtt port")
@click.option("--cert", "-c", default=None, help="mqtt cert")
def create_web_user(**kwargs):
    username = kwargs['user']
    password = kwargs['pass']
    host = kwargs['host']
    cert = kwargs['cert']
    port = kwargs['port'] or 1883 if not kwargs['cert'] else 8883

    if cert and os.path.exists(cert):
        import ssl
        client.tls_set(cert, tls_version=ssl.PROTOCOL_TLSv1_2)
        client.tls_insecure_set(True)
    
    
    client.username_pw_set(username, password)
    client.connect(host, port, 60)
    
    delete_dynsec_web_user()
    time.sleep(1)

    topics = get_topics('+')
    cmd = {
        'commands': [
            {
                'command': 'createRole',
                'rolename': '$web',
                'acls': [
                    {
                        'acltype': 'subscribePattern',
                        'topic': topics['metaTopic'],
                        'priority': -1,
                        'allow': True
                    },
                    {
                        'acltype': 'subscribePattern',
                        'topic': topics['evtTopic'],
                        'priority': -1,
                        'allow': True
                    }
                ]
            }
        ]
    }
    client.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))
    
    cmd = {
        'commands': [
            {
                'command': 'createClient',
                'username': web_user,
                'password': web_user_password,
                'roles': [
                    {
                        'rolename': web_user,
                        'priority': -1
                    }
                ]
            }
        ]
    }
    client.publish('$CONTROL/dynamic-security/v1', json.dumps(cmd))
    
    # mqtt options generation
    mqtt_options = {
        'username': web_user,
        'password': web_user_password
    }
    import io
    run_cfg = io.StringIO()
    run_cfg.write(json.dumps(mqtt_options, indent=8))
    buffer = run_cfg.getvalue()

    with open('./data/wsmqaccess.json', 'w') as f:
        f.write(buffer)

if __name__ == '__main__':
    create_web_user()