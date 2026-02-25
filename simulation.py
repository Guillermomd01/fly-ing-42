from zone import Graph, TypeZone
from utils import Colors
from typing import List, Tuple, Dict, Any


class Simulation:
    """
    The core execution engine for the drone fleet logistics simulation.

    This class orchestrates the life cycle of the mission, managing drone
    deployment, movement synchronization, and the monitoring of delivery
    goals while strictly enforcing environmental and physical constraints.
    """
    def __init__(self, color: Colors, graph: Graph, nb_drones: int,
                 start: str, end: str) -> None:
        """
        Initializes the simulation state with the flight network
        and mission parameters.
        """
        self.color: Colors = color
        self.graph: Graph = graph
        self.nb_drones: int = nb_drones
        self.start_node: str = start
        self.end_node: str = end
        self.drones_delivered: int = 0
        self.drones: List[Any] = self.graph.drones

    def run(self) -> None:
        """
        Executes the primary simulation loop until all drones reach
        their destination.

        This method manages the passage of time (turns), processes
        movements for normal and restricted zones, and provides
        real-time telemetry to the terminal.
        """
        moves_i: int = 0
        while self.drones_delivered < self.nb_drones:
            turn_movements: List[str] = []

            moves = self.calculate_turn_moves()
            moves_i += 1
            for drone, target in moves:
                zone_color: str = self.graph.zones[target].color

                if self.graph.zones[target].type == TypeZone.restricted:
                    if drone.state == "idle":
                        conn_name: str = f"{drone.current_zone}-{target}"
                        move_str: str = f"D{drone.id}-{conn_name}"
                        turn_movements.append(
                            self.color.color_text(move_str, zone_color))
                        drone.start_restricted_move(target)
                    else:
                        move_str = f"D{drone.id}-{target}"
                        turn_movements.append(
                            self.color.color_text(move_str, zone_color))
                        drone.complete_move()
                        if drone.current_zone == self.end_node:
                            drone.is_active = False
                            self.drones_delivered += 1
                else:
                    move_str = f"D{drone.id}-{target}"
                    turn_movements.append(
                        self.color.color_text(move_str, zone_color))
                    drone.move_to(target)
                    if drone.current_zone == self.end_node:
                        drone.is_active = False
                        self.drones_delivered += 1

            if turn_movements:
                print(" ".join(turn_movements))
                print(moves_i)

    def calculate_turn_moves(self) -> List[Tuple[Any, str]]:
        """
        Calculates valid fleet movements for the current
        turn based on resource availability.

        The scheduler prioritizes drones in transition and
        evaluates zone occupancy and link throughput capacity
        to prevent collisions and network congestion.
        """
        potential_moves: List[Tuple[Any, str]] = []
        current_zone_occupancy: Dict[str, int] = {
            name: z.real_drones for name, z in self.graph.zones.items()}
        current_link_usage: Dict[Tuple[str, ...], int] = {}

        for drone in self.drones:
            if drone.is_active and drone.state == "moving_restricted":

                potential_moves.append((drone, drone.target_restricted))

        for drone in sorted(self.drones,
                            key=lambda d: d.priority, reverse=True):
            if not drone.is_active or drone.state == "moving_restricted":
                continue

            next_step: str = drone.get_next_path_step()
            if not next_step:
                continue

            zone_aux: int = current_zone_occupancy[next_step]
            if zone_aux >= self.graph.zones[next_step].max_drones:
                continue

            link_key: Tuple[str, ...] = tuple(
                sorted((drone.current_zone, next_step)))
            link_cap: int = self.graph.get_link_capacity(
                drone.current_zone, next_step)
            if current_link_usage.get(link_key, 0) >= link_cap:
                continue

            potential_moves.append((drone, next_step))
            current_zone_occupancy[next_step] += 1
            current_zone_occupancy[drone.current_zone] -= 1
            current_link_usage[link_key] = current_link_usage.get(
                link_key, 0) + 1

        return potential_moves
