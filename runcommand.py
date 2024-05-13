#!/usr/bin/python3

import paramiko
import getpass

# Define SSH parameters and command
router_ip = input("Enter the IP address: ")
username = input("Username: ")
password = getpass.getpass(prompt="Password: ")
command = input("Enter your command: ")

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
