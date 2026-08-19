class Dijkstra:
    def __init__(self,nb_drones:int, zones: dict, metadic: dict, connections: list, meta_connection_dic: dict, end: str, start: str):
        self.zones = zones
        self.__nb_drones = nb_drones
        self.metadic = metadic
        self.connections = connections
        self.meta_connection_dic = meta_connection_dic
        self.start = start
        self.end = end
        self.visited = []
        self.unvisited = []
        self.paths = {}
        self.paths_cost = {}
        self.previous_point = {}
        self.points_available = {}
        self.point_cost = {}


    def initialization(self, point_cost: dict, unvisited: list, visited: list):
        for point in self.zones:
            self.parse_connections(point)
            if point == self.start:
                point_cost[point] = 0
            elif point not in point_cost:
                point_cost[point] = float("inf")
            if point not in visited:
                unvisited.append(point)
            self.metadic[point] = self.zone_metadata(point)


    def path_finding(self, start_point: str, visited: list, unvisited: list, point_cost: dict, previous_point: dict):
        self.initialization(point_cost, unvisited, visited)
        while unvisited:
            point = min(unvisited, key=lambda x:(point_cost[x]))
            # print("the point is ", point)
            # print("the available points are3 " ,self.points_available[point])
            for available in self.points_available[point]:
                if available in visited or self.metadic[available]['zone'] == 'blocked':
                    continue
                edge_cost = self.cost(available)
                value = point_cost[point] + edge_cost
                # print(f"cost of {available}: {value} = {point_cost[point]} + {edge_cost}")
                if  value < point_cost[available]:
                    point_cost[available] = value
                    previous_point[available] = point
            visited.append(point)
            unvisited.remove(point)
        # print(point_cost)
        # print(previous_point)


    def multi_path_finding(self):
        p_cost = {}
        path = []
        l_unvisited = []
        pr_point = {}
        self.path_finding(self.start, self.visited, self.unvisited, self.point_cost, self.previous_point)
        short_path = self.path(self.start, self.end, self.previous_point)
        self.print_path(self.start, self.end, self.previous_point)
        short_path = short_path[::-1]
        self.paths['1'] = short_path
        self.paths_cost['1'] = self.point_cost[self.end]
        for zone in short_path[1:-1]:
            l_visited = []
            # print("The zone were blockin", zone)
            l_visited.append(zone)
            path.append(zone)
            self.path_finding(zone, l_visited, l_unvisited, p_cost, pr_point)
            # print("lvisited" ,l_visited)
            if self.end not in pr_point:
                continue
            self.paths[zone] = self.path(self.start, self.end, pr_point)[::-1]
            self.paths_cost[zone] = p_cost[self.end]
            # print(self.paths)
            print(self.paths_cost)
            for key in self.paths.keys():
                if key == '1':
                    continue
                self.print_path(self.start, self.end, pr_point)


    def cost(self, point: str) -> float:
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


    def path(self, start: str, end: str, previous_point: list) -> list:
        lst = []
        while(start != end):
            lst.append(end)
            end = previous_point[end]
        lst.append(start)
        return lst


    def print_path(self, start: str, end: str,previous_point: list) -> None:
        lst = self.path(start, end, previous_point)
        lst = lst[::-1]
        r = ' -> '.join(lst)
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
        nb_drones, zones, metadic, connections, meta_connection_dic, end, start = x.parse_arguments()
    except Exception as e:
        print(e)
        exit(1)
    else:
        if zones is None or meta_connection_dic is None or connections is None or meta_connection_dic is None:
            exit(1)
        # print(metadic)
        p = Dijkstra(nb_drones=nb_drones,zones=zones,metadic=metadic,connections=connections,meta_connection_dic=meta_connection_dic, end=end, start=start)
        p.multi_path_finding()
        exit(0)