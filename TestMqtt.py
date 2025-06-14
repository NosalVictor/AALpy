import socket
from scapy.compat import raw
from scapy.contrib.mqtt import MQTT, MQTTConnect, MQTTDisconnect

host = 'localhost'
port = 1883
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (host, port)
sock.connect(server_address)

mqtt_connect = MQTT()
mqtt_connect.add_payload(MQTTConnect(clientId='c0', protolevel=4, protoname='MQTT'))
sock.sendall(raw(mqtt_connect))
print("Sent connect packet")
data = sock.recv(4)
print(f"CONNACK reçu (hex): {data.hex()}")

mqtt_disconnect = MQTT()
mqtt_disconnect.add_payload(MQTTDisconnect())
sock.sendall(raw(mqtt_disconnect))
print("Sent disconnect packet")

sock.close()
