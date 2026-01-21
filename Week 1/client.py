import socket
import sys

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket Successfully Created!")
except socket.error as err:
    print("Socket Creation Failed with Error %s" %(err))

port = 80

try:
    host_ip = socket.gethostbyname('www.apple.com')
except socket.gaierror:
    
    print("There Was an Error Resolving the Host")
    sys.exit()

s.connect((host_ip, port))

print("The Socket has Successfully Connected to Apple")