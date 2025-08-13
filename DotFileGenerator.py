def get_exponent(exponent):
    result = 1
    for _ in range(int(exponent)):
        result = result * 2
    return result

def get_destination_state_id(connected_clients, nbr_clients):
    _sum = 0
    previous_client_id = 0
    for client_id in connected_clients:
        client_id += 1
        nbr_possibilities = nbr_clients - previous_client_id
        choice_nbr = client_id - previous_client_id
        denominator = get_exponent(choice_nbr - 1)
        _sum += 1
        _sum += get_exponent(nbr_possibilities) * (denominator-1) // denominator
        previous_client_id = client_id
    return _sum

def generate_connect_model(nbr_clients, generated_file='mqtt_connect_model.dot'):
    def get_output(last_connect_id, connected_clients):
        output = []
        for id in range(nbr_clients):
            if id in connected_clients:
                if id == last_connect_id:
                    output.append(f'c{id}_CONNACK')
                else:
                    output.append(f'c{id}_Empty')
            else:
                output.append(f'c{id}_CONCLOSED')
        return '__'.join(output)

    nbr_states = get_exponent(nbr_clients)
    states = [[]] * nbr_states
    transitions = []

    for state_id in range(nbr_states):
        for client_id in range(nbr_clients):
            was_client_already_connected = 0
            previous_index_in_sorted_list = -1
            destination_connected_clients = states[state_id].copy()
            for connected_client in range(len(states[state_id])):
                if states[state_id][connected_client] < client_id:
                    previous_index_in_sorted_list = connected_client
                if states[state_id][connected_client] == client_id:
                    destination_connected_clients.pop(connected_client)
                    was_client_already_connected = 1
            if not was_client_already_connected:
                destination_connected_clients.insert(previous_index_in_sorted_list + 1, client_id)
            destination_state_id = get_destination_state_id(destination_connected_clients, nbr_clients)
            states[destination_state_id] = destination_connected_clients
            transitions.append((state_id, destination_state_id, client_id, get_output(client_id, destination_connected_clients)))

    with open(generated_file, 'w') as f:
        f.write("digraph g {\n\n")
        for i in range(nbr_states):
            f.write(f'\ts{i} [shape="circle" label="{i}"];\n')
        f.write('\n')
        for from_id, to_id, input, output in transitions:
            f.write(f'\ts{from_id} -> s{to_id} [label="c{input}_connect / {output}"];\n')
        f.write('\n__start0 [label="" shape="none" width="0" height="0"];\n')
        f.write('__start0 -> s0;\n\n}\n')

def generate_connect_model_single_output(nbr_clients, generated_file='mqtt_connect_model_single_output.dot'):
    def get_output(last_connect_id, connected_clients):
        if last_connect_id in connected_clients:
            return f'c{last_connect_id}_CONNACK'
        else:
            return f'c{last_connect_id}_CONCLOSED'

    nbr_states = get_exponent(nbr_clients)
    states = [[]] * nbr_states
    transitions = []

    for state_id in range(nbr_states):
        for client_id in range(nbr_clients):
            was_client_already_connected = 0
            previous_index_in_sorted_list = -1
            destination_connected_clients = states[state_id].copy()
            for connected_client in range(len(states[state_id])):
                if states[state_id][connected_client] < client_id:
                    previous_index_in_sorted_list = connected_client
                if states[state_id][connected_client] == client_id:
                    destination_connected_clients.pop(connected_client)
                    was_client_already_connected = 1
            if not was_client_already_connected:
                destination_connected_clients.insert(previous_index_in_sorted_list + 1, client_id)
            destination_state_id = get_destination_state_id(destination_connected_clients, nbr_clients)
            states[destination_state_id] = destination_connected_clients
            transitions.append((state_id, destination_state_id, client_id, get_output(client_id, destination_connected_clients)))

    with open(generated_file, 'w') as f:
        f.write("digraph g {\n\n")
        for i in range(nbr_states):
            f.write(f'\ts{i} [shape="circle" label="{i}"];\n')
        f.write('\n')
        for from_id, to_id, input, output in transitions:
            f.write(f'\ts{from_id} -> s{to_id} [label="c{input}_connect / {output}"];\n')
        f.write('\n__start0 [label="" shape="none" width="0" height="0"];\n')
        f.write('__start0 -> s0;\n\n}\n')

generate_connect_model(7)
#generate_connect_model_single_output(6)
