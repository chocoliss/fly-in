def start_simulation(self):

    self.create_drones()
    self.drones_info()
    self.initialize()

    while not self.all_finished():

        link_usage = {}

        for request in self.requests:

            next_zone = request['next']
            current = request['current']

            if current == self.end or next_zone is None:
                continue

            link = f"{current}-{next_zone}"

            max_link_capacity = self.connection_capacity(
                current,
                next_zone
            )

            current_link_usage = link_usage.get(link, 0)

            zone_available = self.zone_has_capacity(next_zone)
            link_available = current_link_usage < max_link_capacity

            if zone_available and link_available:

                self.moves.append(request)

                link_usage[link] = current_link_usage + 1

                # Reserve the places for this turn
                self.occupancy[current] -= 1

                if next_zone != self.end:
                    self.occupancy[next_zone] += 1

        if not self.moves:
            print("Deadlock: no drone can move")
            break

        for request in self.moves:

            drone_id = request['drone']

            drone = self.drones[drone_id]

            drone.move()

            print(
                f"D{drone_id} -> {drone.current_zone()}",
                end=" "
            )

            request['current'] = drone.current_zone()
            request['next'] = drone.get_next_zone()

        print()

        self.moves.clear()