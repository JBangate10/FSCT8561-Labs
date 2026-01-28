import nmap
import sys

target = "127.0.0.1"
ports = "20-1024"

try:
    nm = nmap.PortScanner()
except:
    print("ERROR: Nmap is not installed or not accessible")
    sys.exit()

print("Scanning target:", target)
print("Port range:", ports)

try:
    nm.scan(target, ports)
except nmap.PortScannerError:
    print("ERROR: Permission denied (try running with admin privileges)")
    sys.exit()
except:
    print("ERROR: Host unreachable")
    sys.exit()

if target not in nm.all_hosts():
    print("ERROR: Host unreachable")
    sys.exit()

open_found = False

for proto in nm[target].all_protocols():
    for port in nm[target][proto]:
        state = nm[target][proto][port]["state"]
        service = nm[target][proto][port].get("name", "unkown")

        print(f"Port {port}/{proto} - {state} - Service: {service}")

        if state == "open":
            open_found = True

if not open_found:
    print("No open ports found")