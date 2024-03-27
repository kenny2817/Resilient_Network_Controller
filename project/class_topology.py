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


class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)

        self.FLOOD_sw = [ 1, 6 ]
        self.DIV_sw = [ 5, 7 ]
        self.QUEUE_sw = [ 3 ]
        self.DIV_QUEUE_sw = [ 2, 4 ]

        self.live_switches = set()

        self.mac_to_port = {
            2: {
                "00:00:00:00:00:01": 1,
                "00:00:00:00:00:03": 4,
            },
            4: {
                "00:00:00:00:00:02": 1,
                "00:00:00:00:00:04": 4,
            },
            5: {"00:00:00:00:00:03": 1},
            7: {"00:00:00:00:00:04": 1},
        }

        self.get_queue_id = {
            "00:00:00:00:00:01": { "00:00:00:00:00:02": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0 },
            "00:00:00:00:00:02": { "00:00:00:00:00:01": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0 },
            "00:00:00:00:00:03": { "00:00:00:00:00:04": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0 },
            "00:00:00:00:00:04": { "00:00:00:00:00:03": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0 },
        }

        self.slice_ports = {
            2: {1: 2, 2: 3, 3: 3},
            4: {1: 2, 2: 3, 3: 3},
            5: {1: 2, 2: 2, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
        }
        
        self.slice_upper_UDPport = 9999
        self.slice_lower_UDPport = 9997

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

    def udp_match(self, parser, in_port, src, dst, pkt):
        '''
        if (pkt.get_protocol(udp.udp).dst_port == self.slice_upper_UDPport
            or pkt.get_protocol(udp.udp).dst_port == self.slice_lower_UDPport):
            match = parser.OFPMatch(
                in_port=in_port,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x11,  # udp
                udp_dst=pkt.get_protocol(udp.udp).dst_port,
            )
            return match
        '''
        match = parser.OFPMatch(
            in_port=in_port,
            eth_src=src,
            eth_dst=dst,
            eth_type=ether_types.ETH_TYPE_IP,
            ip_proto=0x11,  # udp
            udp_dst=pkt.get_protocol(udp.udp).dst_port,
        )
        return match

    def set_match(self, parser, in_port, src, dst, pkt):
        if pkt.get_protocol(udp.udp):
            return self.udp_match(parser, in_port, src, dst, pkt)
        elif pkt.get_protocol(tcp.tcp):
            ip_proto = 0x06
        elif pkt.get_protocol(icmp.icmp):
            ip_proto = 0x01

        match = parser.OFPMatch(
            in_port=in_port,
            eth_src=src,
            eth_dst=dst,
            eth_type=ether_types.ETH_TYPE_IP,
            ip_proto=ip_proto,
        )
        return match


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


        if dpid in self.FLOOD_sw:
            out_port = ofproto.OFPP_FLOOD
            actions = [parser.OFPActionOutput(out_port)]
            match = parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)
            self.logger.info("FLOOD\t\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

        elif dpid in self.QUEUE_sw:
            if (src in self.get_queue_id and dst in self.get_queue_id[src] and self.get_queue_id[src][dst] != 0):
                queue_id = self.get_queue_id[src][dst]
                actions = [parser.OFPActionSetQueue(queue_id),parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
                match = self.set_match(parser, in_port, src, dst, pkt)
                self.add_flow(datapath, 10, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("QUEUE\t\t ---- s%s in_port=%s", dpid, in_port)
        
        elif dpid in self.DIV_sw:
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
                actions = [parser.OFPActionOutput(out_port)]
                match = parser.OFPMatch(eth_dst=dst)
                self.add_flow(datapath, 100, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("mac_to_port\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

            elif (pkt.get_protocol(udp.udp) and pkt.get_protocol(udp.udp).dst_port == self.slice_lower_UDPport):
                slice_number = 3
                out_port = self.slice_ports[dpid][slice_number]
                match = self.udp_match(parser, in_port, src, dst, pkt)
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
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
                actions = [parser.OFPActionOutput(out_port)]
                match = parser.OFPMatch(eth_dst=dst)
                self.add_flow(datapath, 100, match, actions)
                self._send_package(msg, datapath, in_port, actions)
                self.logger.info("mac_to_port\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

            # to queue 2
            elif (dst == "00:00:00:00:00:03" or dst == "00:00:00:00:00:04"):
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
                match = self.udp_match(parser, in_port, src, dst, pkt)
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

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_added_handler(self, ev):
        datapath = ev.msg.datapath
        dpid = datapath.id
        self.live_switches.add(dpid)
        self.logger.info("Switch %s is now connected.", dpid)

    @set_ev_cls(ofp_event.EventOFPStateChange, DEAD_DISPATCHER)
    def switch_removed_handler(self, ev):
        datapath = ev.datapath
        dpid = datapath.id
        if ev.state == DEAD_DISPATCHER:
            self.live_switches.discard(dpid)
            self.logger.info("Switch %s has disconnected.", dpid)

