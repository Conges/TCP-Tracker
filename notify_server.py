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
from pprint import pprint

CONTROLLER_PORT = 7777

class CongesNotifyServer(Protocol):
    def __init__(self):
        self.parser = CongesParser()
        self.analyzer = CongesAnalyzer()

    def dataReceived(self, data):
        sessions = self.parser.parse_chunck(data)
        for i in range(len(sessions)):
            # print sessions[i]
            self.analyzer.add_entry(sessions[i])
        self.factory.analyzer_map = self.analyzer.analyzer_map
        pprint(self.factory.analyzer_map)

class MyFactory(Factory):
    def __init__(self):
        self.analyzer_map = dict()



def main():
    f = MyFactory()
    f.protocol = CongesNotifyServer
    reactor.listenTCP(CONTROLLER_PORT, f)
    reactor.run()
    # print f.analyzer_map

if __name__ == '__main__':
    main()
