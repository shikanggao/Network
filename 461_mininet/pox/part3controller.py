# Part 3 of UWCSE's Project 3
#
# based on Lab Final from UCSC's Networking Class
# which is based on of_tutorial by James McCauley

from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
import pox.lib.packet as pkt

log = core.getLogger()

# statically allocate a routing table for hosts
# MACs used in only in part 4
IPS = {
    "h10": ("10.0.1.10", '00:00:00:00:00:01'),
    "h20": ("10.0.2.20", '00:00:00:00:00:02'),
    "h30": ("10.0.3.30", '00:00:00:00:00:03'),
    "serv1": ("10.0.4.10", '00:00:00:00:00:04'),
    "hnotrust": ("172.16.10.100", '00:00:00:00:00:05'),
}


class Part3Controller(object):
    """
  A Connection object for that switch is passed to the __init__ function.
  """

    def __init__(self, connection):
        print(connection.dpid)
        # Keep track of the connection to the switch so that we can
        # send it messages!
        self.connection = connection

        # This binds our PacketIn event listener
        connection.addListeners(self)
        # use the dpid to figure out what switch is being created
        if (connection.dpid == 1):
            self.s1_setup()
        elif (connection.dpid == 2):
            self.s2_setup()
        elif (connection.dpid == 3):
            self.s3_setup()
        elif (connection.dpid == 21):
            self.cores21_setup()
        elif (connection.dpid == 31):
            self.dcs31_setup()
        else:
            print("UNKNOWN SWITCH")
            exit(1)

    def s1_setup(self):
        # put switch 1 rules here
        msg = of.ofp_flow_mod()
        msg.priority = 2
        msg.match.nw_src = IPS["hnotrust"][0]
        msg.match.dl_type = 0x800
        msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
        self.connection.send(msg)

        msg = of.ofp_flow_mod()
        msg.priority = 1
        # msg.match.dl_type = 0x800
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)

    def s2_setup(self):
        # put switch 2 rules here
        msg = of.ofp_flow_mod()
        msg.priority = 2
        msg.match.nw_src = IPS["hnotrust"][0]
        msg.match.dl_type = 0x800
        msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
        self.connection.send(msg)

        msg = of.ofp_flow_mod()
        msg.priority = 1
        # msg.match.dl_type = 0x800
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)

    def s3_setup(self):
        # put switch 3 rules here
        msg = of.ofp_flow_mod()
        msg.priority = 2
        msg.match.nw_src = IPS["hnotrust"][0]
        msg.match.dl_type = 0x800
        msg.match.nw_proto = pkt.ipv4.ICMP_PROTOCOL
        self.connection.send(msg)

        msg = of.ofp_flow_mod()
        msg.priority = 1
        # msg.match.dl_type = 0x800
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)

    def cores21_setup(self):
        # put core switch rules here
        switch_table = {'h10': 1,
                        'h20': 2,
                        'h30': 3,
                        'serv1': 4,
                        'hnotrust': 5}

        for host_name, port in switch_table.items():
            msg = of.ofp_flow_mod()
            msg.priority = 2
            msg.match.dl_type = pkt.ethernet.IP_TYPE
            msg.match.nw_dst = IPS[host_name][0]
            msg.actions.append(of.ofp_action_output(port=port))
            self.connection.send(msg)

        msg = of.ofp_flow_mod()
        msg.priority = 1
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)

        # msg = of.ofp_flow_mod()
        # msg.priority = 1
        # # msg.match.dl_type = 0x800
        # msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
        # self.connection.send(msg)

    def dcs31_setup(self):
        # put datacenter switch rules here
        msg = of.ofp_flow_mod()
        msg.priority = 2
        msg.match.nw_src = IPS["hnotrust"][0]
        msg.match.dl_type = 0x800
        self.connection.send(msg)

        msg = of.ofp_flow_mod()
        msg.priority = 1
        msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
        self.connection.send(msg)

    # used in part 4 to handle individual ARP packets
    # not needed for part 3 (USE RULES!)
    # causes the switch to output packet_in on out_port
    def resend_packet(self, packet_in, out_port):
        msg = of.ofp_packet_out()
        msg.data = packet_in
        action = of.ofp_action_output(port=out_port)
        msg.actions.append(action)
        self.connection.send(msg)

    def _handle_PacketIn(self, event):
        """
    Packets not handled by the router rules will be
    forwarded to this method to be handled by the controller
    """

        packet = event.parsed  # This is the parsed packet data.
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return

        packet_in = event.ofp  # The actual ofp_packet_in message.
        print("Unhandled packet from " + str(self.connection.dpid) + ":" + packet.dump())


def launch():
    """
  Starts the component
  """

    def start_switch(event):
        log.debug("Controlling %s" % (event.connection,))
        Part3Controller(event.connection)

    core.openflow.addListenerByName("ConnectionUp", start_switch)
