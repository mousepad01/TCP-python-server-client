import socket
import select
import queue

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


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setblocking(0)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen()

# known sockets

input_sockets = [server_socket]
output_sockets = []

# message queues dictionary

all_message_queues = {}

while input_sockets:

    readable_sockets, writable_sockets, except_sockets = select.select(input_sockets, output_sockets, input_sockets)

    for r_s in readable_sockets:

        if r_s == server_socket:  # if there is a new client

            connected_socket, connecte_address = server_socket.accept()
            input_sockets.append(connected_socket)
            all_message_queues[connected_socket] = queue.Queue()

            connected_socket.setblocking(0)

        else:  # if there was a message received from a connected client

            message_received = receive(r_s)
            if message_received:

                # puts received messages from a socket to be sent to the same socket (echo server)

                    all_message_queues[r_s].put(message_received)

                    if r_s not in output_sockets:
                        output_sockets.append(r_s)

            else:

                # readable sockets without data -> disconnected client

                input_sockets.remove(r_s)
                if r_s in output_sockets:
                    output_sockets.remove(r_s)

                del message_received[r_s]

    for w_s in writable_sockets:

        try:
            message_to_send = message_received[w_s].get_nowait()

        except queue.Empty:
            output_sockets.remove(w_s)

        else:
            send_msg(w_s, message_to_send)

    for e_s in except_sockets:

        input_sockets.remove(e_s)

        if e_s in output_sockets:
            output_sockets.remove(e_s)

        e_s.close()

        del message_received[e_s]
