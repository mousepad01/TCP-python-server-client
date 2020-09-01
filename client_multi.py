import socket


HEADER_LENGTH = 10
SERVER_IP = socket.gethostname()
SERVER_PORT = 5000


def receive(client_socket):

    message_header = client_socket.recv(HEADER_LENGTH)

    if message_header:

        message_length = int(message_header.decode('utf-8'))
        message = client_socket.recv(message_length)
        message = message.decode('utf-8')

        return message
    else:
        return False


def send_msg(client_socket, msg):

    client_socket.send(f'{len(msg):<{HEADER_LENGTH}}'.encode('utf-8') + msg.encode('utf-8'))


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))