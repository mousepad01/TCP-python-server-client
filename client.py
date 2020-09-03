import socket
import errno
import pickle


HEADER_SIZE = 10
SERVER_IP = socket.gethostname()
SERVER_PORT = 5000


def receive(client_socket):

    try:

        message_header = client_socket.recv(HEADER_SIZE)
        if message_header:
            message_length = int(message_header.decode('utf-8'))

            message_pack = client_socket.recv(message_length)
            message_pack = pickle.loads(message_pack)

            return message_pack  # tuple of (username that has sent the message, message)

        else:
            return False

    except socket.error as err:

        if err.errno == errno.WSAECONNRESET:
            print(f"connection with server {(SERVER_IP, SERVER_PORT)} has been forcibly closed")
            quit()


def show_msg(message_pack):
    print(f"{message_pack[0]} > {message_pack[1]}")


def send_msg(client_socket, msg_pack):

    try:
        msg_pack = pickle.dumps(msg_pack)
        client_socket.send(f"{len(msg_pack):<{HEADER_SIZE}}".encode('utf-8') + msg_pack)

    except socket.error as err:

        if err.errno == errno.WSAECONNRESET:
            print(f"server with address {(SERVER_IP, SERVER_PORT)} has forcibly closed the connection")


# socket init

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# auth procedure

username = input("username > ")
password = input("password > ")

auth_data = pickle.dumps({'username': username, 'password': password})
auth_data = f"{len(auth_data):<{HEADER_SIZE}}".encode('utf-8') + auth_data

client_socket.connect((SERVER_IP, SERVER_PORT))
client_socket.send(auth_data)

client_socket.settimeout(1)

auth_rez = receive(client_socket)
if auth_rez:
    show_msg(auth_rez)
else:
    print(f"authentication failed")
    quit()

client_socket.settimeout(1)

# main loop after successful auth

while True:

    receiver = input("send message to : ")
    message_to_send = input("message > ")

    send_msg(client_socket, (receiver, message_to_send))

    while True:

        msg_received_pack = receive(client_socket)
        if msg_received_pack:
            show_msg(msg_received_pack)
        else:
            break






