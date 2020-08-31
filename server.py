import socket
import pickle
import select


HEADER_LENGTH = 10
SERVER_IP = socket.gethostname()
SERVER_PORT = 5000


def receive_message(client_socket):

    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not message_header:
            return False

        message_length = int(message_header.decode('utf-8'))
        if message_length < 1 or message_length > 1024:
            return False

        return {"header": message_header, "data": client_socket.recv(message_length)}

    except:
        return False


def user_auth(client_socket, client_address):

    # authentication information is sent currently UNENCRYPTED under following format (after utf-8 decoding):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not message_header:
            return False

        message_length = int(message_header.decode('utf-8'))
        if message_length < 1 or message_length > 1024:
            return False

        auth_data = client_socket.recv(message_length)
        auth_data = pickle.loads(auth_data)

        return auth_data

    except:
        print(f"client error in authentication process from ip {client_address[0]}, port {client_address[1]}")
        return False


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()

# clients information

clients_auth_data = {'admin01': 'testadmin', 'admin02': 'testadmin2'}  # clients authentication data, permanent and unchanging

socket_list = [server_socket]  # online sockets
socket_addresses = {}  # online sockets corresponding to addresses (ip, port)
clients_online = {}  # online sockets corresponding to usernames

while True:

    readable_sockets, writable_sockets, exception_sockets = select.select(socket_list, [], [])

    for current_socket in readable_sockets:

        if current_socket == server_socket:

            client_socket, client_address = server_socket.accept()

            new_user = user_auth(client_socket, client_address)
            if new_user is not False:

                if new_user['username'] in clients_auth_data.keys() and clients_auth_data[new_user['username']] == new_user['password']:

                    socket_list.append(client_socket)
                    clients_online[client_socket] = new_user['username']
                    socket_addresses[client_socket] = client_address

                    client_socket.send(bytes("T", 'utf-8'))

                    print(f'connection established from ip {client_address[0]}, port {client_address[1]} as user {new_user["username"]}')
                else:
                    client_socket.send(bytes("F", 'utf-8'))

                    print(f'connection refused from ip {client_address[0]}, port {client_address[1]}; invalid auth data for user {new_user["username"]}')

        else:
            message = receive_message(current_socket)

            if message is False:

                print(f'connection with username {clients_online[current_socket]}, ip {socket_addresses[current_socket][0]}, port {socket_addresses[current_socket][1]} has been closed')

                socket_list.remove(current_socket)
                clients_online.pop(current_socket)
                socket_addresses.pop(current_socket)

            else:

                for socket_to_send in socket_list:
                    if socket_to_send != server_socket and socket_to_send != current_socket:

                        to_send = bytes(clients_online[current_socket], 'utf-8')
                        to_send = bytes(f"{len(to_send):<{HEADER_LENGTH}}", 'utf-8') + to_send

                        to_send += message['header'] + message['data']

                        socket_to_send.send(to_send)

                print(f'message from user {clients_online[current_socket]}: {message["data"].decode("utf-8")}')




