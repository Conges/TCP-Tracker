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
REROUTE = "rerouted"


class GUISupply:
    def __init__(self):
        # with open('cloud.json') as topology_file:
        #     self.topology = json.load(topology_file)
        self.topology = dict()
        self.nodes_position = self.get_nodes_positions()

        # print(self.topology["nodes"])

    # dict node_id: (x,y)
    def get_nodes_positions(self):
        nodes_position = dict()
        with open('cloud3.json') as topology_file:
            tmp_topology = json.load(topology_file)
            for node in tmp_topology["nodes"]:
                node_id = node["name"][1:]
                if node["name"][0] != 'R':
                    node_id = str(int(node["name"][1:]) + 100)
                nodes_position[node_id] = (node["x"] ,node["y"])
            return nodes_position



    def release_topology(self):
        with open('our_topology.json', 'w') as fp:
            json.dump(self.topology, fp, indent=4, sort_keys=True)


    def update_nodes(self):
        nodes = []
        with open('graph.txt') as topology_file:
            positions = self.get_nodes_positions()
            # pprint(positions)
            for i, line in enumerate(topology_file):
                if len(line) < 2:
                    continue
                line = line.split()
                src = line[0].split('.')
                ip = line[3]
                nodes = self.add_node(positions, nodes, src, ip, i)
                src = line[1].split('.')
                ip = ''
                nodes = self.add_node(positions, nodes, src, ip, NUMBER_OF_ROUTERS*3 + i)
        # pprint(nodes)
        self.topology["nodes"] = nodes



    def add_node(self, positions, nodes, src, ip, i):
        # print(i , src , ip)
        router = True
        id = src[3]
        if int(id) > 100:
            router = False
        if router:
            ind = ''
            if any(d["name"] == "R"+id   for d in nodes):
                ind = next(index for (index, d) in enumerate(nodes) if d["name"] == "R"+id)
            # print "ind" ,  ind
            if ind != '' and ip != '':
                # pprint(nodes)
                if(nodes[ind].has_key("interfaces")):
                    iface_len = len(nodes[ind]["interfaces"])+1
                    iface = "eth"+ str(iface_len)
                    nodes[ind]["interfaces"].append({"iface": iface, "ip": ip})
                else:
                    nodes[ind]["interfaces"] = [{"iface": "eth1", "ip": ip}]

                return nodes
        if not router and any(d['name'] == 'H'+str(int(id) - 100) for d in nodes):
            return nodes

        node = dict()
        if router:
            node["name"] = 'R'+id
            node["type"] = "router"
            node["group"] = int(id) - 1
            node["protocol"] = "OSPF"
            if(ip != ''):
                node["interfaces"] = [{"iface": "eth1", "ip": ip}]
        else:
            node["name"] = 'H'+str(int(id) - 100)
            node["type"] = "host"
            node["group"] = NUMBER_OF_ROUTERS + int(id) - 100
        node["id"] = i
        node["x"] = 200
        node["y"] = 200
        if positions.has_key(id):
            node["x"] = positions[id][0]
            node["y"] = positions[id][1]
        nodes.append(node)
        return nodes


    def append_host_links(self):
        links = []
        with open('graph.txt') as topology_file:
            for i, line in enumerate(topology_file):
                if len(line) < 2:
                    continue
                line = line.split()
                router_id = ''
                host_id = ''
                if int(line[0].split('.')[3]) > 100:
                    host_id = line[0].split('.')[3]
                else:
                    router_id = line[0].split('.')[3]

                if int(line[1].split('.')[3]) > 100:
                    host_id = line[1].split('.')[3]
                else:
                    router_id = line[1].split('.')[3]

                if(host_id == ''):
                    # print "no host" , line
                    continue
                link = dict()
                link["congestion"] = 0
                link["dist"] = HOST_DIST
                link["id"] = 100 + i
                link["source"] = self.get_node_group(router_id)
                link["target"] = self.get_node_group(host_id)
                links.append(link)
        # pprint(links)
        self.topology["links"].append(links)

    def get_node_group(self, id):
        router = True
        if int(id) > 100:
            router = False
        name = "R"+id
        if not router:
            name = "H" + str(int(id)-100)
        for node in self.topology["nodes"]:
            if node["name"] == name:
                return node["group"]
        raise "Cannot find node with id = ", id

    def update_sessions(self, analyzer_map):
        self.topology[SESSIONS] =[]
        all_rate = 0
        s_rate_cong = 0
        THREEPLACES = decimal.Decimal(10) ** -3
        SIXPLACES = decimal.Decimal(10) ** -6

        for key, value in analyzer_map.iteritems():
            # print "anaylyzer map value\n", value
            session = dict()
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

            session[REROUTE] = value[REROUTE]

            self.topology[SESSIONS].append(session)

        # Sort sessions
        self.topology[SESSIONS] = sorted(self.topology[SESSIONS], reverse=True,
                                         key=lambda k: float(k['rate'].split()[0]) * int(k["congestion"]))
        # pprint(self.topology[SESSIONS])

        all_cong_indicator = 0
        if all_rate != 0:
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

        self.append_host_links()
        # pprint(self.topology["links"])
        #
        # self.release_topology()




if __name__ == '__main__':
    gui_supply = GUISupply()
    gui_supply.update_nodes()
