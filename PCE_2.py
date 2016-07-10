from collections import defaultdict, deque
import copy
import threading
from our_graph import Graph

NOTIFY_PERIOD = 3.0


class PCE:
    def __init__(self):
        self.pce_timer = object()

    def PCE_algo2(self, a4, a5, d4, g, d2):

        f4 = open('test_congestion_2','r')
        a4_src = copy.deepcopy(a4)
        for line in f4:
            l = line.split()
            src = l[0]
            dst = l[1]
            t4 = (src,dst)
            rate = l[2]
            ratio = l[3]
            d4[t4] = (rate,ratio)
            if int(ratio) > 90:
                print "There is a congestion between ", src , " and " , dst
                a4.append(t4)

        # Accumulating all the ratio*rate between all sources and destinations for all links

        for tup in a4:
            g2 = copy.deepcopy(g)
            _,tmp2 = g.shortest_path(tup[0],tup[1])
            print 'old SP', tmp2
            a6 = []
            for k in range (1,len(tmp2)-2):
                t3 = (tmp2[k],tmp2[k+1])
                # print d2[t3]
                a5=[]
                y = 0.0
                for j in d2[t3]:
                    x = float(d4[j][0]) * float(d4[j][1]) / 100
                    y = y + x
                    a5.append(x)
                    # print d4[j]
                a6.append(y)
            # print a6
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

            for i in ind:
                g2.edges[tmp2[i+2]] = [x for x in g2.edges[tmp2[i+2]] if not (x == tmp2[i+1])]
                g2.edges[tmp2[i+1]] = [x for x in g2.edges[tmp2[i+1]] if not (x == tmp2[i+2])]
            # g2.edges[tmp2[index+2]] = [x for x in g2.edges[tmp2[index+2]] if not (x == tmp2[index+1])]
            # g2.edges[tmp2[index+1]] = [x for x in g2.edges[tmp2[index+1]] if not (x == tmp2[index+2])]
            _,tmp3 = g2.shortest_path(tup[0],tup[1])
            print 'new SP', tmp3
            print 'The new stack of labels for the path between ',tup[0],' and ',tup[1]
            ret_val = []
            for items in tmp3:
                if items not in tmp2:
                    print items
                    ret_val.append(items)

            self.pce_timer = threading.Timer(NOTIFY_PERIOD, self.PCE_algo2, (a4_src, a5, d4, g, d2, ))
            self.pce_timer.start()
            return tmp3[1:-1]
            #return ret_val

    def pce_start(self):

        g = Graph()


        #input files
        f1 = open('test_graph','r')
        f2 = open('shortest_paths','w')
        f3 = open('links','w')
        f5 = open('modified_paths','w')

        # Declarations of arrays and dictionaries
        a1 = []  # Contains tuples of all edges
        d1 = defaultdict(int) #counts how many times each edge occurs in all shortest paths
        a2 = []  # Contains tuples of all edges with source and destination of each one of them
        d2 = defaultdict(list) #contains all sources and destinations of each link
        a4 = []  # Contains tuples of all sources and destinations
        d4 = {}  # Mapping all sources and destinations to their ratios and rates
        a5 = []  # Accumulating all the ratio*rate between all sources and destinations for all links


        # Add all edges to the graph
        for line in f1:
            l = line.split()
            #for hosts h0-h7
            if l[0][0] == 'h':
                g.add_edge(l[0],l[1][0])
            elif l[1][0] == 'h':
                g.add_edge(l[0][0],l[1])
            #for routers in the middle
            else:
                g.add_edge(l[0][0],l[1][0])


        # Get all shortest paths from all nodes to all destinations
        for n in g.nodes:
            for node in g.nodes:
                if node[0] == 'h' and n[0] == 'h':
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
        # print d2

        # reading all congestion states and finds if there any ration above 90
        print self.PCE_algo2(a4, a5, d4, g, d2)



if __name__ == '__main__':
    pce_obj = PCE()
    pce_obj.pce_start()