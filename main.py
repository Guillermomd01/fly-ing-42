import sys
try:
    from parser import Parser
    from simulation import Simulation
    from utils import Colors
    from visualizer import DroneVisualizer
    from zone import TypeZone, Zone
    from drone import Drone
    import pygame
except ImportError as e:
    print(f"Error importing module: {e}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    """Function to create main project"""
    if len(sys.argv) != 2:
        print("Use: python3 main.py <map file.txt>")
        sys.exit(1)

    map_file: str = sys.argv[1]

    parser: Parser = Parser(map_file)
    graph = parser.graph
    color: Colors = Colors()

    assert parser.start_node is not None
    assert parser.end_node is not None

    paths: list[list[str]] = graph.find_multiple_paths(
        parser.start_node, parser.end_node, max_paths=3)

    if not paths:
        print(
            "Error: No possible path to the goal has been found.")
        sys.exit(1)

    graph.assign_drones_to_paths(graph.drones, paths, parser.start_node)

    sim: Simulation = Simulation(color=color, graph=graph,
                                 nb_drones=parser.nb_drones,
                                 start=parser.start_node,
                                 end=parser.end_node)

    visualizer: DroneVisualizer = DroneVisualizer(sim)

    running: bool = True
    last_update: int = pygame.time.get_ticks()
    update_delay: int = 600
    # turn_counter = 0

    while running and sim.drones_delivered < sim.nb_drones:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        now: int = pygame.time.get_ticks()

        if now - last_update > update_delay:
            moves: list[tuple[Drone, str]] = sim.calculate_turn_moves()
            turn_movements: list[str] = []

            if moves:
                # turn_counter += 1
                for drone, target in moves:
                    zone_obj: Zone = sim.graph.zones[target]
                    zone_color: str = zone_obj.color

                    if zone_obj.type == TypeZone.restricted:
                        if drone.state == "idle":
                            move_str: str = f"D{drone.id}-{drone.current_zone}"
                            f"-{target}"
                            drone.start_restricted_move(target)
                        else:
                            move_str = f"D{drone.id}-{target}"
                            drone.complete_move()
                            if drone.current_zone == sim.end_node:
                                drone.is_active = False
                                sim.drones_delivered += 1
                    else:
                        move_str = f"D{drone.id}-{target}"
                        drone.move_to(target)
                        if drone.current_zone == sim.end_node:
                            drone.is_active = False
                            sim.drones_delivered += 1

                    turn_movements.append(
                        sim.color.color_text(move_str, zone_color))

                if turn_movements:
                    print(" ".join(turn_movements))

            last_update = now

        visualizer.run_step()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        visualizer.run_step()

    pygame.quit()


if __name__ == "__main__":
    main()
