#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink
from mininet.cli import CLI
import subprocess

class MyTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        host_config = dict(inNamespace=True)
        switch_link_config = dict(bw=10)
        host_link_config = dict()

        # Create hosts
        for i in range(1,3):
            self.addHost("h%d" % (i), **host_config)

        # Create switches
        for i in range(1,3):
            scofig = {"dpid": "%016x" % (i)}
            self.addSwitch("s%d" % (i), **scofig)

        # Add links between H-S
        self.addLink("h1", "s1", **host_link_config)
        self.addLink("h2", "s2", **host_link_config)

        # Add links between S-S
        self.addLink("s1", "s2", **switch_link_config) 

topos = {'mytopo': (lambda: MyTopo())}

if __name__ == "__main__":
    topo = MyTopo()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)
    net.build()
    net.start()

    subprocess.call(["./set_queue.sh", "s1", "eth2", "eth1", "s2"])

    CLI(net)
    net.stop()
