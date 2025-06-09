import threading
import time
import paho.mqtt.client as mqtt_client

broker = "localhost"
port = 1883
topic = "python/mqtt"

subscribe_event = threading.Event()

def on_message(client, userdata, msg):
    print("Received : ", msg.payload.decode())

def on_connect(client, userdata, flags, rc, properties):
    print("Connected : ", client._client_id.decode())

def on_connect_fail(client, userdata, flags, rc, properties):
    print("Connection failed")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    print("Subscribed : ", client._client_id.decode())
    subscribe_event.set()

def run():
    client = mqtt_client.Client(client_id='c0', callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.on_connect = on_connect
    client.on_connect_fail = on_connect_fail
    client.user_data_set({"client : ": 'c0'})
    client.loop_start()
    client.connect(broker, port)
    while not client.is_connected():
        print("waiting for connect")
        time.sleep(0.1)

    client.subscribe(topic)
    subscribe_event.wait(timeout=5)
    pub_response = client.publish(topic, "Hello")
    while not pub_response.is_published():
        print("waiting for publish")
        time.sleep(0.1)

    client.disconnect()
    client.loop_stop()

if __name__ == '__main__':
    run()
