"""Simulate turn-by-turn drone movements through the zone graph."""

from __future__ import annotations

from typing import TypeAlias, TypedDict


Coordinates: TypeAlias = tuple[int, int]
Graph: TypeAlias = dict[str, Coordinates]
ZoneMetadata: TypeAlias = dict[str, str | int]
Metadata: TypeAlias = dict[str, ZoneMetadata]
Paths: TypeAlias = dict[str, list[str]]
PathCosts: TypeAlias = dict[str, float]
Movement = TypedDict(
    "Movement",
    {"drone": int, "from": str, "to": str, "phase": str},
)
Transit = TypedDict("Transit", {"from": str, "to": str})


class Request(TypedDict):
    """Describe one drone's current zone and requested destination."""

    drone: int
    current: str
    next: str | None


class Drone:
    """Track one drone's assigned path and current position."""

    def __init__(self, id: int, start: str, end: str) -> None:
        """Initialize a drone at ``start`` with no assigned path."""
        # self.nb_drones = nb_drones
        self.drone_id = id
        self.path: list[str] = []
        self.path_index = 0
        self.zone = start
        self.end = end
        self.finished = False

    def get_path(self, path: list[str]) -> None:
        """Assign a complete route to the drone."""
        self.path = path

    def current_zone(self) -> str:
        """Return the zone currently occupied by the drone."""
        return self.zone

    def get_next_zone(self) -> str | None:
        """Return the next zone on the route, if one remains."""
        if self.finished:
            return None
        if self.path_index + 1 >= len(self.path):
            return None
        return self.path[self.path_index + 1]

    def move(self) -> None:
        """Advance the drone by one position along its assigned path."""
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
        """Return whether the drone has reached the end hub."""
        return self.finished


class Simulation:
    """Schedule all drones while enforcing zone and link capacities."""

    def __init__(
        self,
        graph: Graph,
        nb_drones: int,
        paths: Paths,
        path_cost: PathCosts,
        paths_order: list[str],
        start: str,
        end: str,
        metadic: Metadata,
        meta_connections: dict[str, int],
    ) -> None:
        """Store the graph, calculated paths, capacities, and endpoints."""
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
        self.requests: list[Request] = []
        self.moves: list[Request] = []
        self.empty: dict[str, int] = {}
        # Each item contains the movements made during one simulation turn.
        # The Pygame file reads this list only after the simulation is
        # finished.
        self.movement_history: list[list[Movement]] = []

    def initialize(self) -> None:
        """Initialize the number of drones occupying every zone."""
        for zone in self.graph.keys():
            self.empty[zone] = 0

        self.empty[self.start] = self.nb_drones
        return

    def create_drones(self) -> None:
        """Create drones and distribute them across selected paths."""
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

    def start_simulation(self) -> list[list[Movement]]:
        """Run until every drone arrives, returning movements by turn."""
        self.create_drones()
        self.drones_info()
        self.initialize()
        self.movement_history.clear()

        turns = 0
        in_transit: dict[int, Transit] = {}
        reserved: dict[str, int] = {zone: 0 for zone in self.graph}
        requests_by_drone: dict[int, Request] = {
            request['drone']: request for request in self.requests
        }

        while not self.all_finished():
            turn_movements: list[Movement] = []
            turn_output: list[str] = []
            link_usage: dict[str, int] = {}
            arrived_drones: set[int] = set()

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

                zone_type = str(self.metadic[next_zone]['zone'])
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
                    max_drones = int(
                        self.metadic[next_zone]['max_drones']
                    )
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
                raise RuntimeError("Deadlock: no drone can move")

            for request in self.moves:
                d_id = request['drone']
                d = self.drones[d_id]
                old_zone = request['current']
                next_zone = request['next']
                if next_zone is None:
                    continue
                zone_type = str(self.metadic[next_zone]['zone'])

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

        print(f"Total turns {turns}")
        return self.movement_history

    def drones_info(self) -> None:
        """Create the initial movement request for every drone."""
        for drone in self.drones:
            current = drone.current_zone()
            next_zone = drone.get_next_zone()
            request: Request = {
                'drone': drone.drone_id,
                'current': current,
                'next': next_zone
            }
            self.requests.append(request)

    def cost_of_turns(self) -> int:
        """Choose the existing path-selection strategy code."""
        if len(self.paths_order) == 1:
            return 0
        if self.nb_drones % len(self.paths_order) == 0 and self.equal() == 0:
            return 1
        if (
            len(self.paths_order) >= 2
            and self.path_cost[self.paths_order[0]]
            == self.path_cost[self.paths_order[1]]
        ):
            return 2
        if round(self.path_cost['shortpath']) + \
                10 <= round(self.path_cost[self.paths_order[1]]):
            return 3
        else:
            return 0
        # to be continued

    def zone_has_capacity(self, zone: str) -> bool:
        """Return whether ``zone`` can accept another drone."""
        if zone == self.end:
            return True
        max_drones = int(self.metadic[zone]['max_drones'])
        return self.empty[zone] < max_drones

    def connection_capacity(
        self,
        current: str,
        next_zone: str
    ) -> int:
        """Return the configured capacity of a connection, or one."""

        direct = f"{current}-{next_zone}"
        reverse = f"{next_zone}-{current}"

        if direct in self.meta_connections:
            return self.meta_connections[direct]

        if reverse in self.meta_connections:
            return self.meta_connections[reverse]

        return 1

    def equal(self) -> int | None:
        """Return zero when every discovered path has the same cost."""
        lst = list(self.path_cost.values())
        if lst.count(lst[0]) == len(lst):
            return 0
        return None

    def all_finished(self) -> bool:
        """Return whether every drone has reached the end hub."""
        for drone in self.drones:
            if not drone.finished:
                return False
        return True
