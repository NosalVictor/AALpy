import threading
import paho.mqtt.client as mqtt_client

broker = "localhost"
port = 1883
topic = "python/mqtt"

subscribe_event = threading.Event()
connect_event_list = {}

def on_message(client, userdata, msg):
    print("Received : ", msg.payload.decode())

def on_connect(client, userdata, flags, rc, properties):
    print("Connected : ", client._client_id.decode())
    connect_event_list[client._client_id.decode()].set()

def on_connect_fail(client, userdata, flags, rc, properties):
    print("Connection failed")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    print("Subscribed : ", client._client_id.decode())
    subscribe_event.set()

def on_disconnect(client, userdata, mid, reason_code_list, properties):
    print("Disconnected : ", client._client_id.decode())

def run():
    clients = ['c0', 'c1']
    client_list = {}
    for client_id in clients:
        client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        client_list[client_id] = client
        connect_event_list[client_id] = threading.Event()
        client.on_message = on_message
        client.on_subscribe = on_subscribe
        client.on_connect = on_connect
        client.on_connect_fail = on_connect_fail
        client.on_disconnect = on_disconnect
        client.user_data_set({"client : ": client_id})
        client.loop_start()
        client.connect(broker, port)
        print("first connect")
        connect_event_list[client_id].wait(timeout=5)
        print("First connection")
        response1 = client.disconnect()
        print("is client connected after disconnect:", client.is_connected(), "response:", response1)
        connect_event_list[client_id].clear()
        client.connect(broker, port)
        print("second connect")
        connect_event_list[client_id].wait(timeout=5)
        print("Second connection")

    #client_list['c0'].subscribe(topic)
    #subscribe_event.wait(timeout=5)
    #pub_response = client_list['c1'].publish(topic, "Hello")
    #while not pub_response.is_published():
    #    print("waiting for publish")
    #    time.sleep(0.1)

    for client_id in clients:
        client = client_list[client_id]
        client.disconnect()
        client.loop_stop()

if __name__ == '__main__':
    run()
