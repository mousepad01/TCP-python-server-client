import socket
import select
import errno
import pickle
import queue

HEADER_SIZE = 10
SERVER_IP = socket.gethostname()
SERVER_PORT = 5000

AUTH_VALID_DATA = {}


def receive(readable_socket):

    try:

        message_header = readable_socket.recv(HEADER_SIZE)
        if message_header:
            message_length = int(message_header.decode('utf-8'))

            message_pack = readable_socket.recv(message_length)
            message_pack = pickle.loads(message_pack)

            return message_pack  # tuple of (username where it is meant to arrive, message)

        else:
            return False

    except socket.error as err:

        if err.errno == errno.WSAECONNRESET:

            input_sockets.remove(readable_socket)

            if readable_socket in output_sockets:
                output_sockets.remove(readable_socket)

            if readable_socket in message_queue.keys():
                del message_queue[readable_socket]

            online_user[sockets_username[readable_socket]] = False

            del username_sockets[sockets_username[readable_socket]]
            del sockets_username[readable_socket]

            print(f"client with address {readable_socket.getsockname()} has forcibly closed the connection")
            return False


def send_msg(writable_socket, msg_pack):

    try:
        msg_pack = pickle.dumps(msg_pack)
        writable_socket.send(f"{len(msg_pack):<{HEADER_SIZE}}".encode('utf-8') + msg_pack)

    except socket.error as err:

        if err.errno == errno.WSAECONNRESET:

            if writable_socket in input_sockets:
                input_sockets.remove(writable_socket)

            if writable_socket in output_sockets:
                output_sockets.remove(writable_socket)

            online_user[sockets_username[writable_socket]] = False

            del username_sockets[sockets_username[writable_socket]]
            del sockets_username[writable_socket]
            del message_queue[writable_socket]

            print(f"client with address {writable_socket.getsockname()} has forcibly closed the connection")


def auth_check(to_check_socket):

    try:
        auth_header = to_check_socket.recv(HEADER_SIZE)
        if auth_header:

            auth_length = int(auth_header.decode('utf-8'))
            auth_data = to_check_socket.recv(auth_length)
            auth_data = pickle.loads(auth_data)

            if auth_data['username'] in AUTH_VALID_DATA.keys() and AUTH_VALID_DATA[auth_data['username']] == auth_data['password']:
                return auth_data['username']
            else:
                return False

        else:
            return False

    except socket.error as err:

        if err.errno == errno.WSAECONNRESET:
            print(f"could not complete authentication process with client {to_check_socket.getsockname()}")
            to_check_socket.close()
            return False


# valid auth data load

online_user = {}

auth_valid_data_file = open("auth_valid_data.txt")

cnt_accounts = int(auth_valid_data_file.readline())
for i in range(cnt_accounts):

    account_str = auth_valid_data_file.readline()

    username_length = account_str[:2]
    username_length = int(username_length[0]) * 10 + int(username_length[1])
    username = account_str[3:3 + username_length]

    password = account_str[4 + username_length:]

    if i < cnt_accounts - 1:
        AUTH_VALID_DATA.update({username: password[:len(password) - 1]})
    else:
        AUTH_VALID_DATA.update({username: password})

    online_user[username] = False

# server init

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

server_socket.listen()

# sockets init

input_sockets = [server_socket]
output_sockets = []

username_sockets = {}
sockets_username = {}

message_queue = {}

while True:

    readable_sockets, writable_sockets, except_sockets = select.select(input_sockets, output_sockets, input_sockets)

    for r_s in readable_sockets:

        if r_s == server_socket:

            server_socket.settimeout(0.5)  # waiting for login credentials

            new_socket, new_address = server_socket.accept()

            username = auth_check(new_socket)
            if username is not False and online_user[username] is False:

                input_sockets.append(new_socket)

                username_sockets[username] = new_socket
                sockets_username[new_socket] = username

                online_user[username] = True

                # sending successful auth message back to the client

                output_sockets.append(new_socket)
                if new_socket not in message_queue.keys():
                    message_queue[new_socket] = queue.Queue()

                message_queue[new_socket].put(('SERVER', "successful authentication"))

                print(f"client with address {new_address} successfully authenticated with username {username}")
            else:
                print(f"client with address {new_address} failed to authenticate")

            server_socket.settimeout(0.0)

        else:

            message_pack = receive(r_s)
            if message_pack is not False:

                if message_pack[0] in AUTH_VALID_DATA.keys() and online_user[message_pack[0]] is True:

                    destination = username_sockets[message_pack[0]]
                    message = message_pack[1]

                    if destination not in message_queue.keys():
                        message_queue[destination] = queue.Queue()

                    sender = sockets_username[r_s]
                    message_queue[destination].put((sender, message))

                    if destination not in output_sockets:
                        output_sockets.append(destination)

                else:
                    # send error message to client that says the destination is incorrect

                    if r_s not in output_sockets:
                        output_sockets.append(r_s)

                    if r_s not in message_queue.keys():
                        message_queue[r_s] = queue.Queue()

                    message_queue[r_s].put(('SERVER', f"error: invalid destination username {message_pack[0]}"))

            '''else:

                if r_s in input_sockets:
                    input_sockets.remove(r_s)

                if r_s in output_sockets:
                    output_sockets.remove(r_s)
                
                del username_sockets[sockets_username[r_s]]
                del sockets_username[r_s]
                del message_queue[r_s]'''

    for w_s in writable_sockets:

        try:

            message_to_send = message_queue[w_s].get_nowait()
            send_msg(w_s, message_to_send)

        except queue.Empty:
            output_sockets.remove(w_s)

    for e_s in except_sockets:

        if e_s in input_sockets:
            input_sockets.remove(e_s)

        if e_s in output_sockets:
            output_sockets.remove(e_s)

        if e_s in message_queue.keys():
            del message_queue[e_s]

        del username_sockets[sockets_username[e_s]]
        del sockets_username[e_s]








