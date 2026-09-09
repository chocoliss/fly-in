"""Run the Fly-in parser, pathfinder, simulation, and visualization."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TypeAlias, cast

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
EmptyProjectData: TypeAlias = tuple[
    None,
    None,
    None,
    None,
    None,
    None,
    None,
]
ProjectResult: TypeAlias = ProjectData | EmptyProjectData


def load_project(config_path: Path) -> ProjectResult:
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
        return (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )
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
    """Run the project using the map supplied on the command line."""
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "map",
        nargs="?",
        type=Path,
        default=Path(__file__).with_name("config.txt"),
    )
    arguments = argument_parser.parse_args()

    try:
        project = load_project(arguments.map)
        if project == (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        ):
            raise ValueError("Nothing to visualize.")
        Visualisation(*cast(ProjectData, project)).run()
    except (OSError, RuntimeError, ValueError, pygame.error) as error:
        print(f"Error: {error}")
        pygame.quit()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
