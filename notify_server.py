#!/usr/bin/env python

"""
    Description:
        This module responsible for liston for tcp sessions data from all hosts(sender hosts)

    Location:
        This will be at SDN Controller

    Configuration:
        Change the global constant to there proper value
        CONTROLLER_PORT: Process port that will accept all incoming data from the server (must be the same on the host)

"""


from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor

from analyzier import CongesAnalyzer
from parser import CongesParser
from PCE_2 import PCE
from gui_supply import GUISupply
from pprint import pprint

CONTROLLER_PORT = 7777
REROUTE = "rerouted"

class CongesNotifyServer(Protocol):
    def __init__(self):
        self.parser = CongesParser()
        self.analyzer = CongesAnalyzer()
        self.sr_enable = False

    def send_stacks(self, stacks):
        for key, value in stacks.iteritems():
            line = key + ":" + str(value)+"\n"
            print(line)
            self.transport.write(line)


    def dataReceived(self, data):
        # print("data", data)
        sessions = self.parser.parse_chunck(data)
        # print "sessions" , sessions
        for i in range(len(sessions)):
            # print "session[i]", sessions[i]
            self.analyzer.add_entry(sessions[i])

        self.factory.analyzer_map.update( self.analyzer.analyzer_map)

        # check if we enable segment routing
        with open('sr_enable.in') as sr_file:
            x = sr_file.readline()
            if int(x) == 1:
                self.sr_enable = True
            else:
                print "SR not enabled"
                self.sr_enable = False

        full_stacks = []
        if self.sr_enable:
            full_stacks = self.factory.PCE.PCE_algo2(self.factory.analyzer_map)
            self.send_stacks(full_stacks)

            # print("fullstack", full_stacks)

        # see which sessions is rerouted
        for key, value in self.analyzer.analyzer_map.iteritems():
            self.analyzer.analyzer_map[key][REROUTE] = "No"
            dest_id = key[1].split('.')[3]
            # print("dest_ip", dest_id)
            if full_stacks.has_key(dest_id):
                self.analyzer.analyzer_map[key][REROUTE] = "Yes"

        self.factory.analyzer_map.update( self.analyzer.analyzer_map)
        # print("factory map", self.factory.analyzer_map)

        # Update session in GUI
        # print("in server start update session in GUI")
        self.factory.gui_supply.update_sessions(self.factory.analyzer_map)
        # pprint(self.factory.analyzer_map)

class MyFactory(Factory):
    def __init__(self):
        self.analyzer_map = dict()
        self.gui_supply = GUISupply()
        self.PCE = PCE(self.gui_supply)
        self.PCE.pce_start()


def main():
    f = MyFactory()
    f.protocol = CongesNotifyServer
    reactor.listenTCP(CONTROLLER_PORT, f)
    reactor.run()
    # print f.analyzer_map

if __name__ == '__main__':
    main()
