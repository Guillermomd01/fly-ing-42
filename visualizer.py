import pygame
from typing import Any, Tuple


class DroneVisualizer:
    def __init__(self, simulation: Any, scale: int = 60) -> None:
        pygame.init()
        self.sim = simulation
        self.scale = scale
        self.offset_x = 100
        self.offset_y = 300  # Ajustamos para que el (0,0) esté centrado

        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Fly-in Drone Simulator")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 14)

    def to_screen(self, coords: Tuple[int, int]) -> Tuple[int, int]:
        """Convierte coordenadas del mapa a píxeles de pantalla."""
        x, y = coords
        return (int(x * self.scale + self.offset_x),
                int(y * self.scale + self.offset_y))

    def draw_map(self) -> None:
        # 1. Dibujar Conexiones (Líneas)
        for zone_name, connections in self.sim.graph.adj.items():
            start_pos = self.to_screen(self.sim.graph.zones[zone_name].coords)
            for conn in connections:
                end_pos = self.to_screen(
                    self.sim.graph.zones[conn.target_zone].coords)
                pygame.draw.line(
                    self.screen, (60, 60, 60), start_pos, end_pos, 2)

        # 2. Dibujar Zonas (Nodos)
        for zone in self.sim.graph.zones.values():
            pos = self.to_screen(zone.coords)
            color = self.sim.color.get_rgb(zone.color)

            # Dibujar el círculo de la zona
            pygame.draw.circle(self.screen, color, pos, 15)
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 15, 2)

            # Etiqueta de la zona y capacidad
            label = self.font.render(
                f"{zone.name} ({zone.max_drones})", True, (200, 200, 200))
            self.screen.blit(label, (pos[0] - 20, pos[1] + 20))

    def draw_drones(self) -> None:
        for drone in self.sim.drones:
            if not drone.is_active:
                continue

            # Dibujamos al dron en su zona actual
            pos = self.to_screen(
                self.sim.graph.zones[drone.current_zone].coords)

            # Si está en movimiento restringido,
            # lo pintamos un poco desplazado o diferente
            color = (255, 255, 255) if drone.state == "idle" else (255, 0, 0)
            pygame.draw.circle(self.screen, color, pos, 8)

            id_tag = self.font.render(f"D{drone.id}", True, (0, 0, 0))
            self.screen.blit(id_tag, (pos[0] - 5, pos[1] - 7))

    def run_step(self) -> None:
        """Ejecuta un turno de la simulación y lo dibuja."""
        self.screen.fill((20, 20, 20))

        self.draw_map()
        self.draw_drones()

        pygame.display.flip()
        self.clock.tick(10)  # fps
