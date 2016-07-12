import json
from pprint import pprint

NUMBER_OF_ROUTERS = 7
ROUTER_DIST = 100
HOST_DIST = 70


class GUISupply:
    def __init__(self):
        with open('cloud.json') as topology_file:
            self.topology = json.load(topology_file)
        print(self.topology["nodes"])

    def print_topology(self, links_avg_cong):
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
        with open('topology.json', 'w') as fp:
            json.dump(self.topology, fp, indent=4, sort_keys=True)



if __name__ == '__main__':
    GUISupply()