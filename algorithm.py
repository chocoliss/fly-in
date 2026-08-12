from math import sqrt

class Dijkstra:
    def __init__(self, zones: dict, metadic: dict, connections: list, meta_connection_dic: dict):
        self.zones = zones
        self.metadic = metadic
        self.connections = connections
        self.meta_connection_dic = meta_connection_dic
        self.visited = []
        self.unvisited = []
        self.path = {}
        self.previous_point = {}
        self.points_available = {}
        self.point_cost = {}

    def path_finding(self) -> None:
        # for connection in self.connections:
        #     a, b = connection.split('-')
        #     print(f"connection: {connection} where {a}:{self.zones[a]} and {b}:{self.zones[b]}")
        #     print(f"The distance between them is {self.cost(self.zones[a], self.zones[b])}")
        start = list(self.zones.keys())[0]
        for point in self.zones:
            self.parse_connections(point)
            if point == start:
                self.point_cost[point] = 0

            else:
                self.point_cost[point] = 2147483647
            self.unvisited.append(point)

        for point in self.zones:
            # print(point)
            # lst = sorted(self.points_available[point],key=lambda x: self.cost(self.zones[point], self.zones[x]))
            # print(lst)
            dic = {}
            print(f"the point is {point}")
            for available in self.points_available[point]:
                print(f"the point available {available}")
                if available in self.visited:
                    print(f"pass {available}")
                    continue
                value = self.cost(self.zones[available],self.zones[point]) + self.point_cost[point]
                print(f"cost of {available} : {value}")
                dic[available] = value
                if value < self.point_cost[available] or self.point_cost[point] == None:
                    self.point_cost[available] = value
                    self.previous_point[available] = point
                # print(f"the point '{point}' and it neighbour '{available}' and the distance betwen them is '{value}'")
            print(f"The value of the point available {dic}")
            if point not in self.visited:
                self.visited.append(point)
            if point in self.unvisited:
                self.unvisited.remove(point)
            print(self.point_cost)
            print(self.previous_point)

        # name = list(self.zones.keys())[-1]
        # while (name != start):
        #     print(self.previous_point[name])
        #     name = self.previous_point[name]


    def cost(self, point1: tuple,point2: tuple) -> int:
            x, y = point1
            x2, y2 = point2
            total = abs(x- x2) + abs(y- y2)
            return total


    def parse_connections(self,point: str):
        lst = []
        for connection in self.connections:
            p1, p2 = connection.split('-')
            if point == p1:
                lst.append(p2)
            elif point == p2:
                lst.append(p1)
            else:
                continue
        self.points_available[point] = lst


if __name__ == "__main__":
    from parsing import Parse

    x = Parse("config.txt")
    if 1 == x.file_cleaner():
        exit(1)
    try:
        zones, metadic, connections, meta_connection_dic = x.parse_arguments()
    except Exception as e:
        print(e)
        exit(1)
    else:
        if zones is None and meta_connection_dic is None and connections is None and meta_connection_dic is None:
            exit(1)
        p = Dijkstra(zones=zones,metadic=metadic,connections=connections,meta_connection_dic=meta_connection_dic)
        p.path_finding()