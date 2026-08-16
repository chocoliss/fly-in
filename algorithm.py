class Dijkstra:
    def __init__(self,nb_drones:int, zones: dict, metadic: dict, connections: list, meta_connection_dic: dict):
        self.zones = zones
        self.__nb_drones = nb_drones
        self.metadic = metadic
        self.connections = connections
        self.meta_connection_dic = meta_connection_dic
        self.visited = []
        self.unvisited = []
        self.paths = {}
        self.previous_point = {}
        self.points_available = {}
        self.point_cost = {}


    def initialization(self):
        start = list(self.zones.keys())[0]
        for point in self.zones:
            self.parse_connections(point)
            if point == start:
                self.point_cost[point] = 0    
            else:
                self.point_cost[point] = float("inf")
            self.unvisited.append(point)
            self.metadic[point] = self.zone_metadata(point)

    def path_finding(self):
        self.initialization()
        while self.unvisited:
            point = min(self.unvisited, key=lambda x:(self.point_cost[x]))
            for available in self.points_available[point]:
                if available in self.visited or self.metadic[available]['zone'] == 'blocked':
                    continue
                edge_cost = self.cost(point, available)
                value = self.point_cost[point] + edge_cost
                print(f"cost of {available}: {value}")
                if (self.point_cost[available] is float("inf") or value < self.point_cost[available]):
                    self.point_cost[available] = value
                    self.previous_point[available] = point
            self.visited.append(point)
            self.unvisited.remove(point)
        print(self.point_cost)
        print(self.previous_point)


    def cost(self, point1: str,point2: str) -> int:
        cost = 0
        start = list(self.zones.keys())[0]
        while (start != point1):
            point1 = self.previous_point[point1]
            cost += self.point_cost[point1]
        return cost + self.zone_cost(point2)

    def zone_cost(self, point: str) -> int:
        zone = self.metadic[point]['zone']
        if zone == 'normal':
            return 1
        if zone == 'priority':
            return 0.99
        if zone == 'restricted':
            return 2

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


    def print_path(self):
        start = list(self.zones.keys())[0]
        end = list(self.zones.keys())[-1]
        lst = []
        while(start != end):
            lst.append(end)
            end = self.previous_point[end]
        lst.append(start)
        r = "->".join(lst[::-1])
        print(r)


    def zone_metadata(self,name: str) -> dict:
        color: str = "none"
        zone: str = "normal"
        max_drones: int = 1
        if name in self.metadic.keys():
            if "color" in self.metadic[name].keys():
                color = self.metadic[name]['color']
            if "zone" in self.metadic[name].keys():
                zone = self.metadic[name]['zone']
            if "max_drones" in self.metadic[name].keys():
                max_drones = self.metadic[name]['max_drones']
        dic = {
            'color': color,
            'zone': zone,
            'max_drones': max_drones
        }
        return dic


    def connection_metadata(self, connection: str) -> int:
        max_link_capacity: int = 0
        if connection in meta_connection_dic.keys():
                max_link_capacity = self.meta_connection_dic[connection]
        return max_link_capacity
    

        
if __name__ == "__main__":
    from parsing import Parse

    x = Parse("config.txt")
    if 1 == x.file_cleaner():
        exit(1)
    try:
        nb_drones, zones, metadic, connections, meta_connection_dic = x.parse_arguments()
    except Exception as e:
        print(e)
        exit(1)
    else:
        if zones is None or meta_connection_dic is None or connections is None or meta_connection_dic is None:
            exit(1)
        # print(metadic)
        p = Dijkstra(nb_drones=nb_drones,zones=zones,metadic=metadic,connections=connections,meta_connection_dic=meta_connection_dic)
        # for name in zones:
        #     print(p.zone_metadata(name))
        # for connection in connections:
        #     print(p.connection_metadata(connection))
        p.path_finding()
        p.print_path()
        exit(0)