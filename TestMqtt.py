import socket
import select

from scapy.compat import raw
from scapy.contrib.mqtt import MQTT, MQTTConnect, MQTTDisconnect

server_address = ('localhost', 1883)

def send_connect(sock, client_id):
    mqtt_connect = MQTT()
    mqtt_connect.add_payload(MQTTConnect(clientId=client_id, protolevel=4, protoname='MQTT'))
    sock.sendall(raw(mqtt_connect))
    print(f"Sent connect packet for client {client_id}")

    response = sock.recv(4)
    if response == b'':
        print("Conclosed reçu")
    elif response[0] == 0x20 and response[1] == 0x02:
        print("Connack reçu")
    else:
        print(f"Réponse inattendue : {response.hex()}")

def send_disconnect(sock):
    mqtt_disconnect = MQTT()
    mqtt_disconnect.add_payload(MQTTDisconnect())
    sock.sendall(raw(mqtt_disconnect))
    print("Sent disconnect packet")

    response = sock.recv(4)

    if response == b'':
        print("Conclosed reçu")
    else:
        print(f"Réponse inattendue : {response.hex()}")

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

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(server_address)
    send_disconnect(s)
    s.close()
