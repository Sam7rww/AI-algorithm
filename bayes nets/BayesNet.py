import sys
from queue import Queue
from collections import OrderedDict, defaultdict


class Node:
    def __init__(self, name='', domain=[]):
        self.name = name
        self.domain = domain
        self.parents = []
        # table = {'TT':{T:0.95,F:0.05},...}
        self.table = {}

    def __str__(self):
        return self.name


class Bn:
    def __init__(self):
        self.graph = OrderedDict()

    def add_node(self, nd=Node):
        if nd in self.graph:
            return
        self.graph[nd] = []

    def add_edge(self, start=Node, end=Node):
        self.graph[start].append(end)

    def topological(self, allNodes=[]):
        result = []
        in_degree = {}
        for n in allNodes:
            in_degree[n] = 0

        for s in self.graph.keys():
            for e in self.graph[s]:
                in_degree[e] += 1

        q = Queue()
        for k in in_degree.keys():
            if in_degree[k] == 0:
                q.put(k)

        while not q.empty():
            u = q.get()
            result.append(u)
            for v in self.graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    q.put(v)

        if len(result) == len(self.graph):
            return result
        else:
            print("topological sort is wrong")


allNode = []
name_node = {}


def handle_file(file_name, bn=Bn()):
    global allNode, name_node
    bn_file = open(file_name)
    phase = 0
    prev_node = Node
    table_size = 0
    parent_cond = 0
    for line in bn_file.readlines():
        if line.strip() == "# Parents":
            phase = 1
            continue
        elif line.strip() == "# Tables":
            phase = 2
            continue

        str_list = line.split()
        if phase == 0:
            name = str_list[0].strip()
            domain = []
            for i in range(len(str_list)):
                if i == 0:
                    continue
                domain.append(str_list[i].strip())
            node = Node(name, domain)
            allNode.append(node)
            name_node[name] = node
            '''add node to graph'''
            bn.add_node(node)
        elif phase == 1:
            cur_node = Node
            for i in range(len(str_list)):
                if i == 0:
                    cur_node = name_node[str_list[i].strip()]
                else:
                    cur_node.parents.append(name_node[str_list[i].strip()])
                    '''add edge to graph, from parent to child'''
                    bn.add_edge(name_node[str_list[i].strip()], cur_node)
        elif phase == 2:
            if table_size == 0:
                # new node
                prev_node = name_node[str_list[0].strip()]
                parents = prev_node.parents
                if len(parents) == 0:
                    table_size = 1
                    parent_cond = 0
                else:
                    table_size = 1
                    for p in parents:
                        table_size *= len(p.domain)
                    parent_cond = len(parents)
            else:
                table_size -= 1
                p_provide = ""
                for i in range(parent_cond):
                    p_provide += str_list[i].strip()
                prob_sum = 0.0
                index = parent_cond
                prev_node.table[p_provide] = {}
                for i in range(len(prev_node.domain)):
                    prob = 0.0
                    if i == (len(prev_node.domain) - 1):
                        prob = round(1.0 - prob_sum, 3)
                    else:
                        prob = round(float(str_list[index].strip()), 3)
                        index += 1
                        prob_sum += prob
                    prev_node.table[p_provide].update({prev_node.domain[i]: prob})

        else:
            print("There is something wrong in reading file!")


def enumeration_ask(x, e={}, bayes=Bn()):
    global name_node, allNode
    node_x = name_node[x]
    q_x = {}
    for v in node_x.domain:
        e[x] = v
        q_x[v] = enumerate_all(bayes.topological(allNode), e)

    norm = 0.0
    for value in q_x.values():
        norm += value
    norm = 1 / norm
    for key in q_x.keys():
        q_x[key] = round(q_x[key] * norm, 3)
    return q_x


def enumerate_all(var=[], e={}):
    if len(var) == 0:
        return 1.0
    cur = var.pop(0)
    if cur.name in e.keys():
        cur_val = e[cur.name]
        pa_y = ""
        for p in cur.parents:
            pa_y += e[p.name]
        p_y = cur.table[pa_y][cur_val]
        return p_y * enumerate_all(var, e)
    else:
        pa_y = ""
        for p in cur.parents:
            pa_y += e[p.name]
        res = 0.0
        for y in cur.domain:
            p_y = cur.table[pa_y][y]
            e_new = e.copy()
            e_new[cur.name] = y
            res += p_y * enumerate_all(var.copy(), e_new)
        return res


def main():
    a = 1
    print("handle input data!")
    bn_file = sys.argv[1]
    bayes_net = Bn()
    handle_file(bn_file, bayes_net)
    '''
    for v in allNode:
        print(v)
    for v in bayes_net.topological(allNode):
        print(v.name + ";" + str(len(bayes_net.graph[v])))
    
    print("")
    for v in allNode:
        for k in v.table:
            print("key is:" + k)
            for temp in v.table[k]:
                print("var is " + temp + "; prob is " + str(v.table[k][temp]))
    '''
    print("")
    while True:
        in_str = input()
        if in_str.strip() == "quit":
            break
        str_list = in_str.split("|")
        if len(str_list) == 1:
            q_x = enumeration_ask(str_list[0].strip(), {}, bayes_net)
            str_out = ""
            for key in q_x:
                str_out += "P("+key+") = "+str(q_x[key])+", "
            print(str_out.strip()[:-1])
        else:
            evidence = str_list[1].strip().split(",")
            evi = {}
            for e in evidence:
                e_list = e.strip().split("=")
                evi[e_list[0].strip()] = e_list[1].strip()
            q_x = enumeration_ask(str_list[0].strip(), evi, bayes_net)
            str_out = ""
            for key in q_x:
                str_out += "P(" + key + ") = " + str(q_x[key]) + ", "
            print(str_out.strip()[:-1])

        print("")


if __name__ == '__main__':
    main()
