#!/bin/bash

for ((i=1; i<=7; i++)); do
    echo @@@@@@@@@@@@@@@@@@@--------------SWITCH S$i----------------@@@@@@@@@@@@@@@@@@@@@
    sudo ovs-ofctl dump-flows s$i
done
