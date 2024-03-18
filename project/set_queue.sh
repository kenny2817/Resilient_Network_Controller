#!/bin/sh

# creating the queues through $4 switch 

# parameters
# $1 - first switch
# $2 - port for first switch
# $3 - lest port for second switch
# $4 - second switch
# $5 - right port for second switch
# $6 - port for third switch
# $7 - third switch

echo ' ---------------------------------------------- '
echo '*** Network Slicing: Creating 2 slices of 5 Mbps each ...'
echo 'Link_1: $1 - $4 ----- on interf: $1-$2'
sudo ovs-vsctl set port $1-$2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:1=@1q \
queues:2=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=5000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=5000000

echo ' '
echo 'Link_2: $4 - $1 ----- on interf: $4-$3'
sudo ovs-vsctl set port $4-$3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:1=@1q \
queues:2=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=5000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=5000000

echo ' '
echo 'Link_3: $4 - $7 ----- on interf: $4-$5'
sudo ovs-vsctl set port $4-$5 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:1=@1q \
queues:2=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=5000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=5000000

echo ' '
echo 'Link_4: $7 - $4 ----- on interf: $7-$6'
sudo ovs-vsctl set port $7-$6 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:1=@1q \
queues:2=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=5000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=5000000

echo '*** End of Creating the Slices ...'
echo ' ---------------------------------------------- '

# Mapping the $1 virtual queues to hosts:
# (h1, h2) --> queue1
sudo ovs-ofctl add-flow $1 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=set_queue:1,normal
sudo ovs-ofctl add-flow $4 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=set_queue:1,normal
sudo ovs-ofctl add-flow $7 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=set_queue:1,normal
sudo ovs-ofctl add-flow $4 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=set_queue:1,normal
# (h3, h4) --> queue2
sudo ovs-ofctl add-flow $1 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=set_queue:2,normal
sudo ovs-ofctl add-flow $4 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=set_queue:2,normal
sudo ovs-ofctl add-flow $7 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=set_queue:2,normal
sudo ovs-ofctl add-flow $4 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=set_queue:2,normal


