import sys
import re
import heapq
import math

cityPos = {}
cityDist = {}


def parse_city_data_file(data_file):
    city_data_regex = re.compile(r"(?P<city>^.+) "
                                 r"(?P<lat>-*\d+\.\d+) "
                                 r"(?P<lon>-*\d+\.\d+)"
                                 )

    city_distance_regex = re.compile(r"(?P<city1>^.+), "
                                     r"(?P<city2>.+): "
                                     r"(?P<dist>-?\d+.\d+)"
                                     )

    city_count = 0
    city_file = open(data_file)
    for line in city_file.readlines():
        city_result = city_data_regex.search(line)
        city_distance_result = city_distance_regex.search(line)
        if city_result != None:
            city_name = city_result.group('city')
            latitude = float(city_result.group('lat'))
            longitude = float(city_result.group('lon'))

            city_count = city_count + 1
            # print("%3d. %s is located at (latitude, longitude) = (%.2f, %.2f)" %
            #      (city_count, city_name, latitude, longitude))
            locate = [latitude, longitude]
            cityPos[city_name] = locate
        elif city_distance_result != None:
            city1_name = city_distance_result.group('city1')
            city2_name = city_distance_result.group('city2')
            distance = float(city_distance_result.group('dist'))

            # print("%s is %.2f miles from %s" % (city1_name, distance, city2_name))
            cityDist.setdefault(city1_name, []).append([city2_name, distance])
            cityDist.setdefault(city2_name, []).append([city1_name, distance])


class Node:
    """Object for storing search-tree node data.
    """

    def __init__(self, city, cost=0, h_val=0.0, parent=None):
        self.city = city
        self.cost = cost
        self.h_val = h_val
        self.parent = parent

    def __lt__(self, next_node):
        return (self.cost + self.h_val) < (next_node.cost + next_node.h_val)

    def __str__(self):
        return str(self.city)

    def isGoal(self, destination):
        return str(self) == str(destination)

    def pathCost(self, next_node, dist):
        if next_node.parent == self:
            return self.cost + dist

        return math.inf

    def A_star_val(self):
        return self.cost + self.h_val


def cal_h_value(city_cur, city_end, radius=3961):
    lat_cur = math.radians(cityPos[city_cur][0])
    lon_cur = math.radians(cityPos[city_cur][1])
    lat_end = math.radians(cityPos[city_end][0])
    lon_end = math.radians(cityPos[city_end][1])
    dlon = lon_end - lon_cur
    dlat = lat_end - lat_cur
    a = (math.pow(math.sin(dlat / 2), 2)) + math.cos(lat_cur) * math.cos(lat_end) * (math.pow(math.sin(dlon / 2), 2))
    c = 2 * (math.atan2(math.sqrt(a), math.sqrt(1 - a)))
    d = radius * c

    return d


def A_star(cityS, cityE):
    """
    :param cityS: the name of start city
    :param cityE: the name of end city
    :return: The destination Node or None
    """
    node = Node(city=cityS, cost=0, h_val=cal_h_value(cityS, cityE))
    frontier = [node]
    heapq.heapify(frontier)
    nodes_num = 1

    while frontier:
        node = heapq.heappop(frontier)
        #print("Expanding", node.city, "h_val is:", node.h_val)
        if node.isGoal(cityE):
            return node, nodes_num, len(frontier)

        next_city_list = cityDist[node.city]
        for i in range(len(next_city_list)):
            next_city = next_city_list[i][0]
            distance = next_city_list[i][1]
            h_value = cal_h_value(next_city, cityE)
            child = Node(city=next_city, cost=0, h_val=h_value, parent=node)
            child.cost = node.pathCost(child, distance)
            #print("Adding:", child.city, " h_val is:", child.h_val)
            nodes_num += 1
            heapq.heappush(frontier, child)

    return None, nodes_num, len(frontier)


def print_route(node):
    node_path = [node.city]
    parent = node.parent
    while parent != None:
        node_path.insert(0, parent.city)
        parent = parent.parent

    print("Route found: " + node_path[0], end=" ")
    for i in range(1, len(node_path)):
        print("-> " + node_path[i], end=" ")
    print("")


# Run as: python astar_search.py FILENAME
def main():
    filename = sys.argv[1]
    print("handle input data!")
    parse_city_data_file(filename)

    while True:
        start_str = input("the names of a starting city: ")
        if start_str == "0":
            break
        while start_str not in cityPos:
            start_str = input("the names of a starting city is wrong! repeat: ")

        end_str = input("the name of a goal city: ")
        if end_str == "0":
            break
        while end_str not in cityPos:
            end_str = input("the names of a goal city is wrong! repeat: ")

        print("")
        print("Searching for path from {} to {}".format(start_str, end_str))
        print("")

        result, nodes_num, frontier_num = A_star(start_str, end_str)
        if result is None:
            print("total path is -1")
        else:
            print("")
            print("Target found: {} {} {}".format(end_str, cityPos[end_str][0], cityPos[end_str][1]))
            print("")
            print_route(result)
            print("Distance: {} miles".format(result.cost))
            print("")
            print("Total nodes generated: ", nodes_num)
            print("Left in frontier: ", frontier_num)
            print("")

        print("-----------------------------")
        temp = input("Enter 0 to quit, or any other keys to search again: ")
        if temp == "0":
            break
        print("-----------------------------")

main()
