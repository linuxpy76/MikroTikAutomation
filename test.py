import re

with open("dhcpleases.txt", mode="r") as f:
    output = f.read()

pattern = r"(\d+\.\d+\.\d+\.\d+)\s+(\w+:\w+:\w+:\w+:\w+:\w+)(?:\s+(\S+)|\s+)(?:\s+(\S+))\s+(\w+)\s+(\w+)(?:\s+$|$)"

m = re.findall(rf"{pattern}", output, flags=re.MULTILINE)

if m:
    dhcp_leases = m
    print("-" * 25)
    for entry in dhcp_leases:
        print(f"Server: {entry[3]}")
        print(f"  IP: {entry[0]}")
        print(f"  MAC: {entry[1]}")
        print(f"  Hostname: {entry[2]}")
        print(f"  Status: {entry[4]}")
        print(f"  Last Seen: {entry[5]}")
        print("-" * 25)