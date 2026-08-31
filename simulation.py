class Drone:
    def __init__(self, id: int, start: str, end: str) -> None:
        # self.nb_drones = nb_drones
        self.drone_id = id
        self.path = []
        self.path_index = 0
        self.zone = start
        self.end = end
        self.finished = False


    def get_path(self, path: list) -> None:
        self.path = path


    def current_zone(self) -> str | None:
        return self.zone


    def get_next_zone(self) -> str | None:
        if self.finished:
            return None
        if self.path_index + 1 >= len(self.path):
            return None
        return self.path[self.path_index + 1]


    def move(self):
        if self.is_finished():
            return
        
        if self.path_index + 1 >= len(self.path):
            return
        self.path_index += 1
        self.zone = self.path[self.path_index]
        if self.zone == self.end:
            self.finished = True
        return


    def is_finished(self) -> None:
        return self.finished 
        



class Simulation:
    def __init__(self,graph: dict ,nb_drones: int ,paths: dict, path_cost: dict, paths_order: list, start: str, end: str, metadic: dict, meta_connections: dict) -> None:
        self.nb_drones = nb_drones
        self.graph = graph
        self.paths = paths
        self.path_cost = path_cost
        self.paths_order = paths_order
        self.start = start
        self.end = end
        self.metadic = metadic
        self.meta_connections = meta_connections
        self.drones: list[Drone] = []
        self.requests : list[dict] = []
        self.empty: dict = {}
        self.moves: list[str] = []

    def initialize(self) -> None:
        for zone in self.graph.keys():
            self.empty[zone]= 0
        self.empty[self.start] = nb_drones


    def create_drones(self) -> None:
        cost = self.cost_of_turns()
        print("the cost is ", cost)
        if cost == 1:
            for i in range(self.nb_drones):
                d = Drone(i, start=self.start, end= self.end)
                if i < (self.nb_drones / 2):
                    d.get_path(self.paths[self.paths_order[0]])
                else:
                    d.get_path(self.paths[self.paths_order[1]])
                self.drones.append(d)
        if cost == 0:
            count = self.nb_drones // len(self.paths_order)
            for i in range(self.nb_drones):
                d = Drone(i, start=self.start, end= self.end)
                path_index = i // count
                d.get_path(self.paths[self.paths_order[path_index]])
                self.drones.append(d)
        if cost == 2:
            for i in range(self.nb_drones):
                d = Drone(i, self.start, self.end)
                d.get_path(self.paths['shortpath'])
                self.drones.append(d)


    def start_simulation(self):
        self.create_drones()
        self.drones_info()
        self.initialize()
        while not self.all_finished():
            link_capacity = []
            for request in self.requests:
                next = request['next']
                current = request['current']
                # if next is not None:
                #     r = '-'.join([current, next])
                #     print(r)
                if current == self.end or next is None:
                    self.empty[current] = 0
                    continue
                if self.isfull(next,current):
                    self.empty[next] += 1
                    self.empty[current] -= 1
                    # count = link_capacity.count(r)
                    # if count < self.meta_connections[r]:
                    #     link_capacity.append(r)
                    # print(f"the current zone {current} is empty")
                    
                    self.moves.append(request)
                    # if not self.moves:
                    #     print("Deadlock: no drone can move")
                    #     break
                else :
                    continue
            # print('---------------------')
            # print(self.empty)
            # print('---------------------')
            for request in self.moves:
                # print(request)
                id = request['drone']
                self.drones[id].move()
                d = self.drones[id]
                print(
                    f"D{id} -> {d.current_zone()}",
                        end=" "
                    )
                request['current'] = request['next']
                request['next'] = d.get_next_zone()

            if self.moves:
                print()
            
            self.moves.clear()




    def drones_info(self):
        for drone in self.drones:
            current = drone.current_zone()
            next_zone = drone.get_next_zone()
            request = {
                'drone': drone.drone_id,
                'current': current,
                'next': next_zone
            }
            self.requests.append(request)



    def isfull(self, next: str, current) -> bool:
        r = '-'.join([current, next])
        re = '-'.join([next, current])
        max_capacity = 1
        if r in self.meta_connections:
            max_capacity = self.meta_connections[r]
        if re in self.meta_connections:
            max_capacity = self.meta_connections[re]
        # print(f"the max drones {self.metadic[next]['max_drones']} and max capacity {max_capacity}")
        if (self.empty[next] == 0) or (self.metadic[next]['max_drones'] - self.empty[next] >= 1 and max_capacity > 1):
            return True
        return False


    def cost_of_turns(self) -> int:
        if self.nb_drones % len(self.paths_order) == 0 and self.equal() == 0:
            return 0
        if len(self.paths_order) >= 2 and self.path_cost[self.paths_order[0]] == self.path_cost[self.paths_order[1]]:
            return 1
        if len(self.paths_order) == 1:
            return 2
        # to be continued
        

    def equal(self) -> int:
        lst = list(self.path_cost.values())
        if lst.count(lst[0]) == len(lst):
            return 0


    def all_finished(self) -> bool:
        for drone in self.drones:
            if not drone.finished:
                return False
        return True


if __name__ == "__main__":
    from parsing import Parse
    from algorithm import Dijkstra
    
    x = Parse("config.txt")
    if 1 == x.file_cleaner():
        exit(1)
    try:
        nb_drones, zones, metadic, connections, meta_connection_dic, end, start = x.parse_arguments()
    except Exception as e:
        print(e)
        exit(1)
    if zones is None or meta_connection_dic is None or connections is None or meta_connection_dic is None:
        exit(1)
            # print(metadic)
    p = Dijkstra(nb_drones=nb_drones,zones=zones,metadic=metadic,connections=connections,meta_connection_dic=meta_connection_dic, end=end, start=start)
    paths, paths_cost, paths_order = p.multi_path_finding()
    s = Simulation(zones, nb_drones, paths, paths_cost,paths_order, start, end, metadic, meta_connection_dic)
    s.start_simulation()
    exit(0)
