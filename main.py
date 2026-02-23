import sys
try:
    from parser import Parser
    from simulation import Simulation
    from utils import Colors
    from visualizer import DroneVisualizer
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
    sim.run()
    print("\n--- MISIÓN COMPLETADA ---")
    visualizer = DroneVisualizer(sim)
    running = True
    paused = True # Empezamos pausados para ver el mapa
    print("Presiona ESPACIO para avanzar turno a turno o ESC para salir.")

    while running and sim.drones_delivered < sim.nb_drones:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # AVANZAR UN TURNO
                    moves = sim.calculate_turn_moves()
                    # Aquí llamarías a la lógica de actualización de posiciones que tienes en simulation.py
                    # (Asegúrate de que calculate_turn_moves() ejecute los cambios en los objetos drone)
                    print(f"Turno procesado. Drones entregados: {sim.drones_delivered}")

        visualizer.run_step()

    pygame.quit()

if __name__ == "__main__":
    main()
