import socket

s = socket.socket()
print("Socket Successfully Created")

port = 12345

s.bind(('', port))
print("Socket Binded to %s" %(port))

s.listen(5)
print("Socket is Listening")

while True:
    c, addr = s.accept()
    print('Got Connection From', addr)

    c.send("Thank You for Connecting".encode())

    c.close()

    break