#!/bin/bash

# Foreach switch clear the table

echo "Set controller rules to all tables"
for arg in "$@"; do
    sudo ovs-vsctl set-controller s"$arg" tcp:127.0.0.1:6633
done
echo "End of setting controller rules to all tables"
echo " "