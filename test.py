import re

with open("arp_output.txt", mode="r") as f:
    output = f.read()

pattern = r"(\d+\.\d+\.\d+\.\d+)(?:\s+(\w+:\w+:\w+:\w+:\w+:\w+)|\s+)(?:\s+(\S+)|\s+)(?:\s+([a-zA-Z]+)| )"

m = re.findall(rf"{pattern}", output, flags=re.MULTILINE)

print("-" * 25)
for entry in arp_table:
    print(f"Interface: {entry[2]}")
    print(f"  IP: {entry[0]}")
    print(f"  MAC: {entry[1]}")
    print(f"  Status: {entry[3]}")
    print("-" * 25)