"""Run the Fly-in parser, pathfinder, simulation, and visualization."""

from __future__ import annotations

from pathlib import Path
from typing import TypeAlias

import pygame

from algorithm import Dijkstra
from parsing import Metadata, Parse, Zones
from simulation import Movement, Simulation
from visualisation import Visualisation


ProjectData: TypeAlias = tuple[
    Zones,
    Metadata,
    list[str],
    str,
    str,
    int,
    list[list[Movement]],
]


def load_project(config_path: Path) -> ProjectData:
    """Run the original simulation once and return its saved movements."""
    parser = Parse(str(config_path))

    parsed = parser.parse_arguments()
    nb_drones, zones, metadata, connections, link_metadata, end, start = parsed

    finder = Dijkstra(
        nb_drones=nb_drones,
        zones=zones,
        metadic=metadata,
        connections=connections,
        meta_connection_dic=link_metadata,
        end=end,
        start=start,
    )
    path_result = finder.multi_path_finding()
    if path_result[0] is None:
        raise ValueError("Nothing to visualize.")
    paths, path_costs, path_order = path_result
    simulation = Simulation(
        zones,
        nb_drones,
        paths,
        path_costs,
        path_order,
        start,
        end,
        metadata,
        link_metadata,
    )
    movement_history = simulation.start_simulation()
    return (
        zones,
        metadata,
        connections,
        start,
        end,
        nb_drones,
        movement_history,
    )


def main() -> int:
    """Run the project using config.txt"""
    try:
        file = Path(__file__).with_name("config.txt")
        if not file.exists():
            raise FileNotFoundError(
                "File not found"
            )
        project = load_project(file)
        Visualisation(*project).run()
    except (OSError, RuntimeError, ValueError, pygame.error) as error:
        print(f"Error: {error}")
        pygame.quit()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
