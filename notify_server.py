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


CONTROLLER_PORT = 7777

class CongesNotifyServer(Protocol):
    def dataReceived(self, data):
        print(data)

def main():
    f = Factory()
    f.protocol = CongesNotifyServer
    reactor.listenTCP(CONTROLLER_PORT, f)
    reactor.run()

if __name__ == '__main__':
    main()
