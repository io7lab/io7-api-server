import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with RC : " + str(rc))
    client.subscribe('#')

def on_message(client, userdata, msg):
    print(msg.topic, ' : ', msg.payload.decode('UTF-8'))

client = mqtt.Client()
client.username_pw_set('gateway1', 'gateway1')

client.connect('127.0.0.1', 1883, 60)
client.on_connect = on_connect
client.on_message = on_message

client.publish("iot3/gateway1/gateway/add", '{"d":{"devId": "client19"}}')
client.publish("iot3/gateway1/gateway/query", '{"d":{"devices": "*"}}')

