import socket

HOST = "127.0.0.1"
PORT = 5000

name = input("Username: ").strip()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

s.sendall(f"HELLO|{name}\n".encode())
print(s.recv(1024).decode().strip())

while True:
    msg = input("> ")

    if msg.upper() == "EXIT":
        s.sendall("EXIT|\n".encode())
        print(s.recv(1024).decode().strip())
        break

    s.sendall(f"MSG|{msg}\n".encode())
    print(s.recv(1024).decode().strip())