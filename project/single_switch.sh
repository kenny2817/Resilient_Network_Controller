#!/bin/sh

# parametri
# 1 switch
# 2 host_A
# 3 host_B

echo ' ---------------------------------------------- '
echo '*** Network Slicing: Removing queues and setting to single bandwidth ...'
echo 'Link_1:'
# Set link to a single bandwidth without queues
sudo ovs-vsctl set port "$1"-eth0 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
-- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=10000000

echo ' '
echo 'Link_2:'
# Set link to a single bandwidth without queues
sudo ovs-vsctl set port "$1"-eth1 qos=@newqos -- \
--id=@newqos create QoS type=linux-htb \
other-config:max-rate=10000000 \
-- \
--id=@1q create queue other-config:min-rate=1000000 other-config:max-rate=10000000

echo '*** End of Removing Queues and Setting to Single Bandwidth ...'
echo ' ---------------------------------------------- '


# Mapping the $1 virtual queues to hosts:
# (h0, h2) --> queue1
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0."$2",nw_dst=10.0.0."$3",idle_timeout=0,actions=set_queue:1,normal
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0."$3",nw_dst=10.0.0."$2",idle_timeout=0,actions=set_queue:1,normal
# Making sure that only these hosts can communicate with each other: (h0, h2), (h1, h3)
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0.0,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0.0,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.0,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.2,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.0,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow "$1" ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.2,idle_timeout=0,actions=drop