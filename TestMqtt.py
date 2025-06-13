import threading
import time
import logging
import paho.mqtt.client as mqtt_client

broker = "localhost"
port = 1883
topic = "python/mqtt"

connect_event_list = {}
disconnect_event_list = {}
logging.basicConfig(level=logging.DEBUG)

#def on_message(client, userdata, msg):
#    print("Received : ", msg.payload.decode())

#def on_connect_fail(client, userdata, flags, rc, properties):
#    print("Connection failed")

#def on_subscribe(client, userdata, mid, reason_code_list, properties):
#    print("Subscribed : ", client._client_id.decode())
#    subscribe_event.set()

def on_connect(client, userdata, flags, rc, properties):
    print("SET UP : ", client._client_id.decode())
    disconnect_event_list[client._client_id.decode()].clear()
    connect_event_list[client._client_id.decode()].set()
    connect_event_list[client._client_id.decode()].clear()

def on_disconnect(client, userdata, mid, reason_code_list, properties):
    if not disconnect_event_list[client._client_id.decode()].is_set():
        disconnect_event_list[client._client_id.decode()].set()
        print("DISCO SET UP : ", client._client_id.decode())
    else:
        print("DISCO ALREADY SET : ", client._client_id.decode())

def make_client(client_id):
    client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
    client.enable_logger()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    return client

def run():
    clients = ['c0', 'c1']
    client_list = {}
    for client_id in clients:
        client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        client.enable_logger()
        client_list[client_id] = client
        connect_event_list[client_id] = threading.Event()
        disconnect_event_list[client_id] = threading.Event()
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.loop_start()

        disco_response = client.disconnect()
        client.loop_stop()
        print("Disconnect Response:", disco_response)
        no_timeout = disconnect_event_list[client_id].wait(timeout=3)
        if not no_timeout:
            print("TIMEOUT Disconnect 1 : ", client_id)

        client = mqtt_client.Client(client_id=client_id, callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
        client.enable_logger()
        client_list[client_id] = client
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.loop_start()

        client.connect(broker, port)
        no_timeout1 = connect_event_list[client_id].wait(timeout=3)
        if not no_timeout1:
            print("TIMEOUT 1 : ", client_id)

    for client_id in clients:
        client = client_list[client_id]
        client.disconnect()
        client.loop_stop()

def loop_start_pause_connect():
    client_id = 'c0'
    client = make_client(client_id)
    connect_event_list[client_id] = threading.Event()
    disconnect_event_list[client_id] = threading.Event()
    client.loop_start()

    time.sleep(2)

    client.connect(broker, port)
    no_timeout1 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout1:
        print("TIMEOUT 1 : ", client_id)

    client.disconnect()
    client.loop_stop()

def double_connect():
    client_id = 'c0'
    client = make_client(client_id)
    connect_event_list[client_id] = threading.Event()
    disconnect_event_list[client_id] = threading.Event()
    client.loop_start()

    client.connect(broker, port)
    no_timeout1 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout1:
        print("TIMEOUT 1 : ", client_id)

    client.connect(broker, port)
    no_timeout2 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout2:
        print("TIMEOUT 2 : ", client_id)

    client.disconnect()
    client.loop_stop()

def connect_disconnect_connect():
    client_id = 'c0'
    client = make_client(client_id)
    connect_event_list[client_id] = threading.Event()
    disconnect_event_list[client_id] = threading.Event()
    client.loop_start()

    client.connect(broker, port)
    no_timeout1 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout1:
        print("TIMEOUT 1 : ", client_id)

    disco_response = client.disconnect()
    print("Disconnect Response:", disco_response)
    no_timeout = disconnect_event_list[client_id].wait(timeout=3)
    if not no_timeout:
        print("TIMEOUT Disconnect 1 : ", client_id)

    client.connect(broker, port)
    no_timeout2 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout2:
        print("TIMEOUT 2 : ", client_id)

    client.disconnect()
    client.loop_stop()

def connect_disconnect_pause_connect(): # Essayer de reset loop
    client_id = 'c0'
    client = make_client(client_id)
    connect_event_list[client_id] = threading.Event()
    disconnect_event_list[client_id] = threading.Event()
    print("test code 1 : ", client.loop_start())

    client.connect(broker, port)
    no_timeout1 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout1:
        print("TIMEOUT 1 : ", client_id)

    disco_response = client.disconnect()
    print("Disconnect Response:", disco_response)
    no_timeout = disconnect_event_list[client_id].wait(timeout=3)
    if not no_timeout:
        print("TIMEOUT Disconnect 1 : ", client_id)

    time.sleep(2)

    print("test code 2 : ", client.loop_start())
    client.connect(broker, port)
    no_timeout2 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout2:
        print("TIMEOUT 2 : ", client_id)

    client.disconnect()
    client.loop_stop()

def connect_disconnect_pause_recreate_connect():
    client_id = 'c0'
    client = make_client(client_id)
    connect_event_list[client_id] = threading.Event()
    disconnect_event_list[client_id] = threading.Event()
    client.loop_start()

    client.connect(broker, port)
    no_timeout1 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout1:
        print("TIMEOUT 1 : ", client_id)

    disco_response = client.disconnect()
    print("Disconnect Response:", disco_response)
    no_timeout = disconnect_event_list[client_id].wait(timeout=3)
    if not no_timeout:
        print("TIMEOUT Disconnect 1 : ", client_id)

    time.sleep(2)
    client = make_client(client_id)
    client.loop_start()

    client.connect(broker, port)
    no_timeout2 = connect_event_list[client_id].wait(timeout=3)
    if not no_timeout2:
        print("TIMEOUT 2 : ", client_id)

    client.disconnect()
    client.loop_stop()

if __name__ == '__main__':
    connect_disconnect_connect()
