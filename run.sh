#!/bin/bash

chmod +x *.sh

# Send the first command
ryu-manager ryu_controller.py &
# Insert your first command here

# Wait for 5 seconds
sleep 1

# Send the second command
sudo python3 network.py
# Insert your second command here
