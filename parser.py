#!/usr/bin/env python
"""
    Description:
        This module responsible for Parse data from data Receiver

    Location:
        This will be at SDN.

    Configuration:

"""

PACKET_COUNT = "packets_count"
TRANSFER_SIZE = "transfer_size"
SENDER_PORT = "sport"
DEST_PORT = "dport"

NUMBER_OF_SPACES = 13;

class CongesParser:
    def __init__(self):
        pass

    def is_valed_line(self, line):
        return  len(line.splitlines()) == 1 and len(line.split(' ')) == NUMBER_OF_SPACES


    def parse_line (self, line):
        arr = line.split(' ');
        senderIP = arr[1].split(':')[0]
        senderPort  = arr[1].split(':')[1]

        receiverIP = arr[3].split(':')[0]
        receiverPort = arr[3].split(':')[1]

        t_packets_count = arr[5:10]
        t_packets_count = [int(x) for x in t_packets_count]
        t_transfer_size = int(arr[-1])
        ret = [(senderIP, receiverIP) , {PACKET_COUNT: t_packets_count, TRANSFER_SIZE: t_transfer_size, SENDER_PORT: senderPort, DEST_PORT: receiverPort}]
        return ret;

    def parse_chunck(self, chunck):
        lines = chunck.splitlines()
        # print("lines", lines)
        ret = []
        for line in lines:
            # print line.rstrip().split(' ')
            if self.is_valed_line(line):
                # print("is valid line")
                ret.append(self.parse_line(line))
        return ret


