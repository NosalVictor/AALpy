import time

import paho.mqtt.client as mqtt_client
import random
from aalpy.base import SUL

class HiveMQ_Mapper_Con_Discon(SUL):
    def __init__(self, broker='localhost', port=1883):
        super().__init__()
        self.clients = ['c0', 'c1']
        self.broker = broker
        self.port = port

        self.client_list = {}
        self.connected_clients_id = set()

    def get_input_alphabet(self):
        return ['connect', 'disconnect']

    def pre(self):
        for client_id in self.clients:
            client = mqtt_client.Client(client_id=client_id, reconnect_on_failure=False,
                                        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
            client.loop_start()
            self.client_list[client_id] = client

    def post(self):
        for client in self.client_list.values():
            client.disconnect(self.broker, self.port)
            client.loop_stop()
        self.client_list = {}
        self.connected_clients_id = set()

    #def on_connect(self, client, userdata, flags, rc):


    def step(self, letter):
        client_id = random.choice(self.clients)
        client = self.client_list[client_id]
        output = 'Letter Error'
        all_out = ''

        if letter == 'connect':
            response = client.connect(self.broker, self.port)
            if client_id not in self.connected_clients_id:
                self.connected_clients_id.add(client_id)
            output = self.return_output(response, True)
            print("client", client_id, "connected, output: ", output)

        elif letter == 'disconnect':
            response = client.disconnect(self.broker, self.port)
            if client_id in self.connected_clients_id:
                self.connected_clients_id.remove(client_id)
            output = self.return_output(response, False)

            if output == 'CONCLOSED' and len(self.connected_clients_id) == 0:
                all_out = '_ALL'
            print("client", client_id, "disconnected, output: ", output+all_out)

        return output + all_out

    def return_output(self, code, is_connect):
        if code == 0:
            if is_connect:
                return 'CONNACK'
            else:
                return 'CONCLOSED'
        else:
            return 'ERROR'

class HiveMQ_Mapper(SUL):
    import socket
    socket.setdefaulttimeout(5)

    def __init__(self, broker='localhost', port=1883):
        super().__init__()
        self.clients = ['c0', 'c1']
        self.broker = broker
        self.port = port

        self.client_list = {}
        self.connected_clients_id = set()
        self.subscribed_clients_id = set()

    def get_input_alphabet(self):
        return ['connect', 'disconnect', 'subscribe', 'unsubscribe', 'publish']

    def pre(self):
        for client_id in self.clients:
            client = mqtt_client.Client(client_id=client_id, reconnect_on_failure=False,
                                        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2)
            client.loop_start()
            self.client_list[client_id] = client

    def post(self):
        for client in self.client_list.values():
            client.disconnect()
            client.loop_stop()
        self.client_list = {}
        self.connected_clients_id = set()
        self.subscribed_clients_id = set()
        time.sleep(0.01)

    def step(self, letter):
        client_id = random.choice(self.clients)
        client = self.client_list[client_id]
        topic = "python/mqtt"
        output = 'Letter Error'
        all_out = ''

        if letter == 'connect':
            response = client.connect(self.broker, self.port)
            if client_id not in self.connected_clients_id:
                self.connected_clients_id.add(client_id)
            output = self.return_output(response, "connect")
            #print("client", client_id, "connected, output: ", output)

        elif letter == 'disconnect':
            response = client.disconnect()
            if client_id in self.connected_clients_id:
                self.connected_clients_id.remove(client_id)
                if client_id in self.subscribed_clients_id:
                    self.subscribed_clients_id.remove(client_id)
                    if len(self.subscribed_clients_id) == 0:
                        all_out = '_UNSUB_ALL'
            output = self.return_output(response, "disconnect")

            if output == 'CONCLOSED' and len(self.connected_clients_id) == 0:
                all_out = '_ALL'
            #print("client", client_id, "disconnected, output: ", output+all_out)

        elif letter == 'subscribe':
            response = client.subscribe(topic)
            if client_id in self.connected_clients_id and client_id not in self.subscribed_clients_id:
                self.subscribed_clients_id.add(client_id)
            output = self.return_output(response[0], "subscribe")
            print("client", client_id, "subscribed, output: ", output)

        elif letter == 'unsubscribe':
            response = client.unsubscribe(topic)
            if client_id in self.subscribed_clients_id:
                self.subscribed_clients_id.remove(client_id)
            output = self.return_output(response[0], "unsubscribe")

            if output == 'UNSUBACK' and len(self.subscribed_clients_id) == 0:
                all_out = '_ALL'
            print("client", client_id, "unsubscribed, output: ", output)

        elif letter == 'publish':
            response = client.publish(topic, "Test message")
            output = self.return_output(response.rc, "publish")
            print("client", client_id, "published, output: ", output)
            time.sleep(0.05)

        return output + all_out

    def return_output(self, code, input):
        if code == 0:
            if input == "connect":
                return 'CONNACK'
            elif input == "disconnect":
                return 'CONCLOSED'
            elif input == "subscribe":
                return 'SUBACK'
            elif input == "unsubscribe":
                return 'UNSUBACK'
            elif input == "publish":
                return 'PUBACK'
            else:
                return 'ERROR'
        else:
            return 'ERROR'

def mqtt_real_example():
    from aalpy.oracles import RandomWalkEqOracle
    from aalpy.learning_algs import run_abstracted_ONFSM_Lstar

    sul = HiveMQ_Mapper()

    alphabet = sul.get_input_alphabet()
    eq_oracle = RandomWalkEqOracle(alphabet, sul, num_steps=1000, reset_prob=0.09, reset_after_cex=True)

    abstraction_mapping = { # Needs to be consistent with the Mapper
        'CONCLOSED': 'CONCLOSED',
        'CONCLOSED_ALL': 'CONCLOSED',
        'CONCLOSED_UNSUB_ALL': 'CONCLOSED',
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
            all_out = ''

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
                    all_out = '_ALL'
                return 'CONCLOSED' + all_out
            else:
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + all_out

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
            all_out = ''

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
                    all_out = '_ALL'
                return 'CONCLOSED' + all_out
            else:
                if 'CONCLOSED' in abstract_outputs:
                    abstract_outputs.remove('CONCLOSED')
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + all_out

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
            all_out = ''

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
                    all_out = '_ALL'
                return 'CONCLOSED' + all_out
            if 'CONNACK' in abstract_outputs:
                if len(self.connected_clients) == len(self.clients):
                    all_out = '_ALL'
                return 'CONNACK' + all_out
            else:
                if 'CONCLOSED' in abstract_outputs:
                    abstract_outputs.remove('CONCLOSED')
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + all_out

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
            all_out = ''

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
                    all_out = '_ALL'
                return 'CONCLOSED' + all_out
            else:
                if 'CONCLOSED' in abstract_outputs:
                    abstract_outputs.remove('CONCLOSED')
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + all_out

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
            all_out = ''

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
                    all_out = '_ALL'
                return 'CONCLOSED' + all_out
            else:
                if 'CONCLOSED' in abstract_outputs:
                    abstract_outputs.remove('CONCLOSED')
                abstract_outputs = sorted(list(abstract_outputs))
                output = '_'.join(abstract_outputs)
                return '_'.join(set(output.split('_'))) + all_out

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

mqtt_real_example()