"""Simple Pygame replay for the Fly-in simulation."""

from __future__ import annotations

import math
from pathlib import Path

import pygame

from simulation import Movement


WINDOW_SIZE = (1200, 750)
BACKGROUND = (12, 19, 32)
LINE_COLOR = (82, 100, 126)
TEXT_COLOR = (235, 241, 248)
ZONE_COLORS = {
    "normal": (70, 130, 180),
    "priority": (46, 204, 113),
    "restricted": (230, 126, 34),
    "blocked": (100, 108, 120),
}
DRONE_IMAGE = Path(__file__).with_name("drone.png")


class Visualisation:
    """Replay movements previously calculated by ``Simulation``."""

    def __init__(
        self,
        zones: dict[str, tuple[int, int]],
        metadata: dict[str, dict[str, str | int]],
        connections: list[str],
        start: str,
        end: str,
        drone_count: int,
        movement_history: list[list[Movement]],
    ) -> None:
        """Initialize the window and replay state for saved movements."""
        pygame.init()
        pygame.display.set_caption("Fly-in drone simulation")
        self.screen = pygame.display.set_mode(WINDOW_SIZE, pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("dejavusans", 13)

        self.zones = zones
        self.metadata = metadata
        self.connections = connections
        self.start = start
        self.end = end
        self.drone_count = drone_count
        self.movement_history = movement_history

        self.zone_positions: dict[str, tuple[float, float]] = {}
        self.current_zones: dict[int, str | tuple[str, str]] = {
            drone_id: start for drone_id in range(drone_count)
        }
        self.drone_positions: dict[int, tuple[float, float]] = {}
        self.animation_start: dict[int, tuple[float, float]] = {}
        self.animation_end: dict[int, tuple[float, float]] = {}

        self.turn_index = 0
        self.animating = False
        self.animation_started = 0
        self.last_animation_ended = pygame.time.get_ticks()
        self.animation_duration = 650
        self.pause_between_turns = 350
        self.running = True

        drone_size = 24 if self.drone_count > 16 else 30
        try:
            drone_picture = pygame.image.load(
                str(DRONE_IMAGE)
            ).convert_alpha()
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Drone picture not found: {DRONE_IMAGE}"
            ) from error
        except pygame.error as error:
            raise pygame.error(
                f"Cannot load drone picture '{DRONE_IMAGE}': {error}"
            ) from error
        self.drone_picture = pygame.transform.smoothscale(
            drone_picture,
            (drone_size, drone_size),
        )
        self.drone_shadow = self.drone_picture.copy()
        self.drone_shadow.fill(
            (0, 0, 0, 100),
            special_flags=pygame.BLEND_RGBA_MULT,
        )
        self._calculate_zone_positions()
        self.drone_positions = self._positions_for(self.current_zones)

    def _calculate_zone_positions(self) -> None:
        """Fit the coordinates from config.txt inside the window."""
        x_values = [point[0] for point in self.zones.values()]
        y_values = [point[1] for point in self.zones.values()]
        min_x, max_x = min(x_values), max(x_values)
        min_y, max_y = min(y_values), max(y_values)
        width = max(1, max_x - min_x)
        height = max(1, max_y - min_y)
        margin = 85
        available_width = max(200, self.screen.get_width() - 2 * margin)
        available_height = max(200, self.screen.get_height() - 2 * margin)

        self.zone_positions = {}
        for name, (x_value, y_value) in self.zones.items():
            x_position = margin + (x_value - min_x) / width * available_width
            y_position = margin + (max_y - y_value) / height * available_height
            self.zone_positions[name] = (x_position, y_position)

    @staticmethod
    def _group_offsets(
            count: int, spacing: float) -> list[tuple[float, float]]:
        """Arrange drones in one centered line around the same zone."""
        first_offset = -((count - 1) * spacing) / 2
        return [
            (0.0, first_offset + index * spacing)
            for index in range(count)
        ]

    def _positions_for(
        self,
        drone_zones: dict[int, str | tuple[str, str]],
    ) -> dict[int, tuple[float, float]]:
        """Convert every drone's zone into a visible screen position."""
        groups: dict[str, list[int]] = {}
        transit_groups: dict[tuple[str, str], list[int]] = {}
        for drone_id, location in drone_zones.items():
            if isinstance(location, tuple):
                transit_groups.setdefault(location, []).append(drone_id)
            else:
                groups.setdefault(location, []).append(drone_id)

        result: dict[int, tuple[float, float]] = {}
        for zone, drone_ids in groups.items():
            center = self.zone_positions[zone]
            spacing = 27 if len(drone_ids) > 16 else 33
            offsets = self._group_offsets(len(drone_ids), spacing)
            for drone_id, offset in zip(sorted(drone_ids), offsets):
                result[drone_id] = (
                    center[0] + offset[0],
                    center[1] + offset[1],
                )

        for (origin, destination), drone_ids in transit_groups.items():
            start_position = self.zone_positions[origin]
            end_position = self.zone_positions[destination]
            middle = (
                (start_position[0] + end_position[0]) / 2,
                (start_position[1] + end_position[1]) / 2,
            )
            difference_x = end_position[0] - start_position[0]
            difference_y = end_position[1] - start_position[1]
            length = max(1.0, math.hypot(difference_x, difference_y))
            normal = (-difference_y / length, difference_x / length)
            offsets = self._group_offsets(len(drone_ids), 27)
            for drone_id, offset in zip(sorted(drone_ids), offsets):
                result[drone_id] = (
                    middle[0] + normal[0] * offset[1],
                    middle[1] + normal[1] * offset[1],
                )
        return result

    def _start_next_turn(self) -> None:
        """Read one saved turn and begin its animation."""
        if self.turn_index >= len(self.movement_history):
            return

        self.animation_start = dict(self.drone_positions)
        for movement in self.movement_history[self.turn_index]:
            drone_id = movement["drone"]
            if movement.get("phase") == "transit":
                self.current_zones[drone_id] = (
                    movement["from"],
                    movement["to"],
                )
            else:
                self.current_zones[drone_id] = movement["to"]
        self.animation_end = self._positions_for(self.current_zones)

        self.turn_index += 1
        self.animation_started = pygame.time.get_ticks()
        self.animating = True

    @staticmethod
    def _smooth(value: float) -> float:
        """Return a smoothstep interpolation value between zero and one."""
        value = max(0.0, min(1.0, value))
        return value * value * (3 - 2 * value)

    def update(self) -> None:
        """Advance the current animation or start the following saved turn."""
        now = pygame.time.get_ticks()
        if self.animating:
            progress = (now - self.animation_started) / self.animation_duration
            progress = self._smooth(progress)
            for drone_id, destination in self.animation_end.items():
                origin = self.animation_start.get(drone_id, destination)
                self.drone_positions[drone_id] = (
                    origin[0] + (destination[0] - origin[0]) * progress,
                    origin[1] + (destination[1] - origin[1]) * progress,
                )

            if now - self.animation_started >= self.animation_duration:
                self.drone_positions = dict(self.animation_end)
                self.animating = False
                self.last_animation_ended = now
        elif now - self.last_animation_ended >= self.pause_between_turns:
            self._start_next_turn()

    def _zone_type_color(self, zone: str) -> tuple[int, int, int]:
        """Return the display color associated with a zone type."""
        zone_type = str(self.metadata.get(zone, {}).get("zone", "normal"))
        return ZONE_COLORS.get(zone_type, ZONE_COLORS["normal"])

    def _draw_configured_color(
        self,
        center: tuple[int, int],
        radius: int,
        color_name: str,
    ) -> None:
        """Draw the small circle using the color from config.txt."""
        if color_name.lower() == "rainbow":
            rainbow = (
                (239, 83, 80),
                (255, 183, 77),
                (255, 238, 88),
                (62, 207, 142),
                (73, 177, 255),
                (171, 106, 230),
            )
            angle_size = 2 * math.pi / len(rainbow)
            for index, color in enumerate(rainbow):
                start_angle = index * angle_size - math.pi / 2
                points: list[tuple[float, float]] = [center]
                for part in range(7):
                    angle = start_angle + angle_size * part / 6
                    points.append(
                        (
                            center[0] + math.cos(angle) * radius,
                            center[1] + math.sin(angle) * radius,
                        )
                    )
                pygame.draw.polygon(self.screen, color, points)
        else:
            try:
                configured_color = pygame.Color(color_name)
            except ValueError:
                configured_color = pygame.Color("white")
            pygame.draw.circle(self.screen, configured_color, center, radius)

        pygame.draw.circle(self.screen, (5, 10, 18), center, radius, 2)

    def _draw_connections(self) -> None:
        """Draw every configured connection behind the zones."""
        for connection in self.connections:
            first, second = connection.split("-")
            pygame.draw.line(
                self.screen,
                LINE_COLOR,
                self.zone_positions[first],
                self.zone_positions[second],
                3,
            )

    def _draw_zones(self) -> None:
        """Draw zone type rings, configured colors, and labels."""
        for zone, position in self.zone_positions.items():
            center = (round(position[0]), round(position[1]))
            zone_type = str(
                self.metadata.get(zone, {}).get("zone", "normal")
            )

            # Large outer circle: zone type.
            pygame.draw.circle(self.screen, (5, 10, 18), center, 30)
            pygame.draw.circle(
                self.screen,
                self._zone_type_color(zone),
                center,
                27,
            )

            # Small inner circle: the color written in config.txt.
            configured_color = str(
                self.metadata.get(zone, {}).get("color", "white")
            )
            self._draw_configured_color(center, 18, configured_color)

            if zone_type == "blocked":
                pygame.draw.line(
                    self.screen,
                    TEXT_COLOR,
                    (center[0] - 10, center[1] - 10),
                    (center[0] + 10, center[1] + 10),
                    3,
                )
                pygame.draw.line(
                    self.screen,
                    TEXT_COLOR,
                    (center[0] - 10, center[1] + 10),
                    (center[0] + 10, center[1] - 10),
                    3,
                )

            label = self.font.render(zone, True, TEXT_COLOR)
            label_rectangle = label.get_rect(
                center=(center[0], center[1] + 42))
            self.screen.blit(label, label_rectangle)

    def _draw_drones(self) -> None:
        """Draw every drone image without an identifier."""
        for position in self.drone_positions.values():
            center = (round(position[0]), round(position[1]))
            picture_rectangle = self.drone_picture.get_rect(center=center)
            self.screen.blit(self.drone_shadow, picture_rectangle.move(2, 3))
            self.screen.blit(self.drone_picture, picture_rectangle)

    def _draw_zone_legend(self) -> None:
        """Show the meaning of every zone color."""
        items = (
            ("Normal", ZONE_COLORS["normal"]),
            ("Priority", ZONE_COLORS["priority"]),
            ("Restricted", ZONE_COLORS["restricted"]),
            ("Blocked", ZONE_COLORS["blocked"]),
        )
        x_position = 22
        y_position = 25
        for label, color in items:
            pygame.draw.circle(
                self.screen,
                color,
                (x_position, y_position),
                7,
            )
            text = self.font.render(label, True, TEXT_COLOR)
            text_rectangle = text.get_rect(
                midleft=(x_position + 13, y_position),
            )
            self.screen.blit(text, text_rectangle)
            x_position = text_rectangle.right + 30

    def draw(self) -> None:
        """Draw and display one complete visualization frame."""
        self.screen.fill(BACKGROUND)
        self._draw_connections()
        self._draw_zones()
        self._draw_drones()
        self._draw_zone_legend()
        pygame.display.flip()

    def handle_events(self) -> None:
        """Handle quitting, Escape, and window resizing."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.type == pygame.VIDEORESIZE:
                width = max(800, event.w)
                height = max(550, event.h)
                self.screen = pygame.display.set_mode(
                    (width, height),
                    pygame.RESIZABLE,
                )
                self._calculate_zone_positions()
                self.drone_positions = self._positions_for(self.current_zones)
                self.animating = False

    def run(self) -> None:
        """Run the visualization loop until the window is closed."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
