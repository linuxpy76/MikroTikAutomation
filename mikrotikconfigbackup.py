#!/usr/bin/python3

import paramiko
import getpass
import datetime
import argparse
import os

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Logs into MikroTik router and creates a config backup.")

# Add arguments
parser.add_argument("-r", "--router-ip", type=str, help="Remote IP address without CIDR notation or hostname. Ex. 192.168.10.1 or router.org.lan")
parser.add_argument("-u", "--username", type=str, help="Username Ex. admin")
parser.add_argument("-p", "--password", type=str, help="Enter your password.")
parser.add_argument("-d", "--directory", type=str, help="Path to save config file. Ex. C:\\backup\\")
parser.add_argument("--delete", action="store_true", help="Delete the remote backup file from the router. Default: False")

# Parse the command-line arguments
args = parser.parse_args()

config = vars(args)

# Assigning arguments to variables for SSH parameters
# args values must be the later value and not the first one
# Even though the argument above is router-ip this args value must be args.router_ip
router_ip = args.router_ip
username = args.username
password = args.password
directory = args.directory
delete_remote_file = args.delete

# Output to test if arguments are being accepted
print(config)

# If arguments aren't supplied then ask user for input to define SSH parameters
if args.router_ip is None:
    # Prompt for Router IP
    router_ip = input("Enter the IP address: ")
if args.username is None:
    # Prompt for Username
    username = input("Username: ")
if args.password is None:
    # Prompt for Password
    password = getpass.getpass(prompt="Password: ")
if args.directory is None:
    # Prompt for Directory
    directory = input("Enter the local backup directory: ")

# Define function to append endswitch to path if there isn't one
def save_backslash_to_path(path):
    # Check if the directory path ends with a backslash
    if not path.endswith(os.path.sep):
        path += os.path.sep # Append a backslash to the path
    return path

# Call function to append endswitch to path
directory = save_backslash_to_path(directory)

# Create SSH client
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # Connect to the router
    ssh.connect(router_ip, username=username, password=password)
    print("Connected to MikroTik router.")

    # Get router identity
    identity_command = "/system/identity/print"
    stdin, stdout, stderr = ssh.exec_command(identity_command)
    router_identity = stdout.read().decode('utf-8').strip().split()[1]

    # Get current date and time for backup file naming
    now = datetime.datetime.now()
    backup_filename = f"{router_identity}_backup_{now.strftime('%Y-%m-%d-%H-%M-%S')}.backup"
    ext_filename = f"{backup_filename}.rsc"

    # Execute the command
    command = f'/export file={backup_filename}'
    stdin, stdout, stderr = ssh.exec_command(command)

    # Wait for the command to complete
    stdout.channel.recv_exit_status()
    
    # Check if the backup file was created successfully
    sftp_client = ssh.open_sftp()
    remote_files = sftp_client.listdir()
    if ext_filename in remote_files and directory:
        file_size = sftp_client.stat(ext_filename).st_size
        if file_size > 0:
            print(f"Backup completed successfully. Configuration saved as '{ext_filename}'.")
        else:
            print("Backup file size is 0. Backup may have failed.")
        
        # Define local path for the backup file
        local_backup_path = directory + ext_filename

        # Download the backup file to the local directory
        sftp_client.get(ext_filename, local_backup_path)

        # Remove the backup file from the router (optional)
        if delete_remote_file == True:
            sftp_client.remove(ext_filename)
            print(f"Backup file '{ext_filename}' removed from the router.")
    
    elif ext_filename in remote_files and not directory:
        print("Local backup directory not provided. Skipping file transfer and deletion.")

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
    ssh.close()
