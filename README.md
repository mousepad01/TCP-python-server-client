# TCP-python-server-client
TCP server and client implementation for a chat application

note: client currently configured to run on localhost; to make it connect at distance, change SERVER_IP (from client.py) to the corresponding public ipv4 of the server 

implemented:
- login system with username and password
- passwords are hashed
- sending messages to specific online users
- end to end encryption implemented with RC5 block cipher operating in CBC mode
- asynchronous client code (using asyncio and aioconsole - https://pypi.org/project/aioconsole/), so that receiving and sending messages can happen simultaneously

to do list:
- integrating diffie-hellman key exchange protocol for the above mentioned encryption

