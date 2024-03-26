from socket import ETHERTYPE_ARP
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4

class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)
        self.mac_to_port = {
            "10.0.0.1": 1,
            "10.0.0.2": 2,
            "10.0.0.3": 3,
            "10.0.0.4": 4,
        }
        self.slice_queues = {
            1: 1,
            2: 2,
        }

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

        # Configure queues
        self.configure_queues(datapath)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

    def configure_queues(self, datapath):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Configure queues for each port
        for port, queue_id in self.slice_queues.items():
            actions = [parser.OFPActionSetQueue(queue_id)]
            queue_config = parser.OFPQueueConfig(
                datapath=datapath,
                port=port,
                queues=[parser.OFPQueueConfigProps(
                    prop=ofproto.OFPQT_MAX_RATE,
                    rate=5000000  # Specify max rate for the queue in bps (5 Mbps)
                )]
            )
            datapath.send_msg(queue_config)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)

        if eth.ethertype == ETHERTYPE_ARP.ETH_TYPE_IP and ipv4_pkt:
            src_ip = ipv4_pkt.src
            dst_ip = ipv4_pkt.dst

            if src_ip in self.mac_to_port and dst_ip in self.mac_to_port:
                src_port = self.mac_to_port[src_ip]
                dst_port = self.mac_to_port[dst_ip]
                slice_queue = self.slice_queues[src_port]

                actions = [parser.OFPActionOutput(dst_port)]
                match = parser.OFPMatch(
                    eth_type=ETHERTYPE_ARP.ETH_TYPE_IP,
                    ipv4_src=src_ip,
                    ipv4_dst=dst_ip
                )

                self.add_flow(datapath, 1, match, actions)
                actions.append(parser.OFPActionSetQueue(slice_queue))
                out = parser.OFPPacketOut(
                    datapath=datapath,
                    buffer_id=msg.buffer_id,
                    in_port=in_port,
                    actions=actions,
                    data=msg.data
                )
                datapath.send_msg(out)
