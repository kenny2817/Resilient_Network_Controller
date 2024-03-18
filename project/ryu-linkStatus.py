from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER 
import time
import subprocess

class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)

        time.sleep(10)
        subprocess.call(["./shared_switch.sh", "3"])
        self.live_switches = set()

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def switch_status_handler(self, ev):
        datapath = ev.datapath
        dpid = datapath.id

        if ev.state == MAIN_DISPATCHER:
            self.live_switches.add(dpid)
            self.logger.info("Switch %s is now connected.", dpid)
        elif ev.state == DEAD_DISPATCHER:
            self.live_switches.discard(dpid)
            self.logger.info("Switch %s has disconnected.", dpid)
            # Add logic to handle switch failure here

    def _check_switch_status(self, dpid):
        # Check if the switch is still live
        return dpid in self.live_switches
