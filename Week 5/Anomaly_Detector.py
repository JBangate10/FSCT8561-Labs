from scapy.all import rdpcap, IP, TCP, UDP, UDP_SERVICES

pcap = rdpcap("botnet-capture-20110812-rbot.pcap")

tcp_count = 0
udp_count = 0
timeline = {}
alerts = set()

for pkt in pcap:
    if IP not in pkt:
        continue
    ip = pkt[IP].src
    t = pkt.time

    if TCP in pkt: tcp_count += 1
    if UDP in pkt: udp_count += 1

    if ip not in timeline:
        timeline[ip] = []
    timeline[ip].append(t)

    window = [x for x in timeline[ip] if t - x <= 5]
    timeline[ip] = window

    if len(window) > 20 and ip not in alerts:
        print(f"ALERT: Flooding form {ip}")
        alerts.add(ip)
    
print("\nTotal TCP:", tcp_count)
print("Total UDP:", udp_count)
print("Suscpicious IPs:", len(alerts))