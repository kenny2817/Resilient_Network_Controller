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
        for i in range(1,5):
            self.addHost("h%d" % (i), **host_config)

        # Create switches
        for i in range(1,8):
            scofig = {"dpid": "%016x" % (i)}
            self.addSwitch("s%d" % (i), **scofig)

        # Add links between H-S
        self.addLink("h1", "s2", **host_link_config)
        self.addLink("h2", "s4", **host_link_config)
        self.addLink("h3", "s5", **host_link_config)
        self.addLink("h4", "s7", **host_link_config)

        # Add links between S-S
        self.addLink("s1", "s2", **switch_link_config)
        self.addLink("s1", "s4", **switch_link_config)
        self.addLink("s2", "s3", **switch_link_config)
        self.addLink("s2", "s5", **switch_link_config)
        self.addLink("s3", "s4", **switch_link_config)
        self.addLink("s4", "s7", **switch_link_config)
        self.addLink("s5", "s6", **switch_link_config)
        self.addLink("s6", "s7", **switch_link_config)


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

    subprocess.call("./shared_switch.sh")

    CLI(net)
    net.stop()
