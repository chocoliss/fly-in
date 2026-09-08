"""Find shortest and alternative routes through a Fly-in map."""

from __future__ import annotations

from typing import TypeAlias


Coordinates: TypeAlias = tuple[int, int]
ZoneMetadata: TypeAlias = dict[str, str | int]
Zones: TypeAlias = dict[str, Coordinates]
Metadata: TypeAlias = dict[str, ZoneMetadata]
Paths: TypeAlias = dict[str, list[str]]
PathCosts: TypeAlias = dict[str, float]


class Dijkstra:
    """Calculate usable drone paths without an external graph library."""

    def __init__(
        self,
        nb_drones: int,
        zones: Zones,
        metadic: Metadata,
        connections: list[str],
        meta_connection_dic: dict[str, int],
        end: str,
        start: str,
    ) -> None:
        """Store the map and initialize path-finding state."""
        self.zones = zones
        self.metadic = metadic
        self.connections = connections
        self.meta_connection_dic = meta_connection_dic
        self.start = start
        self.end = end
        self.visited: list[str] = []
        self.unvisited: list[str] = []
        self.paths: Paths = {}
        self.paths_cost: PathCosts = {}
        self.order_paths: list[str] = []
        self.previous_point: dict[str, str] = {}
        self.points_available: dict[str, list[str]] = {}
        self.point_cost: dict[str, float] = {}

    def initialization(
        self,
        start: str,
        point_cost: dict[str, float],
        unvisited: list[str],
        visited: list[str],
    ) -> None:
        """Prepare costs, adjacency data, and unvisited zones."""
        for point in self.zones:
            self.parse_connections(point)
            if point == start:
                point_cost[point] = 0
            elif point not in point_cost:
                point_cost[point] = float("inf")
            if point not in visited:
                unvisited.append(point)
            self.metadic[point] = self.zone_metadata(point)

    def path_finding(
        self,
        start_point: str,
        blocked_path: str | None,
        visited: list[str],
        unvisited: list[str],
        point_cost: dict[str, float],
        previous_point: dict[str, str],
    ) -> None:
        """Calculate shortest paths while optionally avoiding one edge."""
        self.initialization(start_point, point_cost, unvisited, visited)
        while unvisited:
            point = min(unvisited, key=lambda x: (point_cost[x]))
            # print("the point is ", point)
            # if len(self.points_available[point]) == 1:
            #     check = self.points_available[point][0]
            #     if check == blocked_path:
            #         break
            if point_cost[point] == float("inf"):
                # print(f"the point {point} is infinity")
                break
            for available in self.points_available[point]:
                # Available points are stored in self.points_available[point].
                if point == start_point and blocked_path == available:
                    continue
                if (
                    available in visited
                    or self.metadic[available]['zone'] == 'blocked'
                ):
                    continue
                edge_cost = self.cost(available)
                value = point_cost[point] + edge_cost
                # value combines the current cost and the next edge cost.
                if value < point_cost[available]:
                    point_cost[available] = value
                    previous_point[available] = point
            visited.append(point)
            unvisited.remove(point)
        # print(point_cost)
        # print(previous_point)

    def multi_path_finding(
        self,
    ) -> tuple[Paths, PathCosts, list[str]]:
        """Return the shortest route, alternatives, costs, and ordering."""
        path: list[str] = []
        names = [
            'p2',
            'p3',
            'p4',
            'p5',
            'p6',
            'p7',
            'p8',
            'p9',
            'p10',
            'p11',
            'p12',
            'p13',
            'p14']
        self.path_finding(
            self.start,
            None,
            self.visited,
            self.unvisited,
            self.point_cost,
            self.previous_point)
        short_path = self.path(self.start, self.end, self.previous_point)
        # self.print_path(self.start, self.end, self.previous_point, None)
        short_path = short_path[::-1]
        self.paths['shortpath'] = short_path
        self.paths_cost['shortpath'] = self.point_cost[self.end]
        i = 1
        for zone in short_path[:-1]:
            p_cost: dict[str, float] = {}
            l_unvisited: list[str] = []
            pr_point: dict[str, str] = {}
            l_visited: list[str] = []
            blocked_path = short_path[short_path.index(zone) + 1]
            path.append(zone)
            if zone != self.start:
                pr_point[zone] = self.previous_point[zone]
            self.path_finding(
                zone,
                blocked_path,
                l_visited,
                l_unvisited,
                p_cost,
                pr_point)
            if self.end not in pr_point:
                continue
            lst = self.path(self.start, zone, self.previous_point)[
                ::-1] + self.path(zone, self.end, pr_point)[::-1]
            lst.remove(zone)
            self.paths[names[i]] = lst
            self.paths_cost[names[i]] = self.point_cost[zone] + \
                p_cost[self.end]
            i += 1
        self.order_paths = sorted(
            self.paths_cost,
            key=lambda x: self.paths_cost[x])
        # print(self.paths)
        # print(self.paths_cost)
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
    #             first_path = self.paths[self.order_paths[j]]
    #             second_path = self.paths[self.order_paths[i]]
    #             if first_path != second_path:
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
        """Return the movement cost of entering ``point``."""
        zone = str(self.metadic[point]['zone'])
        if zone == 'normal':
            return 1
        if zone == 'priority':
            return 0.99
        if zone == 'restricted':
            return 2
        raise ValueError(f"Unknown zone type: {zone}")

    def parse_connections(self, point: str) -> None:
        """Build the adjacency list for one point."""
        lst: list[str] = []
        for connection in self.connections:
            p1, p2 = connection.split('-')
            if point == p1:
                lst.append(p2)
            elif point == p2:
                lst.append(p1)
            else:
                continue
        self.points_available[point] = lst

    def path(
        self,
        start: str,
        end: str,
        previous_point: dict[str, str],
    ) -> list[str]:
        """Reconstruct a route from a previous-point mapping."""
        lst: list[str] = []
        while start != end:
            lst.append(end)
            end = previous_point[end]
        lst.append(start)
        return lst

    def print_path(
        self,
        start: str,
        end: str,
        previous_point: dict[str, str] | None,
        lst: list[str] | None,
    ) -> None:
        """Print either a reconstructed path or a supplied path."""
        if previous_point:
            lst = self.path(start, end, previous_point)
            lst = lst[::-1]
        if lst is None:
            raise ValueError("A path or previous-point mapping is required")
        r = ' -> '.join(lst)
        print(r)

    def zone_metadata(self, name: str) -> ZoneMetadata:
        """Return complete metadata for a zone, applying defaults."""
        color: str = "none"
        zone: str = "normal"
        max_drones: int = 1
        if name in self.metadic.keys():
            if "color" in self.metadic[name].keys():
                color = str(self.metadic[name]['color'])
            if "zone" in self.metadic[name].keys():
                zone = str(self.metadic[name]['zone'])
            if "max_drones" in self.metadic[name].keys():
                max_drones = int(self.metadic[name]['max_drones'])
        dic: ZoneMetadata = {
            'color': color,
            'zone': zone,
            'max_drones': max_drones
        }
        return dic

    def connection_metadata(self, connection: str) -> int:
        """Return explicit capacity metadata for ``connection`` or zero."""
        max_link_capacity: int = 0
        if connection in self.meta_connection_dic.keys():
            max_link_capacity = self.meta_connection_dic[connection]
        return max_link_capacity
