import socket
import random
import sys
import select

from scapy.compat import raw
from scapy.contrib import mqtt
from aalpy.base import SUL

class HiveMQ_Mapper_Con_Discon(SUL):
    def __init__(self, broker='localhost', port=1883):
        super().__init__()
        self.server_address = (broker, port)

        self.clients = ['c0', 'c1', 'c2']
        self.clients_socket = {}
        self.clients_set_up = set()
        self.connected_clients_id = set()

    def get_input_alphabet(self):
        return ['connect', 'disconnect']

    def pre(self):
        pass

    def post(self):
        for client_id in self.clients_socket:
            self.clients_socket[client_id].close()
        self.clients_socket = {}
        self.clients_set_up = set()
        self.connected_clients_id = set()
        print("===============================================")

    def step(self, letter):
        client_id = random.choice(self.clients)
        if client_id not in self.clients_set_up:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(self.server_address)
            self.clients_socket[client_id] = s
            self.clients_set_up.add(client_id)
        sock = self.clients_socket[client_id]

        data= b'Error'
        suffix = ''

        if letter == 'connect':
            mqtt_connect = mqtt.MQTT()
            mqtt_connect.add_payload(mqtt.MQTTConnect(clientId=client_id, protolevel=4, protoname='MQTT'))
            sock.sendall(raw(mqtt_connect))
            data = sock.recv(4)

        elif letter == 'disconnect':
            mqtt_disconnect = mqtt.MQTT()
            mqtt_disconnect.add_payload(mqtt.MQTTDisconnect())
            sock.sendall(raw(mqtt_disconnect))

            ready, _, _ = select.select([sock], [], [], 0.1)
            if ready:
                data = sock.recv(4)
            else:
                data = b''

        output = self.return_output(data)
        if output == 'CONNACK' and client_id not in self.connected_clients_id:
            self.connected_clients_id.add(client_id)
        elif output == 'CONCLOSED':
            self.close_socket(client_id)
            if client_id in self.connected_clients_id:
                self.connected_clients_id.remove(client_id)
                if len(self.connected_clients_id) == 0:
                    suffix = '_ALL'

        print(client_id, letter, " : ", output+suffix)
        return output + suffix

    def close_socket(self, client_id):
        self.clients_socket[client_id].close()
        self.clients_socket.pop(client_id)
        self.clients_set_up.remove(client_id)

    def return_output(self, data):
        if data == b'':
            return "CONCLOSED"
        elif data[0] == 0x20 and data[1] == 0x02:
            return "CONNACK"
        else:
            return "ERROR"

class HiveMQ_Mapper_Connect(SUL):
    def __init__(self, broker='localhost', port=1883):
        super().__init__()
        self.server_address = (broker, port)

        self.clients = ['c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6']
        self.clients_socket = {}
        self.clients_set_up = set()
        self.connected_clients_id = set()

    def get_input_alphabet(self):
        return ['connect']

    def pre(self):
        pass

    def post(self):
        for client_id in self.clients_socket:
            self.clients_socket[client_id].close()
        self.clients_socket = {}
        self.clients_set_up = set()
        self.connected_clients_id = set()
        print("===============================================")

    def step(self, letter):
        client_id = random.choice(self.clients)
        if client_id not in self.clients_set_up:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(self.server_address)
            self.clients_socket[client_id] = s
            self.clients_set_up.add(client_id)
        sock = self.clients_socket[client_id]
        suffix = ''

        mqtt_connect = mqtt.MQTT()
        mqtt_connect.add_payload(mqtt.MQTTConnect(clientId=client_id, protolevel=4, protoname='MQTT'))
        sock.sendall(raw(mqtt_connect))
        data = sock.recv(4)

        output = self.return_output(data)
        if output == 'CONNACK' and client_id not in self.connected_clients_id:
            self.connected_clients_id.add(client_id)
        elif output == 'CONCLOSED':
            self.close_socket(client_id)
            if client_id in self.connected_clients_id:
                self.connected_clients_id.remove(client_id)
                if len(self.connected_clients_id) == 0:
                    suffix = '_ALL'

        print(client_id, output+suffix)
        return output + suffix

    def close_socket(self, client_id):
        self.clients_socket[client_id].close()
        self.clients_socket.pop(client_id)
        self.clients_set_up.remove(client_id)

    def return_output(self, data):
        if data == b'':
            return "CONCLOSED"
        elif data[0] == 0x20 and data[1] == 0x02:
            return "CONNACK"
        else:
            return "ERROR"

