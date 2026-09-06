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


    def is_finished(self) -> bool:
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
        self.moves: list[dict] = []
        self.empty: dict = {}
        # Each item contains the movements made during one simulation turn.
        # The Pygame file reads this list only after the simulation is finished.
        self.movement_history: list[list[dict]] = []

    def initialize(self) -> None:
        for zone in self.graph.keys():
            self.empty[zone]= 0

        self.empty[self.start] = self.nb_drones
        return
    

    def create_drones(self) -> None:
        cost = self.cost_of_turns()

        if cost == 0:
            selected_paths = ["shortpath"]
        elif cost in (2, 3):
            selected_paths = self.paths_order[:2]
        else:
            selected_paths = self.paths_order

        for drone_id in range(self.nb_drones):
            drone = Drone(
                drone_id,
                start=self.start,
                end=self.end
            )

            path_index = drone_id % len(selected_paths)
            path_name = selected_paths[path_index]

            drone.get_path(self.paths[path_name])
            self.drones.append(drone)


    def start_simulation(self):
        self.create_drones()
        self.drones_info()
        self.initialize()
        self.movement_history.clear()

        turns = 0
        in_transit = {}
        reserved = {zone: 0 for zone in self.graph}
        requests_by_drone = {
            request['drone']: request for request in self.requests
        }

        while not self.all_finished():
            turn_movements = []
            turn_output = []
            link_usage = {}
            arrived_drones = set()

            # A drone that entered a restricted connection during the previous
            # turn must arrive at its destination during this turn.
            for d_id, transit in list(in_transit.items()):
                origin = transit['from']
                destination = transit['to']
                drone = self.drones[d_id]
                request = requests_by_drone[d_id]
            

                if destination != self.end:
                    reserved[destination] -= 1
                    self.empty[destination] += 1

                drone.move()
                request['current'] = drone.current_zone()
                request['next'] = drone.get_next_zone()
                arrived_drones.add(d_id)
                del in_transit[d_id]

                turn_movements.append({
                    'drone': d_id,
                    'from': origin,
                    'to': destination,
                    'phase': 'arrival'
                })
                turn_output.append(f"D{d_id}-{destination}")


            self.moves.clear()
            for request in self.requests:
                d_id = request['drone']
                if d_id in in_transit or d_id in arrived_drones:
                    continue

                next_zone = request['next']
                current = request['current']

                if current == self.end or next_zone is None:
                    continue

                zone_type = self.metadic[next_zone]['zone']
                if zone_type == 'blocked':
                    continue

                link = "-".join(sorted([current, next_zone]))
                max_link_capacity = self.connection_capacity(
                    current,
                    next_zone
                )
                current_link_usage = link_usage.get(link, 0)

                link_available = current_link_usage < max_link_capacity
                if not link_available:
                    continue

                if next_zone != self.end:
                    zone_load = self.empty[next_zone] + reserved[next_zone]
                    max_drones = self.metadic[next_zone]['max_drones']
                    if zone_load >= max_drones:
                        continue

                self.moves.append(request)
                link_usage[link] = current_link_usage + 1
                self.empty[current] -= 1

                if next_zone != self.end:
                    if zone_type == 'restricted':
                        reserved[next_zone] += 1
                    else:
                        self.empty[next_zone] += 1

            if not self.moves and not turn_movements:
                print("Deadlock: no drone can move")
                break

            for request in self.moves:
                d_id = request['drone']
                d = self.drones[d_id]
                old_zone = request['current']
                next_zone = request['next']
                zone_type = self.metadic[next_zone]['zone']

                if zone_type == 'restricted':
                    in_transit[d_id] = {
                        'from': old_zone,
                        'to': next_zone
                    }
                    turn_movements.append({
                        'drone': d_id,
                        'from': old_zone,
                        'to': next_zone,
                        'phase': 'transit'
                    })
                    turn_output.append(f"D{d_id}-{old_zone}-{next_zone}")
                else:
                    d.move()
                    request['current'] = d.current_zone()
                    request['next'] = d.get_next_zone()
                    turn_movements.append({
                        'drone': d_id,
                        'from': old_zone,
                        'to': d.current_zone(),
                        'phase': 'move'
                    })
                    turn_output.append(f"D{d_id}-{d.current_zone()}")

            turns += 1
            print(" ".join(turn_output))
            self.movement_history.append(turn_movements)
            self.moves.clear()

        print(turns)
        return self.movement_history


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


    def cost_of_turns(self) -> int:
        if len(self.paths_order) == 1:
            return 0
        if self.nb_drones % len(self.paths_order) == 0 and self.equal() == 0:
            return 1
        if len(self.paths_order) >= 2 and self.path_cost[self.paths_order[0]] == self.path_cost[self.paths_order[1]]:
            return 2
        if round(self.path_cost['shortpath']) + 10 <= round(self.path_cost[self.paths_order[1]]):
            return 3
        else:
            return 0
        # to be continued
       

    def zone_has_capacity(self, zone: str) -> bool:
        if zone == self.end:
            return True
        max_drones = self.metadic[zone]['max_drones']
        return self.empty[zone] < max_drones


    def connection_capacity(
        self,
        current: str,
        next_zone: str
    ) -> int:

        direct = f"{current}-{next_zone}"
        reverse = f"{next_zone}-{current}"

        if direct in self.meta_connections:
            return self.meta_connections[direct]

        if reverse in self.meta_connections:
            return self.meta_connections[reverse]

        return 1


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
