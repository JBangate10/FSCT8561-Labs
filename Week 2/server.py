import socket

HOST = "127.0.0.1"
PORT = 5000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen()

print("Server running...")

while True:
    conn, addr = s.accept()
    print("Connected:", addr)

    username = ""
    data_buffer = ""

    while True:
        part = conn.recv(1024)
        if not part:
            print("Client left:", addr)
            break
        data_buffer += part.decode("utf-8", "ignore")

        while "\n" in data_buffer:
            line, data_buffer = data_buffer.split("\n", 1)
            line = line.strip()

            if line == "":
                conn.sendall("ERROR|Empty\n".encode())
                continue

            if "|" not in line:
                conn.sendall("ERROR|Bad\n".encode())
                continue

            cmd, info = line.split("|", 1)
            cmd = cmd.upper()

            if username == "" and cmd != "HELLO":
                conn.sendall("ERROR|Login first\n".encode())
                continue

            if cmd == "HELLO":
                username = info.strip()
                conn.sendall(f"OK|HELLO {username}\n".encode())
                print("User:", username)
            
            elif cmd == "MSG":
                conn.sendall(f"OK|{username}: {info}\n".encode())
                print(username, "says:", info)
            
            elif cmd == "EXIT":
                conn.sendall("OK|Bye\n".encode())
                print(username, "disconnected")
                conn.close()
                break

            else:
                conn.sendall("ERROR|Unknown\n".encode())
        
        if cmd == "EXIT":
            break