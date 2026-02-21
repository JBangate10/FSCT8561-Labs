import socket
import hashlib
import os
import time
import json
import threading

# In-memory storing
users = {
    "admin":{
        "pass_hash": hashlib.sha256("StrongPass!".encode()).hexdigest()
    }
}

HOST = "127.0.0.1"
PORT = 7000

# Generating fresh random nonce string
def new_nonce():
    return os.urandom(8).hex()

# Server challenge/response logic
def handle_client(conn, addr):
    print("Client connected:", addr)
    data = conn.recv(1024).decode()
    msg = json.loads(data)

    # Expect initial HELLO with username
    if msg.get("type") != "AUTH_HELLO":
        conn.send(json.dumps({"type":"ERROR", "msg":"Bad start"}).encode())
        conn.close()
        return
    
    username = msg["payload"]["username"]
    if username not in users:
        conn.send(json.dumps({"type":"AUTH_FAIL","msg":"Unknown user"}).encode())
        conn.close()
        return
    
    # Send random server challenge (nonce + timestamp)
    challenge = new_nonce()
    timestamp = int(time.time())
    conn.send(json.dumps({
        "type": "AUTH_CHALLENGE",
        "payload": {"nonce": challenge, "timestamp": timestamp}
    }).encode())

    # Receive client response
    response_data = json.loads(conn.recv(1024).decode())
    client_hash = response_data["payload"]["response"]

    # Compute client response
    stored_hash = users[username]["pass_hash"]
    expected = hashlib.sha256((stored_hash + challenge + str(timestamp)).encode()).hexdigest()

    if client_hash == expected:
        conn.send(json.dumps({"type":"AUTH_OK"}).encode())
    else:
        conn.send(json.dumps({"type":"AUTH_FAIL","msg":"Bad credentials"}).encode())
    
    conn.close()

# Run the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST,PORT))
server.listen()

print("Auth server listenting...")
while True:
    c,a = server.accept()
    threading.Thread(target=handle_client.args(c,a)).start()