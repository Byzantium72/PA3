# Created on Oct 12, 2016

# @author: mwittie

import queue
import threading
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

    # @param dst_addr: address of the destination host
    # @param data_S: packet payload
    def __init__(self, dst_addr, data_S):
        self.dst_addr = dst_addr
        self.data_S = data_S

    # called when printing the object
    def __str__(self):
        return self.to_byte_S()

    # convert packet to a byte string for transmission over links
    def to_byte_S(self):
        byte_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        byte_S += self.data_S
        return byte_S

    # extract a packet object from a byte string
    # @param byte_S: byte string representation of the packet
    @classmethod
    def from_byte_S(cls, byte_S):
        dst_addr = int(byte_S[0: NetworkPacket.dst_addr_S_length])
        data_S = byte_S[NetworkPacket.dst_addr_S_length:]
        return cls(dst_addr, data_S)

    @staticmethod
    def segmentPacketsFromString(pkt_S, mtu):
        dst_addr = int(pkt_S[0: NetworkPacket.dst_addr_S_length])
        data_S = pkt_S[NetworkPacket.dst_addr_S_length:]

        numOfPacketsNeeded = int(math.ceil((len(pkt_S) / float(mtu))))
        # print("len(pkt_S): ", len(pkt_S))
        # print("mtu:  ", mtu)
        # print("#packetsneeded: ", numOfPacketsNeeded)
        packetsSegmented = []

        for x in range(0, numOfPacketsNeeded):
            packet = str(dst_addr).zfill(NetworkPacket.dst_addr_S_length) + data_S[(mtu - NetworkPacket.dst_addr_S_length) * x: (mtu - NetworkPacket.dst_addr_S_length) * (x + 1)]
            packetsSegmented.append(packet)

        return packetsSegmented


