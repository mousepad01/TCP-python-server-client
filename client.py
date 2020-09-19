import socket
import errno
import pickle

import asyncio
import aioconsole

from RC5 import RC5_key_generator
from CBC_RC5 import RC5_CBC_encryption, RC5_CBC_decryption


HEADER_SIZE = 10
SERVER_IP = socket.gethostname()
SERVER_PORT = 5000

KEY = 0
EXPANDED_KEY = []

SLEEP_TIME = 0.01  # in seconds


def receive(client_socket):

    try:

        message_header = client_socket.recv(HEADER_SIZE)
        if message_header:
            message_length = int(message_header.decode('utf-8'))

            message_pack_encrypted = client_socket.recv(message_length)
            message_pack_encrypted = pickle.loads(message_pack_encrypted)
            message_pack_decrypted = RC5_CBC_decryption(message_pack_encrypted[0], EXPANDED_KEY, message_pack_encrypted[1])

            message_pack = pickle.loads(message_pack_decrypted)

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
        msg_pack_encrypted = RC5_CBC_encryption(msg_pack, EXPANDED_KEY)
        to_send = pickle.dumps(msg_pack_encrypted)

        to_send = f"{len(to_send):<{HEADER_SIZE}}".encode('utf-8') + to_send

        client_socket.send(to_send)

    except socket.error as err:

        if err.errno == errno.WSAECONNRESET:
            print(f"server with address {(SERVER_IP, SERVER_PORT)} has forcibly closed the connection")


# socket init

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("socket initialized")

# key init

key_file = open("client_key.txt")
KEY = int(key_file.read())

EXPANDED_KEY = RC5_key_generator(KEY)

# auth procedure

print("please write your username, press ENTER then write the corresponding password and press ENTER again")

username = input("username > ")
password = input("password > ")

auth_data = pickle.dumps({'username': username, 'password': password})
auth_data_encrypted = RC5_CBC_encryption(auth_data, EXPANDED_KEY)
auth_data_encrypted = pickle.dumps(auth_data_encrypted)
auth_data_to_send = f"{len(auth_data_encrypted):<{HEADER_SIZE}}".encode('utf-8') + auth_data_encrypted

client_socket.connect((SERVER_IP, SERVER_PORT))
client_socket.send(auth_data_to_send)

client_socket.settimeout(1)

auth_rez = receive(client_socket)
if auth_rez:
    show_msg(auth_rez)
else:
    print("authentication failed (wrong username / password or username is already online); client app is now closed")
    quit()

client_socket.settimeout(1)

# main loops after successful auth

# due to being implemented without proper user interface, inputs must be read from console in asynchronous way in a limited time


async def input_loop():

    while True:

        receiver = await aioconsole.ainput("send message to : ")
        message_to_send = await aioconsole.ainput("message > ")

        send_msg(client_socket, (receiver, message_to_send))


async def receive_loop():

    while True:

        msg_received_pack = receive(client_socket)
        if msg_received_pack:

            print("(incoming messages, write the destination/ message after receiving following messages)")

            show_msg(msg_received_pack)

        await asyncio.sleep(SLEEP_TIME)


async def main_client_loop():

    tasks = [asyncio.create_task(receive_loop()), asyncio.create_task(input_loop())]

    await asyncio.gather(*tasks)


asyncio.run(main_client_loop())

# old synchronous version of the implementation

'''while True:

    receiver = input("send message to : ")
    message_to_send = input("message > ")

    send_msg(client_socket, (receiver, message_to_send))

    while True:

        msg_received_pack = receive(client_socket)
        if msg_received_pack:
            show_msg(msg_received_pack)
        else:
            break'''






