#!/usr/bin/python3

import argparse

# Create an ArgumentParser object
parser = argparse.ArgumentParser(description="Logs into MikroTik router and creates a config backup.")

# Add arguments
parser.add_argument('arg1', type=str, help="An IP address without CIDR notation. Ex: 192.168.10.1")
parser.add_argument('-u', type=str, help="Username Ex. admin")
parser.add_argument('-p', type=str, help="Password")

# Parse the command-line arguments
args = parser.parse_args()

config = vars(args)
print(config)