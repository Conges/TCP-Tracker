from collections import defaultdict, deque
import copy
import threading
from our_graph import Graph
from gui_supply import GUISupply

NOTIFY_PERIOD = 3.0
packets_count = "packets_count"
transfer_size = "transfer_size"
cong_percentage = "cong_percentage"
transfer_rate = "transfer_rate"


class PCE:
    def __init__(self):
        self.pce_timer = object()
        self.analyzer_map = dict()
        self.sdn_network = 77
        self.full_stacks = dict()
        self.CONGESTON_LIMIT = 90
        self.d2 = defaultdict(list)
        self.links_avg_cong = dict()  # Contains average percentage for all links
        self.gui_supply = GUISupply()


    def fake_analyzer_map(self):
        self.analyzer_map.clear()
        self.analyzer_map[('192.168.1.101', '192.168.5.107')] = {'cong_percentage': 95.714285714285714,
                                        'packets_count': [33, 0, 0, 0, 2],
                                        'transfer_rate': 4.784531073161735,
                                        'transfer_size': 6171}
        self.analyzer_map[('192.168.1.101', '192.168.1.108')] = {'cong_percentage': 91.0,
                                        'packets_count': [85, 0, 0, 0, 0],
                                        'transfer_rate': 6.408061792202518,
                                        'transfer_size': 8265}


    def PCE_algo2(self,  _analyzer_map):
        print "in pce algo 2"
        self.analyzer_map = _analyzer_map

        # TODO work on real congestion data
        self.fake_analyzer_map()


        # f4 = open('test_congestion_2','r')
        a4 = []
        d4 = dict()

        for key, value in self.analyzer_map.iteritems():
            t4 = (self.ip_to_id(key[0]), self.ip_to_id(key[1]))
            # print(t4)
            # print(value)
            rate = int(value[transfer_rate])
            ratio = int(value[cong_percentage])
            d4[t4] = (rate,ratio)
            # print(d4[t4])
            if int(ratio) > self.CONGESTON_LIMIT:
                print "There is a congestion between ", str(key)
                a4.append(t4)


        for tup in self.a1:
            # print tup
            # print self.d2[tup]
            z = 0.0
            for k in self.d2[tup]:
                x = 0.0
                if(d4.has_key(k)):
                    x = float(d4[k][1])
                    z += x
            self.links_avg_cong[tup] = z / self.d1[tup]
        # print self.links_avg_cong

        self.gui_supply.print_topology(self.links_avg_cong)
        # return
        # Accumulating all the ratio*rate between all sources and destinations for all links
        for tup in a4:
            g2 = copy.deepcopy(self.g)
            _,tmp2 = self.g.shortest_path(tup[0],tup[1])
            print 'old SP', tmp2
            a6 = []
            for k in range (1,len(tmp2)-2):
                t3 = (tmp2[k],tmp2[k+1])
                # print self.d2[t3],'d2'
                a5=[]
                y = 0.0

                for j in self.d2[t3]:
                    x = 0
                    if(d4.has_key(j)):
                        x = float(d4[j][0]) * float(d4[j][1]) / 100
                    y = y + x
                    a5.append(x)
                    # print d4[j]
                a6.append(y)
            # print a6 , 'a6'
            la = a6[0]
            index = 0
            ind = []
            if len(a6) > 1:
                for e in range (1,len(a6)):
                    if a6[e] > la:
                        la = a6[e]
                        index = e

            for e in range (0,len(a6)):
                if a6[e] > 1000.0:
                    ind.append(e)

            if len(ind) == 0:
                g2.edges[tmp2[index+2]] = [x for x in g2.edges[tmp2[index+2]] if not (x == tmp2[index+1])]
                g2.edges[tmp2[index+1]] = [x for x in g2.edges[tmp2[index+1]] if not (x == tmp2[index+2])]
            else:
                for i in ind:
                    g2.edges[tmp2[i+2]] = [x for x in g2.edges[tmp2[i+2]] if not (x == tmp2[i+1])]
                    g2.edges[tmp2[i+1]] = [x for x in g2.edges[tmp2[i+1]] if not (x == tmp2[i+2])]

            _,tmp3 = g2.shortest_path(tup[0],tup[1])
            print 'new SP', tmp3
            print 'The new stack of labels for the path between ',tup[0],' and ',tup[1]
            ret_val = []
            for items in tmp3:
                if items not in tmp2:
                    print items
                    ret_val.append(items)

            tmp_stack = tmp3[1:-1]
            for i in range(0,len(tmp_stack)):
                tmp_stack[i] = self.id_to_label(tmp_stack[i])
                # print(tmp_stack[i])
            self.full_stacks[tmp3[-1]] = tmp_stack
        # print(self.full_stacks)
        # self.pce_timer = threading.Timer(NOTIFY_PERIOD, self.PCE_algo2, (a4_src, a5, g, d2, ))
        # self.pce_timer.start()
        return self.full_stacks


    def pce_start(self,):
        print("in PCE start")
        g = Graph()

        #input files
        f1 = open('test_graph','r')
        f2 = open('shortest_paths','w')
        f3 = open('links','w')
        f5 = open('modified_paths','w')

        # Declarations of arrays and dictionaries
        a1 = []  # Contains tuples of all edges
        d1 = defaultdict(int)  # Counts how many times each edge occurs in all shortest paths
        a2 = []  # Contains tuples of all edges with source and destination of each one of them
        d2 = defaultdict(list)  # contains all sources and destinations of each link
        a4 = []  # Contains tuples of all sources and destinations
        # d4 = {}  # Mapping all sources and destinations to their ratios and rates
        a5 = []  # Accumulating all the ratio*rate between all sources and destinations for all links

        # Add all edges to the graph
        for line in f1:
            l = line.split()
            #for hosts h0-h7
            # if l[0][0] == 'h':
            #     g.add_edge(l[0],l[1][0])
            # elif l[1][0] == 'h':
            #     g.add_edge(l[0][0],l[1])
            # #for routers in the middle
            # else:
            if l[0].find('.') != -1:
                l[0] = l[0][0]
            if l[1].find('.') != -1:
                l[1] = l[1][0]
            g.add_edge(l[0],l[1])

        # Get all shortest paths from all nodes to all destinations
        for n in g.nodes:
            for node in g.nodes:
                if len(node) == 3 and len(n) == 3:
                    if n != node:
                        l,path = g.shortest_path(n,node)
                        # print>>f2, path
                        for item in path:
                                f2.write("%s " % item)
                        f2.write('\n')
        f2.flush()


        #find the sources and the destinations passing by all links of shortest paths

        f2 = open('shortest_paths','r')
        for line in f2:
            ln = line.split()
            # print>>f3,ln
            for i in range (1,len(ln)-2):
                t1 = (ln[i],ln[i+1])
                t2 = (ln[i],ln[i+1],ln[0],ln[len(ln)-1])
                a1.append(t1)
                a2.append(t2)
                print>>f3,t2

        # Count how many times each edge occurs in all shortest paths
        # collecting all sources and destinations of each link together

        for k in a1:
            d1[k] += 1
        for t21,t22,t23,t24 in a2:
            d2[(t21,t22)].append((t23,t24))

        self.a1 = a1
        self.a4 = a4
        self.g = g
        self.d2 = d2
        self.d1 = d1

        # self.PCE_algo2(a4, a5, g, d2)


    def ip_to_id(self, ip):
        if(int(ip.split('.')[3]) > 100):
            return ip.split('.')[3]
        return ip.split('.')[3] + '.' + ip.split('.')[3] + '.' + ip.split('.')[3] + '.' + ip.split('.')[3]


    def host_id_to_ip(self, id):
        ip = "192.168." + self.sdn_network + "." + id
        return ip

    def id_to_label(self,id):
        return id+id+id



if __name__ == '__main__':
    pce_obj = PCE()
    analyzer_map = dict()
    analyzer_map[('192.168.1.101', '192.168.5.107')] = {'cong_percentage': 95.714285714285714,
                                    'packets_count': [33, 0, 0, 0, 2],
                                    'transfer_rate': 4.784531073161735,
                                    'transfer_size': 6171}
    analyzer_map[('192.168.1.101', '192.168.1.108')] = {'cong_percentage': 91.0,
                                    'packets_count': [85, 0, 0, 0, 0],
                                    'transfer_rate': 6.408061792202518,
                                    'transfer_size': 8265}
    pce_obj.pce_start()
    pce_obj.PCE_algo2(analyzer_map)
