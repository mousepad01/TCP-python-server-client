import socket
import pickle
import errno

HEADER_LENGTH = 10
SERVER_IP = socket.gethostname()
SERVER_PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, SERVER_PORT))

# login process

username = input("Username:")
password = input("Password:")

auth_data = ''

if len(username) < 10:
    auth_data = f"0{len(username)} {username}: {password}"
else:
    auth_data = f"{len(username)} {username}: {password}"

auth_data = pickle.dumps({"username": username, "password": password})
auth_data = bytes(f"{len(auth_data):<{HEADER_LENGTH}}", 'utf-8') + auth_data

client_socket.send(auth_data)

# verify if auth data is correct

ver = client_socket.recv(1)

if ver.decode('utf-8') == 'F':

    print(f"invalid auth data")
    quit()

elif ver.decode('utf-8') == 'T':

    client_socket.setblocking(False)

    # client is now logged in
    # main loop for receiving and sending messages

    print("connection established with server; you can now send and receive messages")

    while True:

        message = input(f"{username} > ")

        if message:
            message = bytes(message, 'utf-8')
            message = bytes(f"{len(message):<{HEADER_LENGTH}}", 'utf-8') + message

            client_socket.send(message)

        try:
            while True:

                username_header = client_socket.recv(HEADER_LENGTH)
                if not username_header:
                    print("connection closed by the server")
                    quit()

                username_length = int(username_header.decode('utf-8'))
                username = client_socket.recv(username_length)
                username = username.decode('utf-8')

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8'))
                message = client_socket.recv(message_length)
                message = message.decode('utf-8')

                print(f"{username} > {message}")

        except:
            continue

        '''while True:
    
            chunk = s.recv(32)
    
            if new_message:
    
                length_message = int(chunk[:HEADERSIZE])
                print(f'message with length {length_message} is being received...')
    
                new_message = False
    
            current_message += chunk
    
            if len(current_message) - HEADERSIZE == length_message:
    
                received = pickle.loads(current_message[HEADERSIZE:])
                print(received)
    
                length_message = 0
                new_message = True
                current_message = b'''''