class HiveMQ_Mapper(SUL):
    def __init__(self, broker='localhost', port=1883):
        super().__init__()
        self.server_address = (broker, port)

        self.clients = ('c0', 'c1', 'c2', 'c3')
        self.clients_socket = {}
        self.clients_set_up = set()
        self.connected_clients_id = set()
        self.subscribed_clients_id = set()

    def get_input_alphabet(self):
        return ['connect', 'subscribe', 'unsubscribe', 'publish']

    def pre(self):
        pass

    def post(self):
        for client_id in self.clients_socket:
            self.clients_socket[client_id].close()
        self.clients_socket = {}
        self.clients_set_up = set()
        self.connected_clients_id = set()
        self.subscribed_clients_id = set()
        print("===============================================")

    def step(self, letter):
        client_id = random.choice(self.clients)
        if client_id not in self.clients_set_up:
            self.set_up_socket(client_id)
        sock = self.clients_socket[client_id]

        data= b'Error'
        suffix = ''

        if letter == 'publish':
            data = self.send_publish(sock)
            output, suffix = self.handle_publish(data, sock)
        else:
            if letter == 'connect':
                data = self.send_connect(sock, client_id)

            elif letter == 'subscribe':
                data = self.send_subscribe(sock)

            elif letter == 'unsubscribe':
                data = self.send_unsubscribe(sock)

            output = self.return_output(data, letter)

        if output == 'CONNACK' and client_id not in self.connected_clients_id:
            self.connected_clients_id.add(client_id)
        elif output == 'CONCLOSED':
            self.close_socket(client_id)
            if client_id in self.connected_clients_id:
                self.connected_clients_id.remove(client_id)
                if client_id in self.subscribed_clients_id:
                    self.subscribed_clients_id.remove(client_id)
                if len(self.subscribed_clients_id) == 0:
                    suffix = '_UNSUB_ALL'
            if len(self.connected_clients_id) == 0:
                suffix = '_ALL'
        elif output == 'SUBACK' and client_id not in self.subscribed_clients_id:
            self.subscribed_clients_id.add(client_id)
        elif output == 'UNSUBACK':
            if client_id in self.subscribed_clients_id:
                self.subscribed_clients_id.remove(client_id)
            if len(self.subscribed_clients_id) == 0:
                suffix = '_ALL'

        print(client_id, letter, " : ", output+suffix)
        return output + suffix

    def set_up_socket(self, client_id):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.server_address)
        self.clients_socket[client_id] = s
        self.clients_set_up.add(client_id)

    def send_connect(self, sock, client_id):
        mqtt_connect = mqtt.MQTT()
        mqtt_connect.add_payload(mqtt.MQTTConnect(clientId=client_id, protolevel=4, protoname='MQTT', cleansess=1))
        sock.sendall(raw(mqtt_connect))
        return sock.recv(4)

    def send_subscribe(self, sock):
        mqtt_sub = mqtt.MQTT(QOS=1)
        topic = mqtt.MQTTTopicQOS(topic="test")
        mqtt_sub.add_payload(mqtt.MQTTSubscribe(msgid=1, topics=[topic]))
        sock.sendall(raw(mqtt_sub))
        return sock.recv(5)

    def send_unsubscribe(self, sock):
        mqtt_unsub = mqtt.MQTT(QOS=1)
        topic = mqtt.MQTTTopic(topic="test")
        mqtt_unsub.add_payload(mqtt.MQTTUnsubscribe(msgid=1, topics=[topic]))
        sock.sendall(raw(mqtt_unsub))
        ready, _, _ = select.select([sock], [], [], 0.1)
        if ready:
            return sock.recv(4)
        else:
            return b''

    def send_publish(self, sock):
        mqtt_pub = mqtt.MQTT(QOS=1)
        mqtt_pub.add_payload(mqtt.MQTTPublish(topic="test", msgid=1, value="Test Message"))
        sock.sendall(raw(mqtt_pub))
        return sock.recv(2)

    def handle_publish(self, data, sock):
        output = "PUBACK"
        suffix = ''

        if data == b'':
            output = "CONCLOSED"

        elif data[0] == 0x40:
            sock.recv(2)
            if self.is_publish_received():
                suffix = '_PUBLISH'

        elif data[0] == 0x30:
            o = sys.stdout

            with open('publish_first.txt', 'w') as f:
                sys.stdout = f
                print("Data:", data)
                print("Data hex:", data.hex())

            sys.stdout = o

            sock.recv(data[1])
            data = sock.recv(4)
            if data != b'' and data[0] == 0x40:
                suffix = '_PUBLISH'
                self.is_publish_received() # Make sure publish of each client is read
            else:
                o = sys.stdout

                with open('error_publish_puback.txt', 'w') as f:
                    sys.stdout = f
                    print("Data:", data)
                    print("Data hex:", data.hex())

                sys.stdout = o
                output = "ERROR"

        else:
            o = sys.stdout

            with open('error_publish.txt', 'w') as f:
                sys.stdout = f
                print("Data:", data)
                print("Data hex:", data.hex())

            sys.stdout = o
            output = "ERROR"

        return output, suffix

    def is_publish_received(self):
        is_publish_received = False

        for client in self.clients:
            if client not in self.clients_set_up:
                self.set_up_socket(client)
            sock = self.clients_socket[client]
            ready, _, _ = select.select([sock], [], [], 0.1)
            if ready:
                response = sock.recv(20)
                if response != b'' and response[0] == 0x30:
                    is_publish_received = True

        return is_publish_received

    def close_socket(self, client_id):
        self.clients_socket[client_id].close()
        self.clients_socket.pop(client_id)
        self.clients_set_up.remove(client_id)

    def return_output(self, data, letter):
        if data == b'':
            return "CONCLOSED"
        elif data[0] == 0x20 and data[1] == 0x02:
            return "CONNACK"
        elif data[0] == 0x90:
            return "SUBACK"
        elif data[0] == 0xb0:
            return "UNSUBACK"
        else:
            o = sys.stdout

            with open('error.txt', 'w') as f:
                sys.stdout = f
                print("Data:", data)
                print("Data hex:", data.hex())
                print("Letter:", letter)

            sys.stdout = o
            return "ERROR"

