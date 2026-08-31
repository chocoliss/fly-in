def initialize(self) -> None:
    for zone in self.graph.keys():
        self.empty[zone] = 0


def drones_info(self) -> None:
    """
    Recreate the requests for the current turn.
    """
    self.requests.clear()

    for drone in self.drones:

        if drone.finished:
            continue

        current = drone.current_zone()
        next_zone = drone.get_next_zone()

        request = {
            "drone": drone.drone_id,
            "current": current,
            "next": next_zone
        }

        self.requests.append(request)


def all_finished(self) -> bool:
    for drone in self.drones:
        if not drone.finished:
            return False

    return True


def get_link_capacity(self, current: str, next_zone: str) -> int:
    """
    Return max_link_capacity for current-next_zone.
    Default capacity = 1.
    """

    connection = "-".join([current, next_zone])
    reverse = "-".join([next_zone, current])

    if connection in self.meta_connections:
        value = self.meta_connections[connection]

    elif reverse in self.meta_connections:
        value = self.meta_connections[reverse]

    else:
        return 1

    # If meta_connections stores directly the number
    if isinstance(value, int):
        return value

    # If it stores metadata dictionary
    return value.get("max_link_capacity", 1)


def connection_key(self, current: str, next_zone: str) -> tuple[str, str]:
    """
    Because connections are bidirectional:
    A-B and B-A represent the same connection.
    """

    return tuple(sorted((current, next_zone)))


def resolve_requests(self) -> list:
    """
    Decide which drones can move THIS turn.

    Important:
    self.empty is NOT modified here.
    """

    candidates = []

    # ---------------------------------------------------
    # 1. Remove invalid requests
    # ---------------------------------------------------

    for request in self.requests:

        current = request["current"]
        next_zone = request["next"]

        if current == self.end:
            continue

        if next_zone is None:
            continue

        candidates.append(request)

    # Lower drone ID gets priority for now
    candidates.sort(key=lambda request: request["drone"])

    # ---------------------------------------------------
    # 2. Check connection capacity
    # ---------------------------------------------------

    link_usage = {}
    after_links = []

    for request in candidates:

        current = request["current"]
        next_zone = request["next"]

        key = self.connection_key(current, next_zone)

        max_capacity = self.get_link_capacity(
            current,
            next_zone
        )

        used = link_usage.get(key, 0)

        if used < max_capacity:

            after_links.append(request)

            link_usage[key] = used + 1

    candidates = after_links

    # ---------------------------------------------------
    # 3. Check zone capacities
    #
    # We repeat because rejecting a drone means that
    # its current zone is NOT freed anymore.
    # ---------------------------------------------------

    changed = True

    while changed:

        changed = False

        outgoing = {}
        incoming = {}

        # Count drones leaving/entering
        for request in candidates:

            current = request["current"]
            next_zone = request["next"]

            # start has unlimited capacity
            if current != self.start:
                outgoing[current] = (
                    outgoing.get(current, 0) + 1
                )

            # end has unlimited capacity
            if next_zone != self.end:
                if next_zone not in incoming:
                    incoming[next_zone] = []

                incoming[next_zone].append(request)

        rejected = []

        # Check each destination zone
        for zone, zone_requests in incoming.items():

            current_occupancy = self.empty[zone]

            leaving = outgoing.get(zone, 0)

            max_drones = self.metadic[zone]["max_drones"]

            # Example:
            #
            # capacity = 1
            # occupancy = 1
            # leaving = 1
            #
            # available = 1 - (1 - 1)
            #           = 1
            #
            available = (
                max_drones
                - (current_occupancy - leaving)
            )

            if available < 0:
                available = 0

            if len(zone_requests) > available:

                # lower drone IDs already come first
                rejected.extend(
                    zone_requests[available:]
                )

        if rejected:

            changed = True

            candidates = [
                request
                for request in candidates
                if request not in rejected
            ]

    return candidates


def execute_moves(self, moves: list) -> None:
    """
    Now that all moves were accepted,
    actually change the simulation state.
    """

    # --------------------------------------------
    # First update occupancy
    # --------------------------------------------

    for request in moves:

        current = request["current"]
        next_zone = request["next"]

        # start is unlimited
        if current != self.start:
            self.empty[current] -= 1

        # end is unlimited
        if next_zone != self.end:
            self.empty[next_zone] += 1

    # --------------------------------------------
    # Then move the Drone objects
    # --------------------------------------------

    for request in moves:

        drone_id = request["drone"]

        drone = self.drones[drone_id]

        drone.move()

        print(
            f"D{drone_id} -> {drone.current_zone()}",
            end=" "
        )

    if moves:
        print()


def start_simulation(self) -> None:

    self.create_drones()

    self.initialize()

    turn = 1

    while not self.all_finished():

        # Create requests using CURRENT drone positions
        self.drones_info()

        print(f"\nTurn {turn}")

        # Decide first
        self.moves = self.resolve_requests()

        # Move afterwards
        self.execute_moves(self.moves)

        print("Occupancy:", self.empty)

        self.moves.clear()

        turn += 1