from scapy.all import sniff, IP, TCP, UDP, Raw

counts = {"TCP":0, "UDP":0, "Other":0}

def packet_callback(pkt):
    proto = "Other"
    if IP in pkt:
        src = pkt[IP].src
        dst = pkt[IP].dst
    else:
        src, dst = "N/A", "N/A"
    
    if TCP in pkt:
        proto = "TCP"
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
        counts["TCP"] += 1
    elif UDP in pkt:
        proto = "UDP"
        sport = pkt[UDP].sport
        dport = pkt[UDP].dport
        counts["UDP"] += 1
    else:
        sport = dport = "N/A"
        counts["Other"] += 1
    
    print(f"{proto} {src}:{sport} -> {dst}:{dport}")

    if Raw in pkt:
        payload = pkt[Raw].load.decode(errors="ignore")
        if "password" in payload.lower():
            print("** Sensitive Data Detected:", payload)

print("Capturing 50 TCP packets")
sniff(filter="tcp", count=50, prn=packet_callback)

print("\nCapturing 50 HTTP packets")
sniff(filter="tcp port 80", count=50, prn=packet_callback)

print("\nCapturing 50 DNS packets")
sniff(filter="udp port 53", count=50, prn=packet_callback)

print("\nSummary:", counts)