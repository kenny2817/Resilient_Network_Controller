from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER 
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import udp
from ryu.lib.packet import tcp
from ryu.lib.packet import icmp
from rules import EnumRules
import subprocess
import time
import threading


class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)

        # handler must be activated after the network is created
        self.switch_handler_activated = False
        # set of working switches
        self.live_switches = set()

        # variables to store the scenario
        self.switches = []
        self.exist_queue = False
        self.queue = None
        self.FLOOD_sw = []
        self.DIV_sw = []
        self.QUEUE_sw = []
        self.DIV_QUEUE_sw = []
        self.mac_to_port = {}
        self.mac_to_queue_id = {}
        self.slice_ports = {}

        # specific UDP ports for slicing
        self.slice_upper_UDPport = 9999
        self.slice_lower_UDPport = 9997

        self.logger.info("Waiting for network creation...")
        def network_creation_thread():
            # ATTENTION: you have 10 second to start the network using the comand:
            # sudo python3 network.py
            time.sleep(2)
            self.set_scenario()
            self.logger.info("Network created. Switch handlers are now active.")          

        # Create and start the thread
        thread = threading.Thread(target=network_creation_thread)
        thread.start()        
        


    def setRules(self):
        self.switches = self.scenario.value.switches
        self.exist_queue = self.scenario.value.exist_queue
        self.queue = self.scenario.value.queue

        # clear tables        
        subprocess.call("./empty_table.sh")

        # convert the set of switch numbers to a list of strings
        switch_numbers = [str(num) for num in self.switches]
        subprocess.call(["./set_controller.sh"] + switch_numbers)        

        # set drop rules to avoid unwanted communication between hosts
        subprocess.call("./set_drop_rules_table.sh")

        # if exist_queue is True, set the queue
        if self.exist_queue:
            subprocess.call(["./set_queue.sh", 
                            self.queue.switch1, 
                            self.queue.port1, 
                            self.queue.port2, 
                            self.queue.switch2, 
                            self.queue.port3, 
                            self.queue.port4, 
                            self.queue.switch3
                            ])

        # set the rules for the switches
        self.FLOOD_sw = self.scenario.value.FLOOD_sw
        self.DIV_sw = self.scenario.value.DIV_sw
        self.QUEUE_sw = self.scenario.value.QUEUE_sw
        self.DIV_QUEUE_sw = self.scenario.value.DIV_QUEUE_sw

        self.mac_to_port = self.scenario.value.mac_to_port
        self.mac_to_queue_id = self.scenario.value.mac_to_queue_id
        self.slice_ports = self.scenario.value.slice_ports
        

    # it's used as a thread with a mutex to avoid scenario creation conflicts
    def set_scenario(self):
        self.switch_handler_activated = False
        print("switch_handler_activated = False")
        # remove queue if it exists
        if self.exist_queue:
            subprocess.call(["./remove_queue.sh", 
                        self.queue.switch1, 
                        self.queue.port1, 
                        self.queue.port2, 
                        self.queue.switch2, 
                        self.queue.port3, 
                        self.queue.port4, 
                        self.queue.switch3
                        ])

        # find the scenario
        live_switches = sorted(self.live_switches)
        
        if live_switches == [1, 2, 3, 4, 5, 6, 7]:
            print("All good, registered switches: ", live_switches)
            self.scenario = EnumRules.ALL_GOOD
        elif live_switches == [2, 3, 4, 5, 6, 7]:
            print("Switch 1 is broken, registered switches: ", live_switches)
            self.scenario = EnumRules.BROKEN_SWITCH_s1
        elif live_switches == [1, 2, 4, 5, 6, 7]:
            print("Switch 3 is broken, registered switches: ", live_switches)
            self.scenario = EnumRules.BROKEN_SWITCH_s3
        elif live_switches == [1, 2, 3, 4, 5, 7]:
            print("Switch 6 is broken, registered switches: ", live_switches)
            self.scenario = EnumRules.BROKEN_SWITCH_s6
        elif live_switches == [2, 4, 5, 6, 7]:
            print("Switches 1 and 3 are broken, registered switches: ", live_switches)
            self.scenario = EnumRules.BROKEN_SWITCH_s1_s3
        elif live_switches == [2, 3, 5, 6, 7]:
            print("Switches 1 and 6 are broken, registered switches: ", live_switches)
            self.scenario = EnumRules.BROKEN_SWITCH_s1_s6
        elif live_switches == [1, 2, 4, 5, 7]:
            print("Switches 3 and 6 are broken, registered switches: ", live_switches)
            self.scenario = EnumRules.BROKEN_SWITCH_s3_s6
        else:
            print("All is broken, registered switches: ", live_switches)
            self.scenario = EnumRules.ALL_BROKEN
        
        # set rules
        self.setRules()
        self.switch_handler_activated = True
        print("switch_handler_activated = True")


    # handler for new switches
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_added_handler(self, ev):
        datapath = ev.msg.datapath
        dpid = datapath.id
        self.live_switches.add(dpid)
        self.logger.info("---------------- Switch %s is now connected ----------------", dpid)

        if self.switch_handler_activated:
            thread = threading.Thread(target=self.set_scenario)
            thread.start()

    #handler for removed switches
    @set_ev_cls(ofp_event.EventOFPStateChange, DEAD_DISPATCHER)
    def switch_removed_handler(self, ev):
        datapath = ev.datapath
        dpid = datapath.id
        if ev.state == DEAD_DISPATCHER:
            self.live_switches.discard(dpid)
            self.logger.info("---------------- Switch %s has disconnected ----------------", dpid)

            if self.switch_handler_activated:
                thread = threading.Thread(target=self.set_scenario)
                thread.start()


    # set the match for UDP-TCP-ICMP
    def set_match(self, parser, in_port, src, dst, pkt):
        if pkt.get_protocol(udp.udp):
            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x11, # udp
                udp_dst=pkt.get_protocol(udp.udp).dst_port,
            )
        else:
            if pkt.get_protocol(tcp.tcp):
                ip_proto = 0x06 # tcp
            elif pkt.get_protocol(icmp.icmp):
                ip_proto = 0x01 # icmp

            match = parser.OFPMatch(
                in_port=in_port,
                eth_src=src,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=ip_proto,
            )

        return match


    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(
                ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

    def _send_package(self, msg, datapath, in_port, actions):
        data = None
        ofproto = datapath.ofproto
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)



    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        in_port = msg.match['in_port']
        dpid = datapath.id
        parser = datapath.ofproto_parser

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src


        if dpid in self.mac_to_port and dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(eth_dst=dst)
            self.add_flow(datapath, 100, match, actions)
            self._send_package(msg, datapath, in_port, actions)
            self.logger.info("mac_to_port\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

        elif dpid in self.FLOOD_sw:
            out_port = ofproto.OFPP_FLOOD
            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)
            self.logger.info("FLOOD\t\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

        elif dpid in self.QUEUE_sw:
            if (src in self.mac_to_queue_id and dst in self.mac_to_queue_id[src] and self.mac_to_queue_id[src][dst] != 0):
                queue_id = self.mac_to_queue_id[src][dst]
                actions = [parser.OFPActionSetQueue(queue_id),parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
                match = self.set_match(parser, in_port, src, dst, pkt)
                self.add_flow(datapath, 10, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("QUEUE\t\t ---- s%s in_port=%s", dpid, in_port)
        
        elif dpid in self.DIV_sw:
            if (pkt.get_protocol(udp.udp) and pkt.get_protocol(udp.udp).dst_port == self.slice_lower_UDPport):
                slice_number = 3
                out_port = self.slice_ports[dpid][slice_number]
                match = self.set_match(parser, in_port, src, dst, pkt)
                actions = [parser.OFPActionOutput(out_port)]
                self.add_flow(datapath, 10, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("UPD DOWN \t---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

            elif (pkt.get_protocol(udp.udp)
                  or pkt.get_protocol(tcp.tcp) 
                  or pkt.get_protocol(icmp.icmp)):
                slice_number = 2
                out_port = self.slice_ports[dpid][slice_number]
                match = self.set_match(parser, in_port, src, dst, pkt)
                actions = [parser.OFPActionOutput(out_port)]
                self.add_flow(datapath, 1, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("UDP\t\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

        elif dpid in self.DIV_QUEUE_sw:
            # to queue 2
            if (dst == "00:00:00:00:00:03" or dst == "00:00:00:00:00:04"):
                queue_id = 2
                slice_number = 2
                out_port = self.slice_ports[dpid][slice_number]
                actions = [parser.OFPActionSetQueue(queue_id),parser.OFPActionOutput(out_port)]
                match = self.set_match(parser, in_port, src, dst, pkt)
                self.add_flow(datapath, 50, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("QUEUE\t\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)
            
            # to upper slice
            elif (pkt.get_protocol(udp.udp) and pkt.get_protocol(udp.udp).dst_port == self.slice_upper_UDPport):
                slice_number = 1
                out_port = self.slice_ports[dpid][slice_number]
                match = self.set_match(parser, in_port, src, dst, pkt)
                actions = [parser.OFPActionOutput(out_port)]
                self.add_flow(datapath, 10, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("UPD UP \t---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

            # to queue 1
            elif (pkt.get_protocol(udp.udp)
                  or pkt.get_protocol(tcp.tcp) 
                  or pkt.get_protocol(icmp.icmp)):
                queue_id = 1
                slice_number = 2
                out_port = self.slice_ports[dpid][slice_number]
                actions = [parser.OFPActionSetQueue(queue_id),parser.OFPActionOutput(out_port)]
                match = self.set_match(parser, in_port, src, dst, pkt)
                self.add_flow(datapath, 1, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("UDP\t\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)
