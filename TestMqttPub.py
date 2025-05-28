import random
import time
import paho.mqtt.client as mqtt_client

broker = "localhost"
port = 1883
topic = "python/mqtt"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_disconnect(client, userdata, flags, rc, properties):
        if rc == 0:
            print("Disconnected from MQTT Broker!")
        else:
            print("Failed to disconnect, return code %d\n", rc)

    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    print("Attempt 1 to connect...")
    client.user_data_set({"attempt": 1})
    client.loop_start()
    client.connect(broker, port)
    time.sleep(2)

    print("Attempt 2 to connect...")
    client.user_data_set({"attempt": 2})
    client.connect(broker, port)
    time.sleep(2)

    print("Attempt 3 to connect...")
    client.user_data_set({"attempt": 3})
    client.connect(broker, port)
    time.sleep(2)
    publish(client)
    client.disconnect()
    client.loop_stop()

    return client

def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 5:
            break

def run():
    client = connect_mqtt()
    #client.loop_start()
    #publish(client)
    #client.loop_stop()

if __name__ == '__main__':
    run()
