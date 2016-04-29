#!/usr/bin/env python
"""
    Description:
        This module responsible for read data from monitor congestion module
        then notify the controller with all tcp sessions states

    Location:
        This will be at every host on the network.

    Configuration:
        Change the global constant to there proper value
        NOTIFY_PERIOD: number of Seconds that will be a period to notify the SDN controller
        CONGESTION_DATA_FILE: the path of the monitor congestion output (/proc/monitor_congestion)
        CONTROLLER_IP: SDN Controller IP
        CONTROLLER_PORT: SDN Controller port that corresponding for the notify server process (see notify_server.py)

"""

from __future__ import print_function

from twisted.internet import task
from twisted.internet.defer import Deferred
from twisted.internet.protocol import ClientFactory
from twisted.protocols.basic import LineReceiver

import threading

NOTIFY_PERIOD = 3.0
CONGESTION_DATA_FILE = "/proc/net/tcp"
# CONGESTION_DATA_FILE = "/proc/monitor_congestion"
CONTROLLER_IP = "localhost"
CONTROLLER_PORT = 7777


def getCongestionDataFromFile():
    conges_file = open(CONGESTION_DATA_FILE, "r")
    sessions = conges_file.readlines()
    conges_file.close()
    return sessions

class CongesNotifyClient(LineReceiver):
    def __init__(self):
        self.end = "m3a elsalama"
        self.timer = object()

    def connectionMade(self):
        self.sendCongestionData()

    def connectionLost(self,reason):
        self.timer.cancel()

    def sendCongestionData(self):

        sessions = getCongestionDataFromFile()
        print(len(sessions))
        for line in sessions:
            self.sendLine(line)

        self.timer = threading.Timer(NOTIFY_PERIOD, self.sendCongestionData)
        self.timer.start()





class CongesNotifyClientFactory(ClientFactory):
    protocol = CongesNotifyClient

    def __init__(self):
        self.done = Deferred()


    def clientConnectionFailed(self, connector, reason):
        print('connection failed:', reason.getErrorMessage())
        self.done.errback(reason)


    def clientConnectionLost(self, connector, reason):
        print('connection lost:', reason.getErrorMessage())
        self.done.callback(None)



def main(reactor):
    factory = CongesNotifyClientFactory()
    reactor.connectTCP(CONTROLLER_IP, CONTROLLER_PORT, factory)
    return factory.done



if __name__ == '__main__':
    task.react(main)
