#!/bin/bash

# Foreach switch clear the table

echo "Clearing all tables"
for ((i=1; i<=7; i++)); do
    sudo ovs-vsctl del-controller s$i
done
echo "All tables cleared"
echo " "