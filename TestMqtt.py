import socket
import select

from scapy.compat import raw
from scapy.contrib import mqtt

server_address = ('localhost', 1883)

def send_connect(sock, client_id):
    mqtt_connect = mqtt.MQTT()
    mqtt_connect.add_payload(mqtt.MQTTConnect(clientId=client_id, protolevel=4, protoname='MQTT', cleansess=1))
    sock.sendall(raw(mqtt_connect))
    print(client_id, "sent CONNECT")

    response = sock.recv(4)
    if response == b'':
        print("CONCLOSED received")
    elif response[0] == 0x20 and response[1] == 0x02:
        print("CONNACK received")
    else:
        print("Unexpected response :", response.hex())

def send_disconnect(sock):
    mqtt_disconnect = mqtt.MQTT()
    mqtt_disconnect.add_payload(mqtt.MQTTDisconnect())
    sock.sendall(raw(mqtt_disconnect))
    print("Sent DISCONNECT")

    ready, _, _ = select.select([sock], [], [], 0.1)
    if ready:
        response = sock.recv(20)
    else:
        response = b''

    if response == b'':
        print("CONCLOSED received")
    else:
        print("Unexpected response :", response.hex())

def send_subscribe(sock, client_id):
    mqtt_sub = mqtt.MQTT(QOS=1)
    topic = mqtt.MQTTTopicQOS(topic="test")
    mqtt_sub.add_payload(mqtt.MQTTSubscribe(msgid=1, topics=[topic]))
    sock.sendall(raw(mqtt_sub))
    print(client_id, " sent SUBSCRIBE : ", raw(mqtt_sub).hex())

    response = sock.recv(5)
    if response == b'':
        print("CONCLOSED received")
    elif response[0] == 0x90:
        print("SUBACK received")
    else:
        print("Unexpected response :", response.hex())

def send_unsubscribe(sock):
    mqtt_unsub = mqtt.MQTT(QOS=1)
    topic = mqtt.MQTTTopic(topic="test")
    mqtt_unsub.add_payload(mqtt.MQTTUnsubscribe(msgid=1, topics=[topic]))
    sock.sendall(raw(mqtt_unsub))
    print("sent UNSUBSCRIBE : ", raw(mqtt_unsub).hex())

    response = sock.recv(4)
    if response == b'':
        print("CONCLOSED received")
    elif response[0] == 0xb0:
        print("UNSUBACK received")
    else:
        print("Unexpected response :", response.hex())

def send_publish(sock):
    mqtt_pub = mqtt.MQTT(QOS=1)
    mqtt_pub.add_payload(mqtt.MQTTPublish(topic="test", msgid=1, value="Test Message"))
    sock.sendall(raw(mqtt_pub))
    print("c0 sent PUBLISH : ", raw(mqtt_pub).hex())

    response = sock.recv(4)
    if response == b'':
        print("CONCLOSED received")
    elif response[0] == 0x40:
        print("PUBACK received")
    else:
        print("Unexpected response :", response.hex())

def receive_publish(ready, sock):
    print("Ready is : ", ready)
    if ready:
        response = sock.recv(20)
        sock_port = sock.getsockname()
        if response == b'':
            print(sock_port, " : CONCLOSED received")
        elif response[0] == 0x30:
            print(sock_port, " : PUBLISH received : ", response.hex())
        else:
            print(sock_port, " : Unexpected response :", response.hex())

def reset_socket(sock):
    sock.close()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    return sock

def triple_connect(sock):
    send_connect(sock, 'c0')
    send_connect(sock, 'c0')

    sock = reset_socket(sock)

    send_connect(sock, 'c0')

def connect_disconnect_connect(sock):
    send_connect(sock, 'c0')
    send_disconnect(sock)

    sock = reset_socket(sock)

    send_connect(sock, 'c0')

def connect_subscribe_unsubscribe(sock):
    send_connect(sock, 'c0')
    send_subscribe(sock, 'c0')
    send_unsubscribe(sock)

def connect_publish(sock):
    send_connect(sock, 'c0')
    send_publish(sock)

def connect_subscribe_publish_receive(sock):
    send_connect(sock, 'c0')
    send_subscribe(sock, 'c0')
    send_publish(sock)

    ready, _, _ = select.select([sock], [], [], 0.1)
    receive_publish(ready, sock)

def multi_clients_publish_receive(sock):
    clients = ['c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9']
    sockets  = {'c0': sock}
    for client in clients[1:]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)
        sockets[client] = sock

    for client in clients:
        send_connect(sockets[client], client)

    send_subscribe(sockets['c0'], 'c0')
    send_subscribe(sockets['c1'], 'c1')
    send_publish(sockets['c0'])

    for client in clients:
        sock = sockets[client]
        ready, _, _ = select.select([sock], [], [], 0.1)
        receive_publish(ready, sock)
        if client != 'c0':
            sock.close()

def publish_first_with_other_client_sub(sock0):
    sock1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock1.connect(server_address)

    send_connect(sock0, 'c0')
    send_subscribe(sock0, 'c0')
    send_connect(sock1, 'c1')
    send_subscribe(sock1, 'c1')

    mqtt_pub = mqtt.MQTT(QOS=1)
    mqtt_pub.add_payload(mqtt.MQTTPublish(topic="test", msgid=1, value="Test Message"))
    sock0.sendall(raw(mqtt_pub))
    print("c0 sent PUBLISH")

    ready, _, _ = select.select([sock0], [], [], 0.1)
    if ready:
        data = sock0.recv(2)
        if data[0] == 0x30:
            print("PUBLISH received FIRST")
            mqtt_connect = mqtt.MQTT()
            mqtt_connect.add_payload(mqtt.MQTTConnect(clientId='c1', protolevel=4, protoname='MQTT', cleansess=1))
            sock1.sendall(raw(mqtt_connect))
            print("c1 sent CONNECT")

            response = sock1.recv(2)
            if response == b'':
                print("CONCLOSED received")
            elif response[0] == 0x30:
                return True

    sock1.close()
    return False

want_bug_search = False

if __name__ == "__main__":
    if want_bug_search:
        bug_found = False
        while not bug_found:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(server_address)
            bug_found = publish_first_with_other_client_sub(s)
            s.close()
            print("==============================================")
        print("Bug Found")
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(server_address)
        triple_connect(s)
        s.close()