class IPPacket:

    dst_addr_S_length = 5
    length_S_length = 5
    fragflag_S_length = 1
    offset_S_length = 5
    id_S_length = 4

    #dst_addr + length + ID + fragflag + offset + data_S
    def __init__(self, dst_addr, data_S, ID, fragflag, offset):
        self.dst_addr = dst_addr
        self.data_S = data_S
        self.ID = ID
        self.fragflag = fragflag
        self.offset = offset

        #self.length = len(dst_addr) + len(data_S) + len(self.ID) + len(fragflag) + len(offset)

    # called when printing the object
    def __str__(self):
        return self.to_byte_S()

    @classmethod
    def from_byte_S(cls, byte_S):
        dst_addr = int(byte_S[0: IPPacket.dst_addr_S_length])
        #length = int(byte_S[IPPacket.dst_addr_S_length : IPPacket.dst_addr_S_length + IPPacket.length_S_length])
        id = int(byte_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length : IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length])
        fragflag = int(byte_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length : IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length])
        offset = int(byte_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length : IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length + IPPacket.offset_S_length])
        data_S = str(byte_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length + IPPacket.offset_S_length : ])
        return cls(dst_addr, data_S, id, fragflag, offset)

    # convert packet to a byte string for transmission over links
    def to_byte_S(self):
        dst_addr_S = str(self.dst_addr).zfill(self.dst_addr_S_length)
        length_S = str(self.dst_addr_S_length + self.length_S_length + self.id_S_length + self.fragflag_S_length + self.offset_S_length + len(self.data_S)).zfill(self.length_S_length)

        id_S = str(self.ID).zfill(self.id_S_length)
        fragflag_S = str(self.fragflag).zfill(self.fragflag_S_length)
        offset_S = str(self.offset).zfill(self.offset_S_length)

        byte_S = dst_addr_S + length_S + id_S + fragflag_S + offset_S + self.data_S
        return byte_S

    @staticmethod
    def segmentPacketsFromString(pkt_S, mtu):
        dst_addr = int(pkt_S[0: IPPacket.dst_addr_S_length])
        # length = int(byte_S[IPPacket.dst_addr_S_length : IPPacket.dst_addr_S_length + IPPacket.length_S_length])
        id = int(pkt_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length: IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length])
        offset = int(pkt_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length: IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length + IPPacket.offset_S_length])
        data_S = str(pkt_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length + IPPacket.offset_S_length:])

        data_S_length = len(data_S)
        headers = pkt_S[: IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length + IPPacket.offset_S_length]
        headers_length = len(headers)

        #numOfPacketsNeeded = int(math.ceil((len(pkt_S) / float(mtu))))
        # print("len(pkt_S): ", len(pkt_S))
        # print("mtu:  ", mtu)
        # print("#packetsneeded: ", numOfPacketsNeeded)
        packetsSegmented = []
        '''for x in range(0, numOfPacketsNeeded):
            
            newPacketData = data_S[mtu - x: (mtu - headers_length * (x + 1))]
            #packet = str(dst_addr).zfill(IPPacket.dst_addr_S_length) + data_S[(mtu - IPPacket.dst_addr_S_length) * x: (mtu - NetworkPacket.dst_addr_S_length) * (x + 1)]
            packetsSegmented.append(headers + newPacketData)
        '''
        dataAvailable = mtu - headers_length

        while data_S is not "":
            fragflag = 1
            if dataAvailable < len(data_S):
                new_data_S = data_S[:dataAvailable]
                data_S = data_S[dataAvailable:]
            else:
                new_data_S = data_S[:dataAvailable]
                data_S = data_S[dataAvailable:]
                fragflag = 0
            packet = IPPacket(dst_addr, new_data_S, id, fragflag, offset)
            offset += dataAvailable

            packetsSegmented.append(packet.to_byte_S())

        return packetsSegmented

    # dst_addr + length + ID + fragflag + offset + data_S

    def get_ID(byte_S):
        id = int(byte_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length: IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length])
        return id

    def get_fragflag(byte_S):
        fragflag = int(byte_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length : IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length])

        return fragflag

    def get_data_S(byte_S):
        data_S = str(byte_S[IPPacket.dst_addr_S_length + IPPacket.length_S_length + IPPacket.id_S_length + IPPacket.fragflag_S_length + IPPacket.offset_S_length:])
        return data_S
# Implements a network host for receiving and transmitting data
class Host:

    packetsSent = 0
    packet_S_List = []

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
    def udt_send(self, dst_addr, data_S):
        p = IPPacket(dst_addr, data_S, 0, 0, self.packetsSent)
        #fragflag, offset, id
        self.packetsSent += 1
        self.out_intf_L[0].put(p.to_byte_S())  # send packets always enqueued successfully
        print('%s: sending packet "%s" on the out interface with mtu=%d' % (self, p, self.out_intf_L[0].mtu))

    # receive packet from the network layer
    def udt_receive(self):

        new_pkt_S = ""


        pkt_S = self.in_intf_L[0].get()
        if pkt_S is not None:
            self.packet_S_List.append(pkt_S)
            if IPPacket.get_fragflag(pkt_S) is 0:
                for packet in self.packet_S_List:
                    new_pkt_S += IPPacket.get_data_S(packet)
                print('%s: received packet "%s" on the in interface' % (self, new_pkt_S))
                self.packet_S_List = []

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
    def __init__(self, name, intf_count, max_queue_size):
        self.stop = False  # for thread termination
        self.name = name
        # create a list of interfaces
        self.in_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]
        self.out_intf_L = [Interface(max_queue_size) for _ in range(intf_count)]

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
                    p = NetworkPacket.from_byte_S(pkt_S)  # parse a packet out
                    # HERE you will need to implement a lookup into the
                    # forwarding table to find the appropriate outgoing interface
                    # for now we assume the outgoing interface is also i
                    # TODO USE DICTIONARY LIBRARY
                    self.out_intf_L[i].put(p.to_byte_S(), True)
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