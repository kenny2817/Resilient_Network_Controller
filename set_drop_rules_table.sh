#!/bin/sh

# Making sure that only these hosts can communicate with each other: (h1, h2), (h2, h3)

echo "Setting drop rules for the network"
# s2
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.4,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.4,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.2,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s2 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.2,idle_timeout=0,actions=drop

# s4
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.4,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.4,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.2,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s4 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.2,idle_timeout=0,actions=drop

# s5
sudo ovs-ofctl add-flow s5 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s5 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.4,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s5 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s5 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.4,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s5 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s5 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.2,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s5 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s5 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.2,idle_timeout=0,actions=drop

# s7
sudo ovs-ofctl add-flow s7 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s7 ip,priority=65500,nw_src=10.0.0.1,nw_dst=10.0.0.4,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s7 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.3,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s7 ip,priority=65500,nw_src=10.0.0.2,nw_dst=10.0.0.4,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s7 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s7 ip,priority=65500,nw_src=10.0.0.3,nw_dst=10.0.0.2,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s7 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.1,idle_timeout=0,actions=drop
sudo ovs-ofctl add-flow s7 ip,priority=65500,nw_src=10.0.0.4,nw_dst=10.0.0.2,idle_timeout=0,actions=drop

echo "End of setting drop rules for the network"
echo " "