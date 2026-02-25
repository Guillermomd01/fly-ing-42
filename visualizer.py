import pygame
from typing import Any, Tuple


class DroneVisualizer:
    """
    Class responsible for the management and graphical
    representation of the simulation.

    Uses the Pygame library to render in real-time
    the map of zones, the logical connections,
    and the current state of each drone in the fleet.
    """
    def __init__(self, simulation: Any, scale: int = 100) -> None:
        """
        Initializes the Pygame engine, configures the window,
        and defines the scale.
        """
        pygame.init()
        self.sim = simulation
        self.scale = scale
        self.offset_x = 100
        self.offset_y = 300

        self.screen = pygame.display.set_mode((2500, 800))
        pygame.display.set_caption("Fly-in Drone Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)

    def to_screen(self, coords: Tuple[int, int]) -> Tuple[int, int]:
        """
        Transforms logical graph coordinates into
        screen pixel coordinates.
        """
        x, y = coords
        return (int(x * self.scale + self.offset_x),
                int(y * self.scale + self.offset_y))

    def draw_map(self) -> None:
        """
        Renders the connections (edges)
        and the nodes (zones) on the screen.
        """
        for zone_name, connections in self.sim.graph.adj.items():
            start_pos = self.to_screen(self.sim.graph.zones[zone_name].coords)
            for conn in connections:
                end_pos = self.to_screen(
                    self.sim.graph.zones[conn.target_zone].coords)
                pygame.draw.line(
                    self.screen, (60, 60, 60), start_pos, end_pos, 2)

        for zone in self.sim.graph.zones.values():
            pos = self.to_screen(zone.coords)
            color = self.sim.color.get_rgb(zone.color)

            pygame.draw.circle(self.screen, color, pos, 15)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 15, 2)

            label = self.font.render(
                f"{zone.name} ({zone.max_drones})", True, (200, 200, 200))
            self.screen.blit(label, (pos[0] - 20, pos[1] + 20))

    def draw_drones(self) -> None:
        """
        Draws active drones and updates their
        color based on their current state.
        """
        for drone in self.sim.drones:
            if not drone.is_active:
                continue

            pos = self.to_screen(
                self.sim.graph.zones[drone.current_zone].coords)

            # Paint in diiferent color if movement is forbidden
            color = (255, 255, 255) if drone.state == "idle" else (255, 0, 0)
            pygame.draw.circle(self.screen, color, pos, 8)

            id_tag = self.font.render(f"D{drone.id}", True, (0, 0, 0))
            self.screen.blit(id_tag, (pos[0] - 5, pos[1] - 7))

    def run_step(self) -> None:
        """
        Executes a visual refresh cycle, updating the current frame.
        """
        self.screen.fill((20, 20, 20))

        self.draw_map()
        self.draw_drones()

        pygame.display.flip()
        # fps
        self.clock.tick(10)
