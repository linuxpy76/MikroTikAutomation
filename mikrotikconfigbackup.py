#!/usr/bin/python3

# Script created by Kyle Ringler
# GitHub: https://github.com/linuxpy76/MikroTikAutomation
# License: GPL 3.0

# This script connects to a MikroTik router and creates a backup file. Optionally you can pull the backup to the local system.

import paramiko
import getpass
import datetime
import argparse
import os

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Logs into MikroTik router and creates a config backup.")

# Add arguments
parser.add_argument("-r", "--router-ip", type=str, help="Hostname or remote IP address without CIDR notation. \nEx. 192.168.10.1 or router.org.lan")
parser.add_argument("-P", "--port", type=int, help="Select the port to use. Default: 22")
parser.add_argument("--list", type=str, help="Provide the path to a list. Ex. /home/user/Documents/list.txt")
parser.add_argument("-u", "--username", type=str, help="Username Ex. admin")
parser.add_argument("-p", "--password", type=str, help="Enter router password. If you skip this option then you will be prompted for it. (hides the pass)")
parser.add_argument("-d", "--directory", type=str, help="Path to save config file. If backup is not defined then the remote copy and delete operations will be skipped. \nEx. C:\\backup\\")
parser.add_argument("--delete", action="store_true", help="Delete the remote backup file from the router. Default: False")
parser.add_argument("-e", "--encryption-password", type=str, help="Enter your backup encryption password.")

# Parse the command-line arguments
args = parser.parse_args()
config = vars(args)
# Output to test if arguments are being accepted
print(config)

# Assigning arguments to variables for SSH parameters
# args values must be the later value and not the first one
# Even though the argument above is router-ip this args value must be args.router_ip
router_ip = args.router_ip
port = args.port
list = args.list
username = args.username
password = args.password
directory = args.directory
delete_remote_file = args.delete
encryption_password = args.encryption_password

# If arguments aren't supplied then ask user for input to define SSH parameters
if args.router_ip is None:
    # Prompt for Router IP
    router_ip = input("Enter the IP address: ").strip()
if args.port is None:
    # Prompt for SSH port number
    port = int(input("Enter an SSH port number: "))
if args.username is None:
    # Prompt for Username
    username = input("Username: ").strip()
if args.password is None:
    # Prompt for Password
    password = getpass.getpass(prompt="Password: ").strip()
if args.directory is None:
    # Prompt for Directory
    directory = input("Enter the local backup directory: ").strip()
if args.encryption_password is None:
    # Prompt for Encryption Password
    encryption_password = getpass.getpass(prompt="Encryption Password: ").strip()

# Get routes from file and compose a list
with open(f"{list}", "r") as file:
    # Read lines and strip for routers
    router_ip_addresses = [line.strip() for line in file.readlines()]

# Print routers
print("Listing routers...")
print(router_ip_addresses)

# Define function to append endswitch to path if there isn't one
def save_endswitch_to_path(path):
    # Check if the directory path ends with a endswitch
    if not path.endswith(os.path.sep):
        path += os.path.sep # Append a endswitch to the path
    return path

# Call function to append endswitch to directory path if it's defined and it's blank
if "directory" in globals() and directory != "":
    directory = save_endswitch_to_path(directory)

# Create SSH and SFTP clients
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Get current date and time for backup file naming
now = datetime.datetime.now()

