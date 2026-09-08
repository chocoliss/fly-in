*This project has been created as part of the 42 curriculum by admansar.*

# Fly-in

## Description

Fly-in is a Python routing simulation that moves a fleet of drones from one
start hub to one end hub in as few turns as possible. The input file describes
a graph of connected zones, zone types, zone capacities, connection
capacities, coordinates, and optional colors.

The project contains four main parts:

- `parsing.py` reads and validates the map.
- `algorithm.py` finds a shortest path and alternative paths without using a
  graph library.
- `simulation.py` distributes drones and schedules their turn-by-turn moves.
- `visualisation.py` replays the saved movements in a Pygame window.

`main.py` connects these parts and is the recommended program entry point.

## Features

- Object-oriented parser, pathfinder, simulation, and visualization.
- Bidirectional graph connections.
- Normal, priority, restricted, and blocked zones.
- Zone and connection capacity handling.
- Two-turn movement into restricted zones.
- Distribution of drones across selected paths.
- Turn-by-turn terminal output.
- Resizable Pygame visualization with zone colors and drone images.

## Algorithm and implementation strategy

The `Dijkstra` class builds an adjacency list from the configured connections.
It calculates the shortest path using the destination zone's movement cost:
normal and priority zones take one simulation turn, while restricted zones take
two turns. Blocked zones are excluded.

Alternative paths are produced by recalculating from points on the shortest
path while excluding the next edge of that path. The resulting paths are
ordered by their calculated costs. The simulation selects paths according to
the existing cost strategy and assigns drones to the selected paths in
round-robin order.

For each simulation turn, the engine checks destination-zone capacity and
connection capacity before accepting a movement. A drone entering a restricted
zone first occupies the connection and must arrive in the zone during the next
turn. Accepted movements are stored in `movement_history`, which lets the
Pygame interface replay the simulation without recalculating routes.

With the current list-based minimum search, one Dijkstra calculation is
approximately `O(V^2 + E)`, where `V` is the number of zones and `E` is the
number of connections. Alternative-path discovery repeats this calculation
for points on the shortest path. Simulation memory includes the graph, drones,
and the saved movement history.

## Installation

Python 3.10 or later is required. A virtual environment is recommended.

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

## Usage

Run the default `config.txt` map:

```bash
make run
```

Run another map:

```bash
make run MAP=path/to/map.txt
```

Run with Python directly:

```bash
python3 main.py path/to/map.txt
```

Start the debugger:

```bash
make debug MAP=path/to/map.txt
```

Check code style and types:

```bash
make lint
```

Remove generated Python caches:

```bash
make clean
```

## Input format

```text
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: roof 2 1 [zone=restricted color=red max_drones=1]
end_hub: goal 4 0 [color=yellow]
connection: start-roof [max_link_capacity=1]
connection: roof-goal
```

Comments begin with `#`. Zone metadata is optional. Connection metadata is
also optional and defaults to a capacity of one.

## Output example

A normal movement is displayed as `D<ID>-<destination>`. During the first turn
of a restricted movement, the connection is displayed; the drone arrives in
the restricted zone on the following turn.

```text
D0-start-roof
D0-roof D1-start-roof
D0-goal D1-roof
D1-goal
Total turns 4
```

Drones that wait during a turn are omitted from that turn's line.

## Visual representation

The Pygame window draws connections, zones, and the current drone positions.
The large circle around a zone represents its type: normal, priority,
restricted, or blocked. The smaller circle uses the optional color from the
map. The `rainbow` value is drawn as a multicolored circle. Blocked zones also
display an X. Drone images move smoothly between the positions saved by the
simulation.

This representation makes path use, congestion, waiting, restricted transit,
and drone distribution easier to inspect than terminal output alone.

## Resources

- [Python documentation](https://docs.python.org/3/)
- [Pygame documentation](https://www.pygame.org/docs/)
- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [mypy documentation](https://mypy.readthedocs.io/)
- [Flake8 documentation](https://flake8.pycqa.org/)

## AI usage

AI was used as a support tool to explain existing code, review edge cases,
suggest the separation between movement calculation and visualization, and
assist with formatting, type annotations, and documentation. The routing and
simulation decisions remain implemented in the project source code and were
tested locally. All generated suggestions were reviewed before inclusion.
