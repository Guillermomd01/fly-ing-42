from typing import Dict, List, Optional, Tuple
from enum import Enum
from drone import Drone
import heapq


class TypeZone(Enum):
    """
    Categorizes zones based on their operational impact on drone navigation.

    Attributes:
        priority: Reduced cost zones that accelerate transit.
        normal: Standard zones with base movement costs.
        restricted: High-security zones requiring additional processing turns.
        blocked: No-fly zones that are completely inaccessible.
    """
    priority = 1
    normal = 2
    restricted = 3
    blocked = 4


class Zone():
    """
    Represents a resource-constrained hub within the flight network.

    This class manages the physical and logical properties of a zone,
    including its geographic location and drone occupancy limits.
    """
    def __init__(self, coords: tuple[int, int],
                 name: str, color: str,
                 type_zone: TypeZone, max_drones: int,
                 real_drones: int) -> None:
        """
        Initializes a hub with its spatial coordinates
        and operational constraints.
        """
        self.coords = coords
        self.name = name
        self.color = color
        self.type = type_zone
        self.max_drones = max_drones
        self.real_drones = real_drones

    def is_accesible(self) -> bool:
        """
        Determines if the zone is available
        for entry based on its TypeZone.
        """
        return self.type != TypeZone.blocked


class Connection():
    """
    Represents a high-throughput link between two flight hubs.

    Manages the traffic flow constraints to prevent network
    congestion.
    """
    def __init__(self, target_zone: str, max_capacity: int) -> None:
        """
        Defines a connection path towards a target
        destination with a specific capacity.
        """
        self.target_zone = target_zone
        self.max_capacity = max_capacity
        self.current_flow = 0


class Graph():
    """
    The central intelligence engine that orchestrates
    the simulation environment.

    This class manages the global topology, handlesdrone
    registration, and executes the turn-based logic for the entire fleet.
    """
    def __init__(self) -> None:
        """
        Initializes an empty flight network with
        zone and adjacency records.
        """
        self.zones: Dict[str, Zone] = {}
        self.adj: Dict[str, List[Connection]] = {}
        self.drones: List[Drone] = []

    def add_zone(self, zone: Zone) -> None:
        """
        Registers a new hub into the network's spatial registry.
        """
        self.zones[zone.name] = zone
        if zone.name not in self.adj:
            self.adj[zone.name] = []

    def add_connection(self, zone_a: str, zone_b: str, capacity: int) -> None:
        """
        Establishes a bidirectional link between two hubs
        with shared throughput limits.
        """
        self.adj[zone_a].append(Connection(zone_b, capacity))
        self.adj[zone_b].append(Connection(zone_a, capacity))

    def find_multiple_paths(self,
                            start: str, end: str,
                            max_paths: int = 3) -> list[list[str]]:
        """
        Calculates alternative routes to maximize fleet distribution
        and avoid bottlenecks.

        This method uses a penalization strategy to force the discovery
        of secondary paths, ensuring the fleet doesn't overwhelm a
        single corridor.
        """
        all_paths: list[list[str]] = []
        # Use a dict for temporal penalties
        penalties: Dict[str, float] = {name: 1.0 for name in self.zones}

        for _ in range(max_paths):
            # Execute Dijkstra with penalties
            path: list[str] = self.dijkstra_with_penalties(
                start, end, penalties)
            if not path:
                break

            all_paths.append(path)

            # Penalty: grow up restrictions for Dijkstra
            # choose another solution
            for node in path:
                if node != start and node != end:
                    penalties[node] += 5.0

        return all_paths

    def assign_drones_to_paths(self, drones: List[Drone],
                               paths: list[list[str]],
                               start_node: str) -> None:
        """
        Strategically distributes drones across discovered
        routes using a Round Robin approach.
        """
        for i, drone in enumerate(drones):
            path_index = i % len(paths)
            # Give each drone his roadap
            drone.route = paths[path_index][1:]
            drone.current_zone = start_node
            drone.state = "idle"

    def get_link_capacity(self, zone_a: str, zone_b: str) -> int:
        """
        Retrieves the maximum throughput allowed between
        two specific hubs.
        """
        for conn in self.adj.get(zone_a, []):
            if conn.target_zone == zone_b:
                return conn.max_capacity
        return 1

    def dijkstra_with_penalties(self, start: str, end: str,
                                penalties: Dict[str, float]
                                ) -> list[str]:
        """
        Calculates the optimal path considering zone types,
        costs, and dynamic congestion penalties.

        This advanced pathfinding logic balances speed and network health by
        weighting priority zones and restricted airspaces differently.
        """
        distances: Dict[str, float] = {
            name: float('inf') for name in self.zones}
        distances[start] = 0
        previous: Dict[str, Optional[str]] = {
            name: None for name in self.zones}
        pq: List[Tuple[float, str]] = [(0.0, start)]

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

                # Cost depends zone
                base_cost = 1.0
                if neighbor.type == TypeZone.priority:
                    base_cost = 0.5
                elif neighbor.type == TypeZone.restricted:
                    base_cost = 2.0

                # Multiply penalties
                cost = base_cost * penalties[neighbor.name]
                new_dist = curr_dist + cost

                if new_dist < distances[neighbor.name]:
                    distances[neighbor.name] = new_dist
                    previous[neighbor.name] = curr_name
                    heapq.heappush(pq, (new_dist, neighbor.name))

        path: list[str] = []
        curr: Optional[str] = end
        while curr:
            path.append(curr)
            curr = previous[curr]
        return path[::-1] if distances[end] != float('inf') else []
