class Dijkstra:
    def __init__(self, zones: dict, metadic: dict, connections: list, meta_connection_dic: dict):
        self.zones = zones
        self.metadic = metadic
        self.connections = connections
        self.meta_connection_dic = meta_connection_dic
        self.visited = set()
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
                self.unvisited.append(point)
                self.point_cost[point] = None
        print(self.points_available)
        # print(self.point_cost)
        for point in self.zones:
            for available in self.points_available[point]:
                if available not in self.visited and available in self.unvisited:
                    value = self.cost(self.zones[available],self.zones[point])
                    print(f"the point {point} and it neighbour {available} and the distance betwen them is {value}")




    def cost(self, point1: tuple,point2: tuple) -> int:
            x, y = point1
            x2, y2 = point2
            return abs(x2-x), abs(y-y2)


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