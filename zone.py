from typing import Dict, List
from enum import Enum
from drone import Drone
import heapq


class TypeZone(Enum):
    priority = 1
    normal = 2
    restricted = 3
    blocked = 4


class Zone():
    def __init__(self, coords: tuple[int, int],
                 name: str, color: str,
                 type_zone: TypeZone, max_drones: int,
                 real_drones: int) -> None:
        self.coords = coords
        self.name = name
        self.color = color
        self.type = type_zone
        self.max_drones = max_drones
        self.real_drones = real_drones

    def is_accesible(self) -> bool:
        return self.type != TypeZone.blocked


class Connection():
    def __init__(self, target_zone: str, max_capacity: int) -> None:
        self.target_zone = target_zone
        self.max_capacity = max_capacity
        self.current_flow = 0


class Graph():
    """
    contiene diccionarios de zonas, lista de drones
    y se encarga de ejecutar los turnos
    """
    def __init__(self):
        self.zones: Dict[str, Zone] = {}
        self.adj: Dict[str, List[Connection]] = {}
        self.drones: List[Drone] = []

    def add_zone(self, zone: Zone):
        self.zones[zone.name] = zone
        if zone.name not in self.adj:
            self.adj[zone.name] = []

    def add_connection(self, zone_a: str, zone_b: str, capacity: int):
        self.adj[zone_a].append(Connection(zone_b, capacity))
        self.adj[zone_b].append(Connection(zone_a, capacity))

    def find_multiple_paths(self,
                            start: str, end: str,
                            max_paths: int = 3) -> list[list[str]]:
        """
        Encuentra varias rutas alternativas para distribuir a la flota.
        """
        all_paths = []
        # Usamos un diccionario de penalizaciones temporales
        penalties = {name: 1.0 for name in self.zones}

        for _ in range(max_paths):
            # Ejecutamos Dijkstra pasando las penalizaciones actuales
            path = self.dijkstra_with_penalties(start, end, penalties)
            if not path:
                break

            all_paths.append(path)

            # PENALIZACIÓN: Subimos el coste de las zonas usadas para que la
            # siguiente búsqueda prefiera caminos nuevos.
            for node in path:
                if node != start and node != end:
                    penalties[node] += 5.0  # Un coste alto para forzar desvíos

        return all_paths

    def assign_drones_to_paths(self, drones: list, paths: list[list[str]],
                               start_node: str):
        """
        Reparte los drones entre las rutas disponibles de forma equilibrada.
        """
        for i, drone in enumerate(drones):
            # Reparto cíclico (Round Robin) - simple y efectivo para empezar
            path_index = i % len(paths)
            # Le damos al dron su hoja de ruta (quitando el nodo de inicio)
            drone.route = paths[path_index][1:]
            drone.current_zone = start_node
            drone.state = "idle"

    def get_link_capacity(self, zone_a: str, zone_b: str) -> int:
        """Busca la capacidad máxima de la conexión entre dos zonas."""
        for conn in self.adj.get(zone_a, []):
            if conn.target_zone == zone_b:
                return conn.max_capacity
        return 1  # Capacidad por defecto

    def dijkstra_with_penalties(self, start: str, end: str,
                                penalties: dict) -> list[str]:
        """Dijkstra que considera el tipo de zona
        y las penalizaciones de tráfico."""
        distances = {name: float('inf') for name in self.zones}
        distances[start] = 0
        previous = {name: None for name in self.zones}
        pq = [(0, start)]

        while pq:
            curr_dist, curr_name = heapq.heappop(pq)
            if curr_name == end:
                break
            if curr_dist > distances[curr_name]:
                continue

            for conn in self.adj.get(curr_name, []):
                neighbor = self.zones[conn.target_zone]
                if not neighbor.is_accesible():
                    continue

                # Coste base por tipo de zona
                base_cost = 1.0
                if neighbor.type == TypeZone.priority:
                    base_cost = 0.5
                elif neighbor.type == TypeZone.restricted:
                    base_cost = 2.0

                # Multiplicamos por la penalización de 'ruta ya usada'
                cost = base_cost * penalties[neighbor.name]
                new_dist = curr_dist + cost

                if new_dist < distances[neighbor.name]:
                    distances[neighbor.name] = new_dist
                    previous[neighbor.name] = curr_name
                    heapq.heappush(pq, (new_dist, neighbor.name))

        path = []
        curr = end
        while curr:
            path.append(curr)
            curr = previous[curr]
        return path[::-1] if distances[end] != float('inf') else []
