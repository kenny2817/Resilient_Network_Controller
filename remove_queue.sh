#!/bin/sh

# parameters
# $1 - first switch
# $2 - port for first switch
# $3 - lest port for second switch
# $4 - second switch
# $5 - right port for second switch
# $6 - port for third switch
# $7 - third switch

echo ' ---------------------------------------------- '
echo '*** Network Slicing: Removing slices and reverting to single channel ...'

echo "Removing slices on link $1-$2"
sudo ovs-vsctl clear port $1-$2 qos

echo "Removing slices on link $4-$3"
sudo ovs-vsctl clear port $4-$3 qos

echo "Removing slices on link $4-$5"
sudo ovs-vsctl clear port $4-$5 qos

echo "Removing slices on link $7-$6"
sudo ovs-vsctl clear port $7-$6 qos

echo '*** End of Removing Slices ...'
echo ' ---------------------------------------------- '
echo ' '
