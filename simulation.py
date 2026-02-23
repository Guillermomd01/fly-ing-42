from zone import Graph, TypeZone
from utils import Colors

class Simulation:
    def __init__(self, color: Colors, graph: Graph, nb_drones: int,
                 start: str, end: str):
        self.color = color
        self.graph = graph
        self.nb_drones = nb_drones
        self.start_node = start
        self.end_node = end
        self.drones_delivered = 0
        self.drones = self.graph.drones

    def run(self):
        """Ejecuta el bucle principal de la simulación."""
        moves_i = 0
        while self.drones_delivered < self.nb_drones:
            turn_movements = []

            # 1. Identificar movimientos para este turno
            # El scheduler decide qué drones se mueven basándose en capacidades
            moves = self.calculate_turn_moves()
            moves_i += 1
            for drone, target in moves:
                zone_color = self.graph.zones[target].color  # Obtenemos el color (red, green, etc.)
                
                if self.graph.zones[target].type == TypeZone.restricted:
                    if drone.state == "idle":
                        # Turno 1: Movimiento a conexión
                        conn_name = f"{drone.current_zone}-{target}"
                        move_str = f"D{drone.id}-{conn_name}"
                        turn_movements.append(self.color.color_text(move_str, zone_color))
                        drone.start_restricted_move(target)
                    else:
                        # Turno 2: Llegada a zona
                        move_str = f"D{drone.id}-{target}"
                        turn_movements.append(self.color.color_text(move_str, zone_color))
                        drone.complete_move()
                        if drone.current_zone == self.end_node:
                            drone.is_active = False
                            self.drones_delivered += 1
                else:
                    # Movimiento normal
                    move_str = f"D{drone.id}-{target}"
                    turn_movements.append(self.color.color_text(move_str, zone_color))
                    drone.move_to(target)
                    if drone.current_zone == self.end_node:
                        drone.is_active = False
                        self.drones_delivered += 1
            # 2. Output del turno
            if turn_movements:
                # Imprime todos los movimientos separados
                # por un espacio en una sola línea
                print(" ".join(turn_movements))
                print(moves_i)
    def calculate_turn_moves(self):
        """
        Decide qué drones se mueven este
        turno respetando todas las capacidades.
        """
        potential_moves = []
        # Usamos diccionarios temporales
        # para rastrear la ocupación EN ESTE TURNO
        # considerando los drones que entran y salen
        current_zone_occupancy = {
            name: z.real_drones for name, z in self.graph.zones.items()}
        current_link_usage = {}  # (A, B) -> drones_usando_link

        # 1. Priorizar drones: Los que ya están en
        # movimiento restringido DEBEN terminar
        for drone in self.drones:
            if drone.is_active and drone.state == "moving_restricted":
                # Estos drones no pueden esperar en la conexión
                # Asumimos que la reserva de capacidad
                # se hizo al iniciar el movimiento.
                potential_moves.append((drone, drone.target_restricted))

        # 2. Drones en espera (IDLE): Intentar moverlos por su ruta asignada.
        for drone in sorted(self.drones,
                            key=lambda d: d.priority, reverse=True):
            if not drone.is_active or drone.state == "moving_restricted":
                continue

            next_step = drone.get_next_path_step()
            if not next_step:
                continue

            # Verificación de Capacidad de Zona
            zone_aux = current_zone_occupancy[next_step]
            if zone_aux >= self.graph.zones[next_step].max_drones:
                # Espera estratégica si la zona está llena.
                continue

            # Verificación de Capacidad de Link
            link_key = tuple(sorted((drone.current_zone, next_step)))
            link_cap = self.graph.get_link_capacity(
                drone.current_zone, next_step)
            if current_link_usage.get(link_key, 0) >= link_cap:
                continue

            # Si pasa los filtros, registramos el movimiento
            # y actualizamos ocupación temporal
            potential_moves.append((drone, next_step))
            current_zone_occupancy[next_step] += 1
            current_zone_occupancy[drone.current_zone] -= 1
            current_link_usage[link_key] = current_link_usage.get(
                link_key, 0) + 1

        return potential_moves