try:
    def connect_to_router(router_ip, port, username, password):
        # Connect to the router
        ssh.connect(router_ip, port=port, username=username, password=password)
        print(f"Connected to {router_ip} MikroTik router.")

    def get_router_identity():
        # Get router identity
        global router_identity
        identity_command = "/system/identity/print"
        stdin, stdout, stderr = ssh.exec_command(identity_command)
        router_identity = stdout.read().decode("utf-8").strip().split()[1]
        # return router_identity

    def name_files(router_identity):
        global cfg_bak_filename
        cfg_bak_filename = f"{router_identity}_cfg_backup_{now.strftime('%Y-%m-%d-%H%M%S')}"
        cfg_bak_filename = f"{cfg_bak_filename}.rsc"
        global sys_bak_filename
        sys_bak_filename = f"{router_identity}_sys_backup_{now.strftime('%Y-%m-%d-%H%M%S')}"
        sys_bak_filename = f"{sys_bak_filename}.backup"
        # return cfg_bak_filename, sys_bak_filename

    def execute_backups():
        # Execute the config backup command
        cfg_bak_cmd = f"/export file={cfg_bak_filename}"
        stdin, stdout, stderr = ssh.exec_command(cfg_bak_cmd)
        # Wait for the command to complete
        stdout.channel.recv_exit_status()
        # Rename config backup variable for file checks
        # global cfg_bak_filename
        # cfg_bak_filename = f"{cfg_bak_filename}.rsc"

        # Execute the system backup command
        if "encryption_password" in globals() and encryption_password != "":
            print("System backup will be encrypted with aes-sha256 and provided password.")
            sys_bak_cmd = f"/system backup save name={sys_bak_filename} password={encryption_password}"
            stdin, stdout, stderr = ssh.exec_command(sys_bak_cmd)
            # Wait for the command to complete
            stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
        else:
            print("WARNING! System backup will not be encrypted. No password provided.")
            sys_bak_cmd = f"/system backup save name={sys_bak_filename} dont-encrypt yes"
            stdin, stdout, stderr = ssh.exec_command(sys_bak_cmd)
            # Wait for the command to complete
            stdout.channel.recv_exit_status()
            output = stdout.read().decode('utf-8')
        # Rename System backup variable for file checks
        # global sys_bak_filename
        # sys_bak_filename = f"{sys_bak_filename}.backup"
        # return output, cfg_bak_filename, sys_bak_filename

    def verify_backup_creation(cfg_bak_filename, sys_bak_filename):
        # Check if the backup file was created successfully
        sftp_client = ssh.open_sftp()
        global remote_files
        remote_files = sftp_client.listdir()

        # Check that the config backup file was created
        if cfg_bak_filename in remote_files:
            cfg_bak_filesize = sftp_client.stat(cfg_bak_filename).st_size
            if cfg_bak_filesize > 0:
                print(f"Config backup completed successfully. Configuration saved as '{cfg_bak_filename}'.")
            else:
                print("Config backup file size is 0. Backup may have failed.")
        else:
            print("Config backup file not found. Backup may have failed.")
    
        # Check that the system backup file was created
        if sys_bak_filename in remote_files:
            sys_bak_filesize = sftp_client.stat(sys_bak_filename).st_size
            if sys_bak_filesize > 0:
                print(f"System backup completed successfully. Configuration saved as '{sys_bak_filename}'.")
            else:
                print("System backup file size is 0. Backup may have failed.")
        else:
            print("System backup file not found. Backup may have failed.")
        # return remote_files

    def download_backups(cfg_bak_filename, sys_bak_filename, remote_files):
        # Backup files to local directory
        sftp_client = ssh.open_sftp()
        if cfg_bak_filename in remote_files and directory:
            # Define local path for the config backup file
            cfg_bak_path = directory + cfg_bak_filename
            sys_bak_path = directory + sys_bak_filename

            # Download the backup file to the local directory
            sftp_client.get(cfg_bak_filename, cfg_bak_path)
            print(f"Config backup copied to '{cfg_bak_path}'")
            sftp_client.get(sys_bak_filename, sys_bak_path)
            print(f"System backup copied to '{sys_bak_path}'")

            # Remove the backup file from the router (optional)
            if delete_remote_file == True:
                sftp_client.remove(cfg_bak_filename)
                print(f"Config backup file '{cfg_bak_filename}' removed from the router.")
                sftp_client.remove(sys_bak_filename)
                print(f"System backup file '{sys_bak_filename}' removed from the router.")
    
        elif cfg_bak_filename in remote_files and not directory:
            print("Local backup directory not provided. Skipping file transfer and deletion.")
 
        else:
            print(f"An error occurred! Backup file not found!")

except paramiko.AuthenticationException:
    print("Authentication failed. Please check your credentials.")
except paramiko.SSHException as ssh_ex:
    print(f"Error occurred while connecting to the router: {ssh_ex}")
except Exception as ex:
    print(f"An error occurred: {ex}")
# finally:

def main():
    for router_ip in router_ip_addresses:
        print(f"Starting process on {router_ip}...")
        # Connect to the router
        connect_to_router(router_ip, port, username, password)
        # Fetch the router identity
        get_router_identity()
        # Create backup file names
        name_files(router_identity)
        # Create the backups
        execute_backups()
        # Verify that the backup was created
        verify_backup_creation(cfg_bak_filename, sys_bak_filename)
        # Download the backups using SFTP to local directory
        download_backups(cfg_bak_filename, sys_bak_filename, remote_files)
        # Close the SSH connection
        ssh.close()

if __name__ == "__main__":
    main()
