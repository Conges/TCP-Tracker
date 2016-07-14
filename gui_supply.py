import json
from pprint import pprint
import decimal

NUMBER_OF_ROUTERS = 7
ROUTER_DIST = 100
HOST_DIST = 70

packets_count = "packets_count"
transfer_size = "transfer_size"
cong_percentage = "cong_percentage"
transfer_rate = "transfer_rate"
SENDER_PORT = "sport"
DEST_PORT = "dport"
SESSIONS = "sessions"
ALL_CONG = "overall_congestion"


class GUISupply:
    def __init__(self):
        with open('cloud.json') as topology_file:
            self.topology = json.load(topology_file)
        # print(self.topology["nodes"])

    def release_topology(self):
        with open('topology.json', 'w') as fp:
            json.dump(self.topology, fp, indent=4, sort_keys=True)


    # TODO read nodes from ospf file
    def update_nodes(self):
        pass

    # TODO get hosts link from ospf file
    def append_host_links(self):
        pass

    # TODO print all sessions from analyzer map
    """

    """
    def update_sessions(self, analyzer_map):
        self.topology[SESSIONS] =[]
        all_rate = 0
        s_rate_cong = 0
        THREEPLACES = decimal.Decimal(10) ** -3
        SIXPLACES = decimal.Decimal(10) ** -6

        for key, value in analyzer_map.iteritems():
            # print "anaylyzer map value\n", value
            session = dict()
            {"congestion": 20, "rate": "12 MB/s", "rerouted": "Yes"},
            session["source_ip"] = key[0]
            session["destination_ip"] = key[1]
            session["source_port"] = value[SENDER_PORT]
            session["destination_port"] = value[DEST_PORT]

            session["congestion"] = value[cong_percentage]

            rate = value[transfer_rate] / (1024 * 1024)
            rate = str(decimal.Decimal(rate).quantize(THREEPLACES)) + " MB/s"

            all_rate += value[transfer_rate]
            s_rate_cong += (value[transfer_rate] * value[cong_percentage]) / 100
            session["rate"] = rate

            self.topology[SESSIONS].append(session)

            # TODO
            # session["rerouted"] = value[DEST_PORT]

        all_cong_indicator = s_rate_cong / all_rate
        self.topology[ALL_CONG] = str(decimal.Decimal(all_cong_indicator).quantize(SIXPLACES))
        #print(s_rate_cong , all_rate)
        #pprint(self.topology[ALL_CONG])



    def update_links(self,links_avg_cong):
        self.topology["links"] = []
        i = 0
        for key, value in links_avg_cong.iteritems():
            x ,y = int(key[0]), int(key[1])
            link = dict()

            link["source"] = x-1
            if x > 100:
                link["source"] = (x - 100) + NUMBER_OF_ROUTERS

            link["target"] = y-1
            if y > 100:
                link["target"] = (y - 100) + NUMBER_OF_ROUTERS

            if x > 100 or y > 100:
                link["dist"] = HOST_DIST
            else:
                link["dist"] = ROUTER_DIST

            link["congestion"] = int(value)
            link["id"] = i
            i += 1
            self.topology["links"].append(link)
        # pprint(self.topology["links"])

        self.append_host_links()

        self.release_topology()




if __name__ == '__main__':
    GUISupply()