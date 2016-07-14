#!/usr/bin/env python
"""
    Description:
        This module responsible for Analyze data from parser

    Location:
        This will be at SDN.

    Configuration:

"""

from __future__ import print_function

CONGESTION_STATES_WEIGHTS = [0.0, 0.2, 0.0, 0.7, 1.0]
NUMBER_OF_STATES = 5

packets_count = "packets_count"
transfer_size = "transfer_size"
cong_percentage = "cong_percentage"
transfer_rate = "transfer_rate"
SENDER_PORT = "sport"
DEST_PORT = "dport"

NOTIFY_PERIOD = 2.0


def take_average(x, y):
    return (x+y)/2


def arr_to_s(arr):
    return ', '.join(str(x) for x in arr)


class CongesAnalyzer:
    def __init__(self):
        """
            analyzer_map is a dict()
                key: pair(senderIP, receiverIP)
                value: dict()
                    packets_count: count of packet in every state
                    transfer_size: number of bytes sent between the two machines
                    cong_percentage: congestion percentage till now
                    transfer_rate: transfer rate till now

        :return:
        """
        self.analyzer_map = dict()
    def calc_congestion_percentage(self, arr):
        t_cong_percentage = 0
        for i in range(NUMBER_OF_STATES):
            t_cong_percentage += arr[i] * CONGESTION_STATES_WEIGHTS[i]
        return -1 if sum(arr) == 0 else t_cong_percentage * 100 / sum(arr)

    def add_entry(self, entry):
        """

        :param entry:dict()
            key: pair(senderIP, receiverIP)
            value: dict()
                packets_count: count of packet in every state
                transfer_size: number of bytes sent between the two machines

        :return:
        """
        # print("in add entry")
        key = entry[0]

        if self.analyzer_map.has_key(key):
            current_value = self.analyzer_map[entry[0]]

            # Calculate new congestion percentage
            new_packets_count = []
            # print(arr_to_s(entry[1][packets_count]) + " " +arr_to_s(current_value[packets_count]))
            for i in range(NUMBER_OF_STATES):
                if entry[1][packets_count][i] < current_value[packets_count][i]:
                    raise ValueError("packets count received less than saved: received = " + entry[packets_count].to_s + "saved = " + current_value[packets_count].to_s )
                new_packets_count.append(entry[1][packets_count][i] - current_value[packets_count][i])

            t_cong_percentage = self.calc_congestion_percentage(new_packets_count)

            # Take average of congestion Percentage
            if t_cong_percentage != -1:
                t_cong_percentage = take_average(t_cong_percentage, current_value[cong_percentage])
            else:
                t_cong_percentage = current_value[cong_percentage]

            # Calculate new transfer rate
            if entry[1][transfer_size] < current_value[transfer_size]:
                raise ValueError("transfer received less than saved: received = " + entry[transfer_size].to_s + "saved = " + current_value[transfer_size].to_s )

            t_transfer_rate = (entry[1][transfer_size] - current_value[transfer_size]) / NOTIFY_PERIOD

            # Take average of transfer rate
            t_transfer_rate = take_average(t_transfer_rate, current_value[transfer_rate])

            value = {packets_count: entry[1][packets_count], transfer_size: entry[1][transfer_size],
                     cong_percentage: t_cong_percentage, transfer_rate: t_transfer_rate,
                     SENDER_PORT: entry[1][SENDER_PORT], DEST_PORT: entry[1][DEST_PORT]}

            self.analyzer_map[key] = value
        else:
            # print("first time")
            t_cong_percentage = self.calc_congestion_percentage(entry[1][packets_count])
            t_transfer_rate = entry[1][transfer_size] / NOTIFY_PERIOD

            value = {packets_count: entry[1][packets_count], transfer_size: entry[1][transfer_size],
                     cong_percentage: t_cong_percentage, transfer_rate: t_transfer_rate,
                     SENDER_PORT: entry[1][SENDER_PORT], DEST_PORT: entry[1][DEST_PORT]}
            self.analyzer_map[key] = value
            # print(self.analyzer_map[key])
        # print("in anaylizer", self.analyzer_map[key])

# test script

# entry = [("192.168.1.10", "192.168.1.4"), {"packets_count": [0, 0, 0, 5, 5], "transfer_size" : 100} ]
# c = CongesAnalyzer()
# c.add_entry(entry)
# entry = [("192.168.1.10", "192.168.1.4"), {"packets_count": [0, 0, 0, 5, 10], "transfer_size" : 300} ]
# c.add_entry(entry)
#
# entry = [("192.168.1.3", "192.168.1.4"), {"packets_count": [0, 0, 0, 5, 5], "transfer_size" : 100} ]
# c.add_entry(entry)
#
# entry = [("192.168.1.3", "192.168.1.4"), {"packets_count": [0, 0, 0, 5, 10], "transfer_size" : 300} ]
# c.add_entry(entry)
# entry = [("192.168.1.3", "192.168.1.4"), {"packets_count": [0, 0, 0, 5, 10], "transfer_size" : 300} ]
# c.add_entry(entry)
# entry = [("192.168.1.3", "192.168.1.4"), {"packets_count": [0, 0, 0, 5, 10], "transfer_size" : 300} ]
# c.add_entry(entry)
# entry = [("192.168.1.3", "192.168.1.4"), {"packets_count": [0, 0, 0, 5, 10], "transfer_size" : 300} ]
# c.add_entry(entry)
