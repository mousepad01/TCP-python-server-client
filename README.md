# TCP-python-server-client
TCP server and client implementation for a chat application

implemented:
- login system with username and password
- passwords are hashed
- sending messages to specific online users
- messages are encrypted with RC5 - CBC mode of operation, decrypted on the server and then re-encrypted and sent to specific user (NOT E2EE)
- asynchrnous client code (using asyncio and aioconsole - https://pypi.org/project/aioconsole/), so that receiving and sending messages can happen simultaneously

to do list:
- end to end encryption 
- integrating diffie-hellman key exchange protocol for the above mentioned encryption

