import socket
import pickle
import errno

HEADER_LENGTH = 10
SERVER_IP = socket.gethostname()
SERVER_PORT = 5000


def receive(readable_socket):

    message_header = readable_socket.recv(HEADER_LENGTH)

    if message_header:

        message_length = int(message_header.decode('utf-8'))
        message = readable_socket.recv(message_length)
        message = message.decode('utf-8')

        return message
    else:
        return False


def send_msg(writable_socket, msg):

    writable_socket.send(f'{len(msg):<{HEADER_LENGTH}}'.encode('utf-8') + msg.encode('utf-8'))


def process_warnings(client_socket, warning):

    if warning == "closed":

        print(f"connection closed by the server({SERVER_IP}, {SERVER_PORT})")

    else:
        print(f"unknown warning received from a client {client_socket.getsockname()}: {warning}")


def process_request(client_socket, request):

    if request == "close":

        send_msg(client_socket, "!closed")
        client_socket.close()

        print(f'connection with ip {client_address[0]}, port {client_address[1]} has been closed as requested by the client')

    if request == "hello":

        send_msg(client_socket, "hello there!")

    else:
        print(f"unknown request received from a client {client_socket.getsockname()}: {request}")


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()

while True:

    client_socket, client_address = server_socket.accept()
    print(f'connection with ip {client_address[0]}, port {client_address[1]} established')

    if client_socket:

        try:
            while True:

                received = receive(client_socket)

                if received:

                    if received[0] == '/':
                        process_request(client_socket, received[1:])
                    elif received[0] == '!':
                        process_warnings(client_socket, received[1:])
                    else:
                        send_msg(client_socket, received)

        except socket.error as error:

            if error.errno == errno.WSAECONNRESET:
                print(f'connection with ip {client_address[0]}, port {client_address[1]} was forcibly closed')
                continue
