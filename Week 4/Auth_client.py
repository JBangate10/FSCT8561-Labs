import socket, hashlib
from getpass import getpass

HOST = "127.0.0.1"
PORT = 6000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

user = input("Username: ").strip()
pw = getpass("Password (not shown): ")

pw_hash = hashlib.sha256(pw.encode()).hexdigest()
s.sendall(f"USERPASS|{user}|{pw_hash}\n".encode())

resp = s.recv(1024).decode(errors="ignore").strip()
print("Server:", resp)

if resp.startswith("OK|"):
    otp = input("TOTP code: ").strip()
    s.sendall(f"OTP|{otp}\n".encode())
    resp2 = s.recv(1024).decode(errors="ignore").strip()
    print("Server:", resp2)

s.sendall(b"EXIT|\n")
s.close()