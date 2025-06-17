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
        print("CONCLOSED reçu")
    elif response[0] == 0x20 and response[1] == 0x02:
        print("CONNACK reçu")
    else:
        print("Réponse inattendue :", response.hex())

def send_disconnect(sock):
    mqtt_disconnect = mqtt.MQTT()
    mqtt_disconnect.add_payload(mqtt.MQTTDisconnect())
    sock.sendall(raw(mqtt_disconnect))
    print("Sent DISCONNECT")

    ready, _, _ = select.select([sock], [], [], 0.1)
    if ready:
        response = sock.recv(4)
    else:
        response = b''

    if response == b'':
        print("CONCLOSED reçu")
    else:
        print("Réponse inattendue :", response.hex())

def send_subscribe(sock):
    mqtt_sub = mqtt.MQTT(QOS=1)
    topic = mqtt.MQTTTopicQOS(topic="test")
    mqtt_sub.add_payload(mqtt.MQTTSubscribe(msgid=1, topics=[topic]))
    sock.sendall(raw(mqtt_sub))
    print("c0 sent SUBSCRIBE : ", raw(mqtt_sub).hex())

    response = sock.recv(5)
    if response == b'':
        print("CONCLOSED reçu")
    elif response[0] == 0x90:
        print("SUBACK reçu")
    else:
        print("Réponse inattendue :", response.hex())

def send_unsubscribe(sock):
    mqtt_unsub = mqtt.MQTT(QOS=1)
    topic = mqtt.MQTTTopic(topic="test")
    mqtt_unsub.add_payload(mqtt.MQTTUnsubscribe(msgid=1, topics=[topic]))
    sock.sendall(raw(mqtt_unsub))
    print("c0 sent UNSUBSCRIBE : ", raw(mqtt_unsub).hex())

    response = sock.recv(4)
    if response == b'':
        print("CONCLOSED reçu")
    elif response[0] == 0xb0:
        print("UNSUBACK reçu")
    else:
        print("Réponse inattendue :", response.hex())

def send_publish(sock):
    mqtt_pub = mqtt.MQTT(QOS=1)
    mqtt_pub.add_payload(mqtt.MQTTPublish(topic="test", msgid=1, value="Test Messageooooooooooooooooooooooooooooooooooo"))
    sock.sendall(raw(mqtt_pub))
    print("c0 sent PUBLISH : ", raw(mqtt_pub).hex())

    response = sock.recv(4)
    if response == b'':
        print("CONCLOSED reçu")
    elif response[0] == 0x40:
        print("PUBACK reçu")
    else:
        print("Réponse inattendue :", response.hex())

def receive_publish(ready, sock):
    if ready:
        response = sock.recv(1024)
        sock_port = sock.getsockname()
        if response == b'':
            print(sock_port, " : CONCLOSED reçu")
        elif response[0] == 0x30:
            print(sock_port, " : PUBLISH reçu : ", response.hex())
        else:
            print(sock_port, " : Réponse inattendue :", response.hex())

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
    send_subscribe(sock)
    send_unsubscribe(sock)

def connect_publish(sock):
    send_connect(sock, 'c0')
    send_publish(sock)

def connect_subscribe_publish_wait(sock):
    send_connect(sock, 'c0')
    send_subscribe(sock)
    send_publish(sock)

    ready, _, _ = select.select([sock], [], [], 1)
    if ready:
        response = sock.recv(1024)
        if response == b'':
            print("CONCLOSED reçu")
        elif response[0] == 0x30:
            print("PUBLISH reçu : ", response.hex())
        else:
            print("Réponse inattendue :", response.hex())

def multi_clients_publish_receive(sock):
    clients = ['c0', 'c1', 'c2']
    sockets  = {'c0': sock}
    for client in clients[1:]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(server_address)
        sockets[client] = sock

    for client in clients:
        send_connect(sockets[client], client)

    send_subscribe(sockets['c0'])
    send_subscribe(sockets['c1'])
    send_publish(sockets['c0'])

    for client in clients:
        sock = sockets[client]
        ready, _, _ = select.select([sock], [], [], 1)
        receive_publish(ready, sock)
        if client != 'c0':
            sock.close()

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_address)
    multi_clients_publish_receive(s)
    s.close()
