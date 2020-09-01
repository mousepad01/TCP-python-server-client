import socket
import pickle

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


def process_warnings(client_socket, warning):

    if warning == "closed":

        print(f"connection closed by the server({SERVER_IP}, {SERVER_PORT})")
        quit()

    else:
        print(f"unknown warning received from the server({SERVER_IP}, {SERVER_PORT}): {warning}")


def process_request(client_socket, request):

    if request == "close":

        send_msg(client_socket, "!closed")
        client_socket.close()

    elif request == "hello":

        send_msg(client_socket, "hello there!")

    else:
        print(f"unknown request received from the server({SERVER_IP}, {SERVER_PORT}): {request}")


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))


while True:

    message = input()
    send_msg(client_socket, message)

    received = receive(client_socket)

    if received[0] == "/":
        process_request(client_socket, received[1:])
    elif received[0] == "!":
        process_warnings(client_socket, received[1:])
    else:
        print(received)




