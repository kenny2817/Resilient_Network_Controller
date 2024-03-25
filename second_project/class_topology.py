from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
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


        self.FLOOD_sw = [ 2, 8 ]
        self.DIV_sw = [ 1, 3, 7, 9 ]

        self.mac_to_port = {
            1: {"00:00:00:00:00:01": 1},
            3: {"00:00:00:00:00:02": 1},
            4: {
                "00:00:00:00:00:01": 1,
                "00:00:00:00:00:03": 3,
            },
            6: {
                "00:00:00:00:00:02": 1,
                "00:00:00:00:00:04": 3,
            },
            7: {"00:00:00:00:00:03": 1},
            9: {"00:00:00:00:00:04": 1},
        }

        self.slice_ports = {
            1: {1: 2, 2: 3, 3: 3},
            3: {1: 2, 2: 3, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
            9: {1: 2, 2: 2, 3: 3},
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

        if dpid in self.mac_to_port:
            if dst in self.mac_to_port[dpid]:
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
            
            elif dpid in self.DIV_sw:
                if (pkt.get_protocol(udp.udp) and pkt.get_protocol(udp.udp).dst_port == self.slice_upper_UDPport):
                    slice_number = 1
                    out_port = self.slice_ports[dpid][slice_number]
                    match = parser.OFPMatch(
                        in_port=in_port,
                        eth_dst=dst,
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto=0x11,  # udp
                        udp_dst=self.slice_lower_UDPport,
                    )
                    actions = [parser.OFPActionOutput(out_port)]
                    self.add_flow(datapath, 10, match, actions)
                    self._send_package(msg, datapath, in_port, actions)
                    self.logger.info("UPD UP \t---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

                elif (pkt.get_protocol(udp.udp) and pkt.get_protocol(udp.udp).dst_port == self.slice_lower_UDPport):
                    slice_number = 3
                    out_port = self.slice_ports[dpid][slice_number]
                    match = parser.OFPMatch(
                        in_port=in_port,
                        eth_dst=dst,
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto=0x11,  # udp
                        udp_dst=self.slice_lower_UDPport,
                    )
                    actions = [parser.OFPActionOutput(out_port)]
                    self.add_flow(datapath, 10, match, actions)
                    self._send_package(msg, datapath, in_port, actions)
                    self.logger.info("UPD DOWN \t---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

                elif (pkt.get_protocol(udp.udp)):
                    slice_number = 2
                    out_port = self.slice_ports[dpid][slice_number]
                    match = parser.OFPMatch(
                        in_port=in_port,
                        eth_dst=dst,
                        eth_src=src,
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto=0x11,  # udp
                        udp_dst=pkt.get_protocol(udp.udp).dst_port,
                    )
                    actions = [parser.OFPActionOutput(out_port)]
                    self.add_flow(datapath, 9, match, actions)
                    self._send_package(msg, datapath, in_port, actions)
                    self.logger.info("UDP\t\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)

                elif pkt.get_protocol(tcp.tcp):
                    slice_number = 2
                    out_port = self.slice_ports[dpid][slice_number]
                    match = parser.OFPMatch(
                        in_port=in_port,
                        eth_dst=dst,
                        eth_src=src,
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto=0x06,  # tcp
                    )
                    actions = [parser.OFPActionOutput(out_port)]
                    self.add_flow(datapath, 8, match, actions)
                    self._send_package(msg, datapath, in_port, actions)
                    self.logger.info("TCP \t\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)


                elif pkt.get_protocol(icmp.icmp):
                    slice_number = 2
                    out_port = self.slice_ports[dpid][slice_number]
                    match = parser.OFPMatch(
                        in_port=in_port,
                        eth_dst=dst,
                        eth_src=src,
                        eth_type=ether_types.ETH_TYPE_IP,
                        ip_proto=0x01,  # icmp
                    )
                    actions = [parser.OFPActionOutput(out_port)]
                    self.add_flow(datapath, 7, match, actions)
                    self._send_package(msg, datapath, in_port, actions)
                    self.logger.info("ICMP\t\t ---- s%s in_port=%s out_port=%s", dpid, in_port, out_port)