def mqtt_real_example():
    from aalpy.oracles import RandomWalkEqOracle
    from aalpy.learning_algs import run_abstracted_ONFSM_Lstar

    sul = HiveMQ_Mapper()

    alphabet = sul.get_input_alphabet()
    eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=1000, reset_prob=0.09, reset_after_cex=True)

    abstraction_mapping = { # Needs to be consistent with the Mapper
        'CONCLOSED': 'CONCLOSED',
        'CONCLOSED_UNSUB_ALL': 'CONCLOSED',
        'CONCLOSED_ALL': 'CONCLOSED',
        'UNSUBACK': 'UNSUBACK',
        'UNSUBACK_ALL': 'UNSUBACK'
    }

    learned_onfsm = run_abstracted_ONFSM_Lstar(alphabet, sul, eq_oracle, abstraction_mapping=abstraction_mapping,
                                               n_sampling=20, print_level=3)
    learned_onfsm.visualize()

def mqtt_connect_model_single_output():
    """
    Returns:
        learned automaton
    """
    import random

    from aalpy.base import SUL
    from aalpy.oracles import RandomWalkEqOracle
    from aalpy.oracles import RandomWordEqOracle
    from aalpy.learning_algs import run_abstracted_ONFSM_Lstar
    from aalpy.SULs import AutomatonSUL
    from aalpy.utils import load_automaton_from_file

    class MqttConnectSingleOutputMapper(SUL):
        def __init__(self):
            super().__init__()

            mqtt_connect_mealy = load_automaton_from_file('mqtt_connect_model_single_output.dot',
                                                          automaton_type='mealy')
            #mqtt_connect_mealy.visualize()
            self.mqtt_connect = AutomatonSUL(mqtt_connect_mealy)
            self.connected_clients = set()

            self.clients = ('c0', 'c1', 'c2', 'c3', 'c4', 'c5') # Needs to be consistent with .dot file
            #self.clients = ('c0', 'c1', 'c2', 'c3') # Needs to be consistent with .dot file

        def get_input_alphabet(self):
            return ['connect']

        def pre(self):
            self.mqtt_connect.pre()

        def post(self):
            self.mqtt_connect.post()
            self.connected_clients = set()

        def step(self, letter):
            client = random.choice(self.clients)
            inp = client + '_' + letter
            concrete_output = self.mqtt_connect.step(inp)
            suffix = ''

            if client not in self.connected_clients:
                self.connected_clients.add(client)
            elif client in self.connected_clients:
                self.connected_clients.remove(client)

            abstract_outputs = set()
            if concrete_output[2] == '_':
                abstract_outputs.add(concrete_output[3:])
            else:
                abstract_outputs.add(concrete_output[4:])
            if abstract_outputs == {'CONCLOSED'}:
                if len(self.connected_clients) == 0:
                    suffix = '_ALL'
                return 'CONCLOSED' + suffix
            else:
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + suffix

    sul = MqttConnectSingleOutputMapper()
    alphabet = sul.get_input_alphabet()

    eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=1000, reset_prob=0.09, reset_after_cex=True)
    #eq_oracle = RandomWordEqOracle(alphabet, sul, num_walks=500, min_walk_len=6, max_walk_len=8, reset_after_cex=True)

    abstraction_mapping = {
        'CONCLOSED': 'CONCLOSED',
        'CONCLOSED_ALL': 'CONCLOSED'
    }

    learned_onfsm = run_abstracted_ONFSM_Lstar(alphabet, sul, eq_oracle, abstraction_mapping=abstraction_mapping,
                                               n_sampling=50, print_level=3)
    #learned_onfsm.visualize()

    return learned_onfsm

