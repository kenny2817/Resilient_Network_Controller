#!/bin/bash

for ((i=1; i<=9; i++)); do
    echo @@@@@@@@@@@@@@@@@@@--------------SWITCH S$i----------------@@@@@@@@@@@@@@@@@@@@@
    sudo ovs-ofctl dump-flows s$i
done
