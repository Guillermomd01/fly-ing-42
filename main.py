import sys
try:
    from parser import Parser
    from simulation import Simulation
    from utils import Colors
    from visualizer import DroneVisualizer
    from zone import TypeZone
    import pygame
except ImportError as e:
    print(f"Error importing module: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    # 1. Validación de argumentos de entrada
    if len(sys.argv) != 2:
        print("Use: python3 main.py <map file.txt>")
        sys.exit(1)

    map_file = sys.argv[1]

    # 2. Fase de Parsing: Construcción del grafo y la flota
    # El Parser ya inicializa el Graph y la lista de Drones
    parser = Parser(map_file)
    graph = parser.graph
    color = Colors()

    # 3. Inteligencia de Rutas: Buscamos caminos alternativos
    # Para mapas Hard/Challenger,
    # buscamos hasta 3 rutas para repartir el tráfico
    print(f"Calculando rutas óptimas para {parser.nb_drones} drones...")
    paths = graph.find_multiple_paths(
        parser.start_node, parser.end_node, max_paths=3)

    if not paths:
        print(
            "Error: No se ha encontrado ningún camino posible hasta la meta.")
        sys.exit(1)

    # 4. Asignación Estratégica:
    # Repartimos los drones entre las rutas encontradas
    graph.assign_drones_to_paths(graph.drones, paths, parser.start_node)

    # 5. Inicialización de la Simulación
    # Pasamos el grafo ya configurado y los puntos críticos
    sim = Simulation(
        color = color,
        graph=graph,
        nb_drones=parser.nb_drones,
        start=parser.start_node,
        end=parser.end_node
    )

    # 6. ¡Despegue! Ejecución del motor de turnos y salida por pantalla
    print("\n--- INICIO DE LA SIMULACIÓN ---\n")
    #sim.run()
    print("\n--- MISIÓN COMPLETADA ---")
    visualizer = DroneVisualizer(sim)
    # ... (después de inicializar sim y visualizer)
    
    running = True
    last_update = pygame.time.get_ticks()
    update_delay = 600  # 0.6 segundos entre pasos para que dé tiempo a leer
    turn_counter = 0

    print("\n--- INICIO DE LA SIMULACIÓN AUTOMÁTICA ---\n")

    while running and sim.drones_delivered < sim.nb_drones:
        # Gestión de eventos para poder cerrar la ventana
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        now = pygame.time.get_ticks()
        
        # Lógica de Turno Automático
        if now - last_update > update_delay:
            moves = sim.calculate_turn_moves()
            turn_movements = []
            
            if moves:
                turn_counter += 1
                for drone, target in moves:
                    zone_obj = sim.graph.zones[target]
                    zone_color = zone_obj.color
                    
                    # Lógica de movimiento y construcción del texto para terminal
                    if zone_obj.type == TypeZone.restricted:
                        if drone.state == "idle":
                            # Movimiento hacia la conexión
                            move_str = f"D{drone.id}-{drone.current_zone}-{target}"
                            drone.start_restricted_move(target)
                        else:
                            # Finaliza llegada a zona
                            move_str = f"D{drone.id}-{target}"
                            drone.complete_move()
                            if drone.current_zone == sim.end_node:
                                drone.is_active = False
                                sim.drones_delivered += 1
                    else:
                        # Movimiento normal
                        move_str = f"D{drone.id}-{target}"
                        drone.move_to(target)
                        if drone.current_zone == sim.end_node:
                            drone.is_active = False
                            sim.drones_delivered += 1
                    
                    # Añadir texto coloreado para la terminal
                    turn_movements.append(sim.color.color_text(move_str, zone_color))

                # Imprimir en terminal igual que antes
                if turn_movements:
                    print(" ".join(turn_movements))
                    print(turn_counter)

            last_update = now

        # Actualizar ventana de Pygame
        visualizer.run_step()

    print(f"\n--- MISIÓN COMPLETADA: {sim.drones_delivered} DRONES ENTREGADOS ---")
    
    # Bucle final para que la ventana no se cierre sola al terminar
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        visualizer.run_step()

    pygame.quit()

if __name__ == "__main__":
    main()
