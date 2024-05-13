#!/usr/bin/python3

import paramiko
import getpass
import datetime

# Define SSH parameters and command
router_ip = input("Enter the IP address: ")
username = input("Username: ")
password = getpass.getpass(prompt="Password: ")

# Create SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the router
    ssh_client.connect(router_ip, username=username, password=password)
    print("Connected to MikroTik router.")

    # Get current date and time for backup file naming
    now = datetime.datetime.now()
    backup_filename = f"fwbackup_{now.strftime('%Y-%m-%d-%H-%M-%S')}.backup"

    # Execute the command
    command = f'/export file={backup_filename}'
    stdin, stdout, stderr = ssh_client.exec_command(command)

    # Wait for the command to complete
    stdout.channel.recv_exit_status()
    
    # Check if the backup file was created successfully
    sftp_client = ssh_client.open_sftp()
    remote_files = sftp_client.listdir()
    if f"{backup_filename}.rsc" in remote_files:
        file_size = sftp_client.stat(f"{backup_filename}.rsc").st_size
        if file_size > 0:
            print(f"Backup completed successfully. Configuration saved as '{backup_filename}'.")
        else:
            print("Backup file size is 0. Backup may have failed.")
    else:
        print("Backup file not found. Backup may have failed.")

except paramiko.AuthenticationException:
    print("Authentication failed. Please check your credentials.")
except paramiko.SSHException as ssh_ex:
    print(f"Error occurred while connecting to the router: {ssh_ex}")
except Exception as ex:
    print(f"An error occurred: {ex}")
finally:
    # Close the SSH connection
    ssh_client.close()
