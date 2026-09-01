class Dijkstra:
    def __init__(self,nb_drones:int, zones: dict, metadic: dict, connections: list, meta_connection_dic: dict, end: str, start: str):
        self.zones = zones
        self.metadic = metadic
        self.connections = connections
        self.meta_connection_dic = meta_connection_dic
        self.start = start
        self.end = end
        self.visited = []
        self.unvisited = []
        self.paths = {}
        self.paths_cost = {}
        self.order_paths = []
        self.previous_point = {}
        self.points_available = {}
        self.point_cost = {}


    def initialization(self, start:str, point_cost: dict, unvisited: list, visited: list):
        for point in self.zones:
            self.parse_connections(point)
            if point == start:
                point_cost[point] = 0
            elif point not in point_cost:
                point_cost[point] = float("inf")
            if point not in visited:
                unvisited.append(point)
            self.metadic[point] = self.zone_metadata(point)


    def path_finding(self, start_point: str, blocked_path: str | None, visited: list, unvisited: list, point_cost: dict, previous_point: dict):
        self.initialization(start_point, point_cost, unvisited, visited)
        while unvisited:
            point = min(unvisited, key=lambda x:(point_cost[x]))
            # print("the point is ", point)
            # if len(self.points_available[point]) == 1:
            #     check = self.points_available[point][0]
            #     if check == blocked_path:
            #         break
            if point_cost[point] == float("inf"):
                # print(f"the point {point} is infinity")
                break
            for available in self.points_available[point]:
                # print(f"the available points of {point} are {self.points_available[point]}")
                if point == start_point and blocked_path == available:
                    continue
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
        path = []
        names = ['p2','p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13', 'p14']
        self.path_finding(self.start, None,  self.visited, self.unvisited, self.point_cost, self.previous_point)
        short_path = self.path(self.start, self.end, self.previous_point) 
        # self.print_path(self.start, self.end, self.previous_point, None)
        short_path = short_path[::-1]
        self.paths['shortpath'] = short_path
        self.paths_cost['shortpath'] = self.point_cost[self.end]
        i = 1
        for zone in short_path[:-1]:
            p_cost = {}
            l_unvisited = []
            pr_point = {}
            l_visited = []
            blocked_path = short_path[short_path.index(zone) + 1]
            path.append(zone)
            if zone != self.start:
                pr_point[zone] = self.previous_point[zone]
            self.path_finding(zone, blocked_path, l_visited, l_unvisited, p_cost, pr_point)
            if self.end not in pr_point:
                continue
            lst = self.path(self.start, zone, self.previous_point)[::-1] + self.path(zone, self.end, pr_point)[::-1]
            lst.remove(zone)
            self.paths[names[i]] = lst
            self.paths_cost[names[i]] =  self.point_cost[zone] + p_cost[self.end]
            i += 1
        self.order_paths = sorted(self.paths_cost, key=lambda x: self.paths_cost[x])
        # print(self.paths)
        print(self.paths_cost)
        # for element in self.order_paths:
        #     self.print_path(self.start,self.end,None, self.paths[element])
        return self.paths, self.paths_cost, self.order_paths


    # def check_paths(self):
    #     length = len(self.order_paths)
    #     if length == 1:
    #         return
    #     j = 0
    #     while(j < length):
    #         i = j + 1
    #         while(i + 1 <= length):
    #             if self.paths[self.order_paths[j]] != self.paths[self.order_paths[i]]:
    #                 p1 = set(self.paths[self.order_paths[i]])
    #                 p2 = set(self.paths[self.order_paths[j]])
    #                 inter = p1.intersection(p2)
    #                 if inter:
    #                     print(inter)
    #                 else:
    #                     print("no inter")
    #             i += 1
    #         j += 1
    #     return


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


    def print_path(self, start: str, end: str,previous_point: list | None, lst: list | None) -> None:
        if previous_point:
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