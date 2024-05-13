#!/usr/bin/python3

import paramiko
import getpass
import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Logs into MikroTik router and runs a single command.")

# Add arguments
parser.add_argument("-r", "--router-ip", type=str, help="Hostname or remote IP address without CIDR notation. \nEx. 192.168.10.1 or router.org.lan")
parser.add_argument("-u", "--username", type=str, help="Username Ex. admin")
parser.add_argument("-p", "--password", type=str, help="Enter your password. If you skip this option then you will be prompted for it. (hides the pass)")
parser.add_argument("-c", "--command",type=str, help="Enter the command to be run. Don't forget to create a backup!")

# Parse the command-line arguments
args = parser.parse_args()
config = vars(args)
# Output to test if arguments are being accepted
print(config)

# Assigning arguments to variables for SSH parameters
# args values must be the later value and not the first one
# Even though the argument above is router-ip this args value must be args.router_ip
router_ip = args.router_ip
username = args.username
password = args.password
command = args.command

# If arguments aren't supplied then ask user for input to define SSH parameters
if args.router_ip is None:
    # Prompt for Router IP
    router_ip = input("Enter the IP address: ").strip()
if args.username is None:
    # Prompt for Username
    username = input("Username: ").strip()
if args.password is None:
    # Prompt for Password
    password = getpass.getpass(prompt="Password: ").strip()
if args.command is None:
    # Prompt for Command
    command = input("Command to execute: ")

# Create SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the router
    ssh_client.connect(router_ip, username=username, password=password)
    print("Connected to MikroTik router.")

    # Execute the command
    stdin, stdout, stderr = ssh_client.exec_command(command)

    # Read the output
    output = stdout.read().decode('utf-8')
    print("Command output:")
    print(output)

except paramiko.AuthenticationException:
    print("Authentication failed. Please check your credentials.")
except paramiko.SSHException as ssh_ex:
    print(f"Error occurred while connecting to the router: {ssh_ex}")
finally:
    # Close the SSH connection
    ssh_client.close()