def mqtt_connect_model():
    """
    Returns:
        learned automaton
    """
    import random

    from aalpy.base import SUL
    from aalpy.oracles import RandomWalkEqOracle
    from aalpy.oracles import RandomWordEqOracle
    from aalpy.learning_algs import run_abstracted_ONFSM_Lstar
    from aalpy.SULs import AutomatonSUL
    from aalpy.utils import load_automaton_from_file

    class MqttConnectMapper(SUL):
        def __init__(self):
            super().__init__()

            mqtt_connect_mealy = load_automaton_from_file('mqtt_connect_model.dot',
                                                               automaton_type='mealy')
            #mqtt_connect_mealy.visualize()
            self.mqtt_connect = AutomatonSUL(mqtt_connect_mealy)
            self.connected_clients = set()

            #self.clients = ('c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8', 'c9', 'c10', 'c11', 'c12', 'c13', 'c14') # Needs to be consistent with .dot file
            self.clients = ('c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6') # Needs to be consistent with .dot file

        def get_input_alphabet(self):
            return ['connect']

        def pre(self):
            self.mqtt_connect.pre()

        def post(self):
            self.mqtt_connect.post()
            self.connected_clients = set()

        def step(self, letter):
            client = random.choice(self.clients)
            inp = client + '_' + letter
            concrete_output = self.mqtt_connect.step(inp)
            suffix = ''

            if client not in self.connected_clients:
                self.connected_clients.add(client)
            elif client in self.connected_clients:
                self.connected_clients.remove(client)

            concrete_outputs = concrete_output.split('__')
            abstract_outputs = set()
            for e in concrete_outputs:
                if e[2] == '_':
                    abstract_outputs.add(e[3:])
                else:
                    abstract_outputs.add(e[4:])
            if 'Empty' in abstract_outputs:
                abstract_outputs.remove('Empty')
            if abstract_outputs == {'CONCLOSED'}:
                if len(self.connected_clients) == 0:
                    suffix = '_ALL'
                return 'CONCLOSED' + suffix
            else:
                if 'CONCLOSED' in abstract_outputs:
                    abstract_outputs.remove('CONCLOSED')
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + suffix

    sul = MqttConnectMapper()
    alphabet = sul.get_input_alphabet()

    eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=1000, reset_prob=0.09, reset_after_cex=True)
    #eq_oracle = RandomWordEqOracle(alphabet, sul, num_walks=500, min_walk_len=6, max_walk_len=8, reset_after_cex=True)

    abstraction_mapping = {
        'CONCLOSED': 'CONCLOSED',
        'CONCLOSED_ALL': 'CONCLOSED'
    }

    import sys
    o_temp = sys.stdout
    with open('output_R.txt', 'w') as f:
        sys.stdout = f
        learned_onfsm = run_abstracted_ONFSM_Lstar(alphabet, sul, eq_oracle, abstraction_mapping=abstraction_mapping,
                                               n_sampling=50, print_level=3)
    sys.stdout = o_temp

    #learned_onfsm = run_abstracted_ONFSM_Lstar(alphabet, sul, eq_oracle, abstraction_mapping=abstraction_mapping,
    #                                           n_sampling=50, print_level=3)
    #learned_onfsm.visualize()

    return learned_onfsm

def mqtt_connect_all_model():
    """
    Returns:
        learned automaton
    """
    import random

    from aalpy.base import SUL
    from aalpy.oracles import RandomWalkEqOracle
    from aalpy.oracles import RandomWordEqOracle
    from aalpy.learning_algs import run_abstracted_ONFSM_Lstar
    from aalpy.SULs import AutomatonSUL
    from aalpy.utils import load_automaton_from_file

    class MqttConnectMapper(SUL):
        def __init__(self):
            super().__init__()

            mqtt_connect_mealy = load_automaton_from_file('mqtt_connect_model.dot',
                                                          automaton_type='mealy')
            #mqtt_connect_mealy.visualize()
            self.mqtt_connect = AutomatonSUL(mqtt_connect_mealy)
            self.connected_clients = set()

            self.clients = ('c0', 'c1', 'c2', 'c3', 'c4', 'c5', 'c6') # Needs to be consistent with .dot file
            #self.clients = ('c0', 'c1', 'c2', 'c3', 'c4', 'c5') # Needs to be consistent with .dot file

        def get_input_alphabet(self):
            return ['connect']

        def pre(self):
            self.mqtt_connect.pre()

        def post(self):
            self.mqtt_connect.post()
            self.connected_clients = set()

        def step(self, letter):
            client = random.choice(self.clients)
            inp = client + '_' + letter
            concrete_output = self.mqtt_connect.step(inp)
            suffix = ''

            if client not in self.connected_clients:
                self.connected_clients.add(client)
            elif client in self.connected_clients:
                self.connected_clients.remove(client)

            concrete_outputs = concrete_output.split('__')
            abstract_outputs = set()
            for e in concrete_outputs:
                if e[2] == '_':
                    abstract_outputs.add(e[3:])
                else:
                    abstract_outputs.add(e[4:])

            if 'Empty' in abstract_outputs:
                abstract_outputs.remove('Empty')
            if abstract_outputs == {'CONCLOSED'}:
                if len(self.connected_clients) == 0:
                    suffix = '_ALL'
                return 'CONCLOSED' + suffix
            if 'CONNACK' in abstract_outputs:
                if len(self.connected_clients) == len(self.clients):
                    suffix = '_ALL'
                return 'CONNACK' + suffix
            else:
                if 'CONCLOSED' in abstract_outputs:
                    abstract_outputs.remove('CONCLOSED')
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + suffix

    sul = MqttConnectMapper()
    alphabet = sul.get_input_alphabet()

    eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=1000, reset_prob=0.09, reset_after_cex=True)
    #eq_oracle = RandomWordEqOracle(alphabet, sul, num_walks=5000, min_walk_len=9, max_walk_len=11, reset_after_cex=True)

    abstraction_mapping = {
        'CONCLOSED': 'CONCLOSED',
        'CONCLOSED_ALL': 'CONCLOSED',
        'CONNACK': 'CONNACK',
        'CONNACK_ALL': 'CONNACK'
    }

    #import sys
    #o_temp = sys.stdout
    #with open('output_R.txt', 'w') as f:
    #    sys.stdout = f
    #    learned_onfsm = run_abstracted_ONFSM_Lstar(alphabet, sul, eq_oracle, abstraction_mapping=abstraction_mapping,
    #                                           n_sampling=50, print_level=3)
    #sys.stdout = o_temp

    learned_onfsm = run_abstracted_ONFSM_Lstar(alphabet, sul, eq_oracle, abstraction_mapping=abstraction_mapping,
                                               n_sampling=50, print_level=3)
    #learned_onfsm.visualize()
    return learned_onfsm

def not_working_onfsm_2_clients_without_dot():
    """
    :return: learned abstracted ONFSM
    """
    import random
    from aalpy.SULs import AutomatonSUL
    from aalpy.oracles import RandomWordEqOracle
    from aalpy.learning_algs import run_abstracted_ONFSM_Lstar
    from aalpy.utils import get_N_Plus_One_ONFSM
    from aalpy.base import SUL

    class N_Plus_One_Without_Dot_Mapper(SUL):
        def __init__(self):
            super().__init__()
            self.two_clients_mqtt_connect = AutomatonSUL(get_N_Plus_One_ONFSM())
            self.connected_clients = set()
            self.clients = ('c0', 'c1')

        def get_input_alphabet(self):
            return ['connect']

        def pre(self):
            self.two_clients_mqtt_connect.pre()

        def post(self):
            self.two_clients_mqtt_connect.post()
            self.connected_clients = set()

        def step(self, letter):
            client = random.choice(self.clients)
            inp = client + '_' + letter
            concrete_output = self.two_clients_mqtt_connect.step(inp)
            suffix = ''

            if letter == 'connect':
                if client not in self.connected_clients:
                    self.connected_clients.add(client)
                elif client in self.connected_clients:
                    self.connected_clients.remove(client)

            concrete_outputs = concrete_output.split('__')
            abstract_outputs = set([e[3:] for e in concrete_outputs])
            if 'Empty' in abstract_outputs:
                abstract_outputs.remove('Empty')
            if abstract_outputs == {'CONCLOSED'}:
                if len(self.connected_clients) == 0:
                    suffix = '_ALL'
                return 'CONCLOSED' + suffix
            else:
                if 'CONCLOSED' in abstract_outputs:
                    abstract_outputs.remove('CONCLOSED')
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + suffix

    sul = N_Plus_One_Without_Dot_Mapper()
    alphabet = sul.get_input_alphabet()

    eq_oracle = RandomWordEqOracle(alphabet, sul, num_walks=500, min_walk_len=4, max_walk_len=8, reset_after_cex=True)

    abstraction_mapping = {
        'CONCLOSED': 'CONCLOSED',
        'CONCLOSED_ALL': 'CONCLOSED'
    }

    learned_onfsm = run_abstracted_ONFSM_Lstar(alphabet, sul, eq_oracle=eq_oracle,
                                               abstraction_mapping=abstraction_mapping,
                                               n_sampling=50, print_level=3)
    learned_onfsm.visualize()
    return learned_onfsm

def not_working_onfsm_2_clients_with_dot():
    """
    Learning based on a .dot file model of an ONFSM with 2 clients.
    Learned automaton is not correct because of the non-deterministic SUL.
    Returns:
        learned automaton
    """
    import random

    from aalpy.base import SUL
    from aalpy.oracles import RandomWalkEqOracle
    from aalpy.learning_algs import run_abstracted_ONFSM_Lstar
    from aalpy.SULs import AutomatonSUL
    from aalpy.utils import load_automaton_from_file

    class Two_Clients_ONFSM_Mapper(SUL):
        def __init__(self):
            super().__init__()

            two_clients_mqtt_connect_onfsm = load_automaton_from_file('DotModels/test_onsfm_2_clients.dot',
                                                               automaton_type='onfsm')
            self.two_clients_mqtt_connect_sul = AutomatonSUL(two_clients_mqtt_connect_onfsm)
            self.connected_clients = set()
            self.clients = ('c0', 'c1')

        def get_input_alphabet(self):
            return ['connect']

        def pre(self):
            self.two_clients_mqtt_connect_sul.pre()

        def post(self):
            self.two_clients_mqtt_connect_sul.post()
            self.connected_clients = set()

        def step(self, letter):
            client = random.choice(self.clients)
            inp = client + '_' + letter
            concrete_output = self.two_clients_mqtt_connect_sul.step(inp)
            suffix = ''

            if letter == 'connect':
                if client not in self.connected_clients:
                    self.connected_clients.add(client)
                elif client in self.connected_clients:
                    self.connected_clients.remove(client)

            concrete_outputs = concrete_output.split('__')
            abstract_outputs = set([e[3:] for e in concrete_outputs])
            if 'Empty' in abstract_outputs:
                abstract_outputs.remove('Empty')
            if abstract_outputs == {'CONCLOSED'}:
                if len(self.connected_clients) == 0:
                    suffix = '_ALL'
                return 'CONCLOSED' + suffix
            else:
                if 'CONCLOSED' in abstract_outputs:
                    abstract_outputs.remove('CONCLOSED')
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + suffix

    sul = Two_Clients_ONFSM_Mapper()
    alphabet = sul.get_input_alphabet()

    eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=5000, reset_prob=0.09, reset_after_cex=True)

    abstraction_mapping = {
        'CONCLOSED': 'CONCLOSED',
        'CONCLOSED_ALL': 'CONCLOSED'
    }

    learned_onfsm = run_abstracted_ONFSM_Lstar(alphabet, sul, eq_oracle, abstraction_mapping=abstraction_mapping,
                                               n_sampling=200, print_level=3)
    learned_onfsm.visualize()
    return learned_onfsm

if __name__ == '__main__':
    mqtt_real_example()