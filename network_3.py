# Created on Oct 12, 2016

# @author: mwittie

import queue
import math
import threading


# wrapper class for a queue of packets
class Interface:
    # @param maxsize - the maximum size of the queue storing packets
    def __init__(self, maxsize=0):
        self.queue = queue.Queue(maxsize)
        self.mtu = None

    # get packet from the queue interface
    def get(self):
        try:
            return self.queue.get(False)
        except queue.Empty:
            return None

    # put the packet into the interface queue
    # @param pkt - Packet to be inserted into the queue
    # @param block - if True, block until room in queue, if False may throw queue.Full exception
    def put(self, pkt, block=False):
        self.queue.put(pkt, block)


# Implements a network layer packet (different from the RDT packet
# from programming assignment 2).
# NOTE: This class will need to be extended to for the packet to include
# the fields necessary for the completion of this assignment.
class NetworkPacket:
    # packet encoding lengths
    dst_addr_S_length = 5
    src_addr_S_length = 5

    # @param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, src_addr, data_S):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.src_addr = src_addr

    # called when printing the object
    def __str__(self):
        return self.to_byte_S()

    # convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += str(self.src_addr).zfill(self.src_addr_S_length)
        byte_S += self.data_S
        return byte_S

    # extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(cls, byte_S):
        dst_addr = int(byte_S[0: NetworkPacket.dst_addr_S_length])
        src_addr = int(byte_S[NetworkPacket.dst_addr_S_length : NetworkPacket.dst_addr_S_length + NetworkPacket.src_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length + NetworkPacket.src_addr_S_length :]
        return cls(dst_addr, src_addr, data_S)

    @staticmethod
    def segmentPacketsFromString(pkt_S, mtu):

        dst_addr = int(pkt_S[0: NetworkPacket.dst_addr_S_length])
        src_addr = int(pkt_S[NetworkPacket.dst_addr_S_length: NetworkPacket.dst_addr_S_length + NetworkPacket.src_addr_S_length])
        data_S = pkt_S[NetworkPacket.dst_addr_S_length + NetworkPacket.src_addr_S_length:]
        headers = pkt_S[: NetworkPacket.dst_addr_S_length + NetworkPacket.src_addr_S_length]
        headers_length = len(headers)
        dataAvailable = mtu - headers_length

        packetsSegmented = []
        while data_S is not "":
            if dataAvailable < len(data_S):
                new_data_S = data_S[:dataAvailable]
                data_S = data_S[dataAvailable:]
            else:
                new_data_S = data_S[:dataAvailable]
                data_S = data_S[dataAvailable:]

            packet = NetworkPacket(dst_addr, src_addr, new_data_S)

            packetsSegmented.append(packet.to_byte_S())

        return packetsSegmented


# Implements a network host for receiving and transmitting data
class Host:

    # @param addr: address of this node represented as an integer
    def __init__(self, addr):
        self.addr = addr
        self.in_intf_L = [Interface()]
        self.out_intf_L = [Interface()]
        self.stop = False  # for thread termination

    # called when printing the object
    def __str__(self):
        return 'Host_%s' % self.addr

    # create a packet and enqueue for transmission
    # @param dst_addr: destination address for the packet
    # @param data_S: data being transmitted to the network layer
    def udt_send(self, dst_addr, src_addr, data_S):
        p = NetworkPacket(dst_addr, src_addr, data_S)
        self.out_intf_L[0].put(p.to_byte_S())  # send packets always enqueued successfully
        print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    # receive packet from the network layer
    def udt_receive(self):
        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            print('%s: received packet "%s" on the in interface' % (self, pkt_S))

    # thread target for the host to keep receiving data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            # receive data arriving to the in interface
            self.udt_receive()
            # terminate
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return


# Implements a multi-interface router described in class
class Router:

    # @param name: friendly router name for debugging
    # @param intf_count: the number of input and output interfaces
    # @param max_queue_size: max queue length (passed to Interface)
    def __init__(self, name, intf_count, max_queue_size, routing_table):
        self.stop = False  # for thread termination
        self.name = name
        # create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.routing_table = routing_table

    # called when printing the object
    def __str__(self):
        return 'Router_%s' % self.name

    # look through the content of incoming interfaces and forward to
    # appropriate outgoing interfaces
    def forward(self):
        for i in range(len(self.in_intf_L)):
            pkt_S = None
            try:
                # get packet from interface i
                pkt_S = self.in_intf_L[i].get()
                # if packet exists make a forwarding decision
                if pkt_S is not None:
                    p = NetworkPacket.from_byte_S(pkt_S)
                    # parse a packet out
                    # HERE you will need to implement a lookup into the
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
                    # TODO USE DICTIONARY LIBRARY
                    self.out_intf_L[self.routing_table[p.src_addr]].put(p.to_byte_S(), True)
                    # self.out_intf_L[i].put(p.to_byte_S(), True)
                    print('%s: forwarding packet "%s" from interface %d to %d with mtu %d'
                          % (self, p, i, i, self.out_intf_L[i].mtu))
            except queue.Full:
                print('%s: packet "%s" lost on interface %d' % (self, p, i))
                pass

    # thread target for the host to keep forwarding data
    def run(self):
        print(threading.currentThread().getName() + ': Starting')
        while True:
            self.forward()
            if self.stop:
                print(threading.currentThread().getName() + ': Ending')
                return
