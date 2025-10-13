#!/usr/bin/python3

import paramiko
import getpass
import argparse
import socket
import sys
import re

# Argument parser setup
parser = argparse.ArgumentParser(description="Logs into MikroTik router and runs a single command.")
parser.add_argument("-r", "--router-ip", type=str, help="Router IP or hostname (e.g. 192.168.10.1)")
parser.add_argument("-u", "--username", type=str, help="Username (e.g. admin)")
parser.add_argument("-p", "--password", type=str, help="Password. If omitted, you'll be prompted.")
args = parser.parse_args()

# Interactive prompts for missing args
router_ip = args.router_ip or input("Enter router IP: ").strip()
username = args.username or input("Username: ").strip()
password = args.password or getpass.getpass("Password: ").strip()
command = "/ip/dhcp/lease/print"

# Pre-check: test TCP connectivity
try:
    sock = socket.create_connection((router_ip, 22), timeout=5)
    banner = sock.recv(1024).decode(errors="ignore")
    sock.close()
    if not banner.startswith("SSH-"):
        print(f"Unexpected response on port 22: {banner.strip() or 'No banner received'}")
        print("Check if SSH is enabled and accessible on the router.")
        sys.exit(1)
except (socket.timeout, ConnectionRefusedError):
    print("Could not reach the router on port 22 (connection refused or timed out).")
    print("Verify SSH is enabled and not blocked by a firewall.")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected socket error: {e}")
    sys.exit(1)

# Create SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect
    ssh_client.connect(
        hostname=router_ip,
        username=username,
        password=password,
        port=22,
        timeout=10,
        banner_timeout=30,
        auth_timeout=10,
        look_for_keys=False,
        allow_agent=False,
    )
    print("Connected to MikroTik router.")

    stdin, stdout, stderr = ssh_client.exec_command(command)
    output = stdout.read().decode("utf-8", errors="ignore").strip()
    err = stderr.read().decode("utf-8", errors="ignore").strip()

    if output:
        print("\n--- Command Output ---")
        print(output)
    if err:
        print("\n--- Command Error ---")
        print(err)

except paramiko.AuthenticationException:
    print("Authentication failed. Check your username or password.")
except paramiko.SSHException as ssh_ex:
    print(f"SSH error: {ssh_ex}")
except socket.timeout:
    print("Connection timed out. The router may be unreachable or slow to respond.")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    ssh_client.close()

# This pattern doesn't match to all entries yet
pattern = r"(\d+\.\d+\.\d+\.\d+)\s+(\w+:\w+:\w+:\w+:\w+:\w+)(?:\s+(\S+)|\s+)(?:\s+(\S+))\s+(\w+)\s+(\w+)(?:\s+$|$)"

m = re.findall(rf"{pattern}", output, flags=re.MULTILINE)
print(len(m))
if m:
    dhcp_leases = m
    print(m)
    print("-" * 25)
    for entry in dhcp_leases:
        print(f"Server: {entry[3]}")
        print(f"  IP: {entry[0]}")
        print(f"  MAC: {entry[1]}")
        print(f"  Hostname: {entry[2]}")
        print(f"  Status: {entry[4]}")
        print(f"  Last Seen: {entry[5]}")
        print("-" * 25)