from ryu.lib.packet import ether_types
from ryu.lib.packet import udp
from ryu.lib.packet import tcp
from ryu.lib.packet import icmp
from enum import Enum

class QueueConfigurations:
    def __init__(self, switch1, port1, port2, switch2, port3, port4, switch3):
        self.switch1 = switch1
        self.port1 = port1
        self.port2 = port2
        self.switch2 = switch2
        self.port3 = port3
        self.port4 = port4
        self.switch3 = switch3

# prendere come esempio
class AllGood:
    def __init__(self):

        self.switches = [1, 2, 3, 4, 5, 6, 7]
        self.exist_queue = True
        self.queue = QueueConfigurations("s2", "eth3", "eth1", "s3", "eth2", "eth3", "s4")

        self.FLOOD_sw = [1, 6]
        self.DIV_sw = [5, 7]
        self.QUEUE_sw = [3]
        self.DIV_QUEUE_sw = [2, 4]
        
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
        
        self.mac_to_queue_id = {
            "00:00:00:00:00:01": {"00:00:00:00:00:02": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:02": {"00:00:00:00:00:01": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:03": {"00:00:00:00:00:04": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
            "00:00:00:00:00:04": {"00:00:00:00:00:03": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
        }
        
        self.slice_ports = {
            2: {1: 2, 2: 3, 3: 3},
            4: {1: 2, 2: 3, 3: 3},
            5: {1: 2, 2: 2, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
        }

# da implementare
class BrokenSwitch_s1:
    def __init__(self):
        
        self.switches = [2, 3, 4, 5, 6, 7]
        self.exist_queue = True
        self.queue = QueueConfigurations("s2", "eth3", "eth1", "s3", "eth2", "eth3", "s4")

        self.FLOOD_sw = [1, 6]
        self.DIV_sw = [5, 7]
        self.QUEUE_sw = [3]
        self.DIV_QUEUE_sw = [2, 4]
        
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
        
        self.mac_to_queue_id = {
            "00:00:00:00:00:01": {"00:00:00:00:00:02": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:02": {"00:00:00:00:00:01": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:03": {"00:00:00:00:00:04": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
            "00:00:00:00:00:04": {"00:00:00:00:00:03": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
        }
        
        self.slice_ports = {
            2: {1: 2, 2: 3, 3: 3},
            4: {1: 2, 2: 3, 3: 3},
            5: {1: 2, 2: 2, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
        }

# da implementare        
class BrokenSwitch_s3:
    def __init__(self):
        
        self.switches = [1, 2, 4, 5, 6, 7]
        self.exist_queue = True
        self.queue = QueueConfigurations("s2", "eth3", "eth1", "s3", "eth2", "eth3", "s4")

        self.FLOOD_sw = [1, 6]
        self.DIV_sw = [5, 7]
        self.QUEUE_sw = [3]
        self.DIV_QUEUE_sw = [2, 4]
        
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
        
        self.mac_to_queue_id = {
            "00:00:00:00:00:01": {"00:00:00:00:00:02": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:02": {"00:00:00:00:00:01": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:03": {"00:00:00:00:00:04": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
            "00:00:00:00:00:04": {"00:00:00:00:00:03": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
        }
        
        self.slice_ports = {
            2: {1: 2, 2: 3, 3: 3},
            4: {1: 2, 2: 3, 3: 3},
            5: {1: 2, 2: 2, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
        }

# da controllare
class BrokenSwitch_s6:
    def __init__(self):
        
        self.switches = [1, 2, 3, 4, 5, 7]
        self.exist_queue = False
        self.queue = None

        self.FLOOD_sw = [1, 3]
        self.DIV_sw = [2, 4]
        self.QUEUE_sw = []
        self.DIV_QUEUE_sw = []

        self.mac_to_port = {
            2: {
                "00:00:00:00:00:01": 1,
                "00:00:00:00:00:02": 2,
                "00:00:00:00:00:03": 4,
                "00:00:00:00:00:04": 3,
            },
            4: {
                "00:00:00:00:00:01": 2,
                "00:00:00:00:00:02": 1,
                "00:00:00:00:00:03": 3,
                "00:00:00:00:00:04": 4,
            },
            5: {
                "00:00:00:00:00:03": 1,
                "00:00:00:00:00:04": 2,
            },
            7: {
                "00:00:00:00:00:03": 2,
                "00:00:00:00:00:04": 1,
            },
        }

        self.mac_to_queue_id = {}

        self.slice_ports = {}

# da implementare
class BrokenSwitch_s1_s3:
    def __init__(self):
        
        self.switches = [2, 4, 5, 6, 7]
        self.exist_queue = True
        self.queue = QueueConfigurations("s2", "eth3", "eth1", "s3", "eth2", "eth3", "s4")

        self.FLOOD_sw = [1, 6]
        self.DIV_sw = [5, 7]
        self.QUEUE_sw = [3]
        self.DIV_QUEUE_sw = [2, 4]
        
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
        
        self.mac_to_queue_id = {
            "00:00:00:00:00:01": {"00:00:00:00:00:02": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:02": {"00:00:00:00:00:01": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:03": {"00:00:00:00:00:04": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
            "00:00:00:00:00:04": {"00:00:00:00:00:03": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
        }
        
        self.slice_ports = {
            2: {1: 2, 2: 3, 3: 3},
            4: {1: 2, 2: 3, 3: 3},
            5: {1: 2, 2: 2, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
        }

# da implementare
class BrokenSwitch_s1_s6:
    def __init__(self):
        
        self.switches = [2, 3, 5, 6, 7]
        self.exist_queue = True
        self.queue = QueueConfigurations("s2", "eth3", "eth1", "s3", "eth2", "eth3", "s4")

        self.FLOOD_sw = [1, 6]
        self.DIV_sw = [5, 7]
        self.QUEUE_sw = [3]
        self.DIV_QUEUE_sw = [2, 4]
        
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
        
        self.mac_to_queue_id = {
            "00:00:00:00:00:01": {"00:00:00:00:00:02": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:02": {"00:00:00:00:00:01": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:03": {"00:00:00:00:00:04": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
            "00:00:00:00:00:04": {"00:00:00:00:00:03": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
        }
        
        self.slice_ports = {
            2: {1: 2, 2: 3, 3: 3},
            4: {1: 2, 2: 3, 3: 3},
            5: {1: 2, 2: 2, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
        }

# da implementare
class BrokenSwitch_s3_s6:
    def __init__(self):
        
        self.switches = [1, 2, 4, 5, 7]
        self.exist_queue = True
        self.queue = QueueConfigurations("s2", "eth3", "eth1", "s3", "eth2", "eth3", "s4")

        self.FLOOD_sw = [1, 6]
        self.DIV_sw = [5, 7]
        self.QUEUE_sw = [3]
        self.DIV_QUEUE_sw = [2, 4]
        
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
        
        self.mac_to_queue_id = {
            "00:00:00:00:00:01": {"00:00:00:00:00:02": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:02": {"00:00:00:00:00:01": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:03": {"00:00:00:00:00:04": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
            "00:00:00:00:00:04": {"00:00:00:00:00:03": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
        }
        
        self.slice_ports = {
            2: {1: 2, 2: 3, 3: 3},
            4: {1: 2, 2: 3, 3: 3},
            5: {1: 2, 2: 2, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
        }

# da implementare
class AllBroken:
    def __init__(self):
        
        self.switches = [ ]
        self.exist_queue = True
        self.queue = QueueConfigurations("s2", "eth3", "eth1", "s3", "eth2", "eth3", "s4")

        self.FLOOD_sw = [1, 6]
        self.DIV_sw = [5, 7]
        self.QUEUE_sw = [3]
        self.DIV_QUEUE_sw = [2, 4]
        
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
        
        self.mac_to_queue_id = {
            "00:00:00:00:00:01": {"00:00:00:00:00:02": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:02": {"00:00:00:00:00:01": 1, "00:00:00:00:00:03": 0, "00:00:00:00:00:04": 0},
            "00:00:00:00:00:03": {"00:00:00:00:00:04": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
            "00:00:00:00:00:04": {"00:00:00:00:00:03": 2, "00:00:00:00:00:01": 0, "00:00:00:00:00:02": 0},
        }
        
        self.slice_ports = {
            2: {1: 2, 2: 3, 3: 3},
            4: {1: 2, 2: 3, 3: 3},
            5: {1: 2, 2: 2, 3: 3},
            7: {1: 2, 2: 2, 3: 3},
        }


class EnumRules(Enum):
    ALL_GOOD = "AllGood"
    BROKEN_SWITCH_s1 = "BrokenSwitch_s1"
    BROKEN_SWITCH_s3 = "BrokenSwitch_s3"
    BROKEN_SWITCH_s6 = "BrokenSwitch_s6"
    BROKEN_SWITCH_s1_s3 = "BrokenSwitch_s1_s3"
    BROKEN_SWITCH_s1_s6 = "BrokenSwitch_s1_s6"
    BROKEN_SWITCH_s3_s6 = "BrokenSwitch_s3_s6"
    ALL_BROKEN = "AllBroken"

    @property
    def value(self):
        if self._value_ == "AllGood":
            return AllGood()
        elif self._value_ == "BrokenSwitch_s1":
            return BrokenSwitch_s1()
        elif self._value_ == "BrokenSwitch_s3":
            return BrokenSwitch_s3()
        elif self._value_ == "BrokenSwitch_s6":
            return BrokenSwitch_s6()
        elif self._value_ == "BrokenSwitch_s1_s3":
            return BrokenSwitch_s1_s3()
        elif self._value_ == "BrokenSwitch_s1_s6":
            return BrokenSwitch_s1_s6()
        elif self._value_ == "BrokenSwitch_s3_s6":
            return BrokenSwitch_s3_s6()
        elif self._value_ == "AllBroken":
            return AllBroken()