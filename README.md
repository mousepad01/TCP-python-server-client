# TCP-python-server-client
TCP server and client implementation for a chat application

implemented:
- login system with username and password
- passwords are hashed
- sending messages to specific online users
- messages are encrypted with RC5 - CBC mode of operation, decrypted on the server and then re-encrypted and sent to specific user (NOT E2EE)

to do list:
- end to end encryption 
- (maybe?) integrating diffie-hellman key exchange protocol for the above mentioned encryption
- (maybe?) asynchrnous client code, so that receiving and sending messages can happen simultaneously
