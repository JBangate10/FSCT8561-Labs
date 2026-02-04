import socket, threading, hashlib, time
import pyotp

HOST = "127.0.0.1"
PORT = 6000

users = {
    "alice": {
        "pass_hash": hashlib.sha256("password123".encode()).hexdigest(),
        "otp_secret": pyotp.random_base32(),
        "fails": 0,
        "lock_until": 0
    }
}

issuer = "FSCT8561"
for u in users:
    secret = users[u]["otp_secret"]
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=u, issuer_name=issuer)
    print(f"[SETUP] user={u} otp_secret={secret}")
    print(f"[SETUP] provisioning_uri={uri}\n")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen()
print(f"[SERVER] Listening on {HOST}:{PORT}")

def handle(conn, addr):
    buf = ""
    pending_user = None

    while True:
        data = conn.recv(1024)
        if not data:
            conn.close()
            return
        
        buf += data.decode(errors="ignore")
        while "\n" in buf:
            line, buf = buf.split("\n", 1)
            line = line.strip()

            if "|" not in line:
                conn.sendall(b"ERROR|Bad format\n")
                continue

            cmd, rest = line.split("|", 1)

            if cmd == "USERPASS":
                parts = rest.split("|")
                if len(parts) != 2:
                    conn.sendall(b"ERROR|Bad USERPASS\n")
                    continue

                user, pass_hash = parts[0], parts[1]
                if user not in users:
                    conn.sendall(b"ERROR|Unknown user\n")
                    continue

                now = time.time()
                if now < users[user]["lock_until"]:
                    conn.sendall(b"ERROR|Locked (too many fails)\n")
                    continue

                if pass_hash != users[user]["pass_hash"]:
                    users[user]["fails"] += 1
                    if users[user]["fails"] >= 3:
                        users[user]["lock_until"] = now + 30
                        users[user]["fails"] = 0
                        conn.sendall(b"ERROR|Too many fails (locked 30s)\n")
                    else:
                        conn.sendall(b"ERROR|Wrong password\n")
                    continue

                pending_user = user
                conn.sendall(b"OK|Password verified, send OTP\n")
            
            elif cmd == "OTP":
                if pending_user is None:
                    conn.sendall(b"ERROR|Send USERPASS first\n")
                    continue

                otp = rest.strip()
                now = time.time()
                if now < users[pending_user]["lock_until"]:
                    conn.sendall(b"ERROR|Locked (too many fails)\n")
                    continue

                totp = pyotp.TOTP(users[pending_user]["otp_secret"])

                if totp.verify(otp, valid_window=1):
                    users[pending_user]["fails"] = 0
                    pending_user = None
                    conn.sendall(b"Access granted\n")
                else:
                    users[pending_user]["fails"] += 1
                    if users[pending_user]["fails"] >= 3:
                        users[pending_user]["lock_until"] = time.time() + 30
                        users[pending_user]["fails"] = 0
                        conn.sendall(b"ERROR|Too many fails (locked 30s)\n")
                    else:
                        conn.sendall(b"ERROR|Invalid/expired OTP (check clock)\n")
            
            elif cmd == "EXIT":
                conn.sendall(b"OK|Bye\n")
                conn.close()
                return
            
            else:
                conn.sendall(b"ERROR|Unkown command\n")

while True:
    conn, addr = s.accept()
    print("[SERVER] Connection:", addr)
    threading.Thread(target=handle, args=(conn, addr), daemon=True).start()