#!/bin/sh

# parametri
# 1 switch dpid
# 2 switch dpid
# 3 s*-eth*
# 4 s*-eth*

echo ' ---------------------------------------------- '
echo '*** Network Slicing: Creating 2 slices of 5 Mbps each ...'
echo 'Link_1: s2 - s3 ----- on interf: s2-eth3'
sudo ovs-vsctl set port s2-eth3 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:1=@1q \
queues:2=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=5000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=5000000

echo ' '
echo 'Link_2: s3 - s2 ----- on interf: s3-eth1'
sudo ovs-vsctl set port s3-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:1=@1q \
queues:2=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=5000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=5000000

echo ' '
echo 'Link_3: s3 - s4 ----- on interf: s3-eth2'
sudo ovs-vsctl set port s3-eth2 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
queues:1=@1q \
queues:2=@2q -- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=5000000 -- \
--id=@2q create queue other-config:min-rate=1000000 other-config:max-rate=5000000

echo ' '
echo 'Link_4: s4 - s3 ----- on interf: s4-eth3'
sudo ovs-vsctl set port s4-eth3 qos=@newqos -- \
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
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=set_queue:1,normal
sudo ovs-ofctl add-flow s3 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=set_queue:1,normal
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=set_queue:1,normal
sudo ovs-ofctl add-flow s3 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=set_queue:1,normal
# (h3, h4) --> queue2
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=set_queue:2,normal
sudo ovs-ofctl add-flow s3 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.4,idle_timeout=0,actions=set_queue:2,normal
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=set_queue:2,normal
sudo ovs-ofctl add-flow s3 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.3,idle_timeout=0,actions=set_queue:2,normal


