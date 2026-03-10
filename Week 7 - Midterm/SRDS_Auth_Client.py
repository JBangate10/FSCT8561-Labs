import socket
import hashlib
import json

HOST = "127.0.0.1"
PORT = 7000

username = input("Username: ")
password = input("Password: ")

# Connect server
s = socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

s.send(json.dumps({
    "type": "AUTH_HELLO",
    "payload": {"username": username}
}).encode())

challenge_msg = json.loads(s.recv(1024).decode())

if challenge_msg["type"] != "AUTH_CHALLENGE":
    print("Protocol error")
    s.close()
    exit()

nonce = challenge_msg["payload"]["nonce"]
ts = str(challenge_msg["payload"]["timestamp"])

# Compute response using stored password hash + nonce + timestamp
pass_hash = hashlib.sha256(password.encode()).hexdigest()
response = hashlib.sha256((pass_hash + nonce + ts).encode()).hexdigest()

# Send response
s.send(json.dumps({
    "type": "AUTH_RESPONSE",
    "payload": {"response": response}
}).encode())

result = json.loads(s.recv(1024).decode())
print("Server says:", result)

s.close()