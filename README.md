This project has been created as part of the 42 curriculum by gumunoz.

Description
-----------

**Fly-in** is a turn-based drone fleet simulation designed to manage the logistics of multiple UAVs navigating through a complex network of zones. The primary goal is to transport a specific number of drones from a **start\_hub** to an **end\_hub** in the fewest number of turns possible.

The simulation handles various environmental constraints, including:

*   **Zone Capacities:** Each hub has a maximum limit of drones it can hold simultaneously.
    
*   **Link Capacities:** Connections between zones limit the flow of traffic per turn.
    
*   **Zone Types:** Drones must adapt their behavior based on whether a zone is _Normal_, _Priority_ (lower movement cost), or _Restricted_ (requires an extra turn to enter).
    

Algorithm and Implementation Strategy
-------------------------------------

### Graph Representation

The environment is modeled as a **Directed/Undirected Graph** where:

*   **Nodes (Zones):** Store metadata such as coordinates, color, type, and capacity.
    
*   **Edges (Connections):** Represent the physical paths between hubs, each with its own throughput capacity.
    

### Pathfinding: Dijkstra with Penalties

To avoid "traffic jams" where all drones attempt to take the single shortest path, the project implements a **Multi-path Dijkstra Algorithm**.

1.  **Initial Search:** The algorithm finds the absolute shortest path based on zone costs (e.g., Priority zones = 0.5, Restricted = 2.0).
    
2.  **Dynamic Penalization:** Once a path is found, the algorithm temporarily increases the "cost" of the nodes used in that path.
    
3.  **Alternative Discovery:** Subsequent searches for the remaining drones will then prefer alternative routes, naturally distributing the fleet across the map to maximize total throughput.
    
4.  ShutterstockExplorar
    

### Turn-Based Scheduler

The core logic resides in a scheduler that executes every turn. It prioritizes drones based on their proximity to the goal and state. It handles the **Restricted Zone State Machine**:

*   **Turn N:** Drone moves to the connection (entering state moving\_restricted).
    
*   **Turn N+1:** Drone completes the move and enters the hub.
    

Visual Representation
---------------------

The project features a real-time GUI built with **Pygame** that serves as more than just a "pretty display"—it is a critical debugging and monitoring tool.

*   **Dynamic Hub Rendering:** Zones change color and display real-time occupancy vs. capacity.
    
*   **Traffic Visualization:** Drone movements are smoothed out visually to help the user identify bottlenecks in the network topology.
    
*   **State Indicators:** Drones change color based on their current state (Idle vs. Moving), allowing for immediate identification of "stuck" drones due to capacity limits.
    

Instructions
------------

### Prerequisites

*   Python 3.10+
    
*   Pygame library
    
*   MyPy (for type checking)
    

### Installation

1.  Clone the repository.
    
2.  Bashpip install pygame
    

### Execution

Run the simulation by providing a map file as the first argument:

Bash

`python3 main.py maps/03_ultimate_challenge.txt`

Resources
---------

*   **Graph Theory:** Introduction to Dijkstra's Algorithm (Red Blob Games).
    
*   **Pygame Documentation:** Official guides for surface rendering and event loops.
    
*   **PEP 8 & Type Hinting:** Python documentation on typing and flake8 standards.
    

### Use of AI

AI (Large Language Models) was utilized in this project for the following tasks:

*   **Type Safety:** Assisting in the implementation of comprehensive mypy type annotations across the codebase to ensure robust data handling.
    
*   **Refactoring:** Optimizing the Dijkstra implementation to include penalty logic for multi-pathing.
    
*   **Linter Compliance:** Assisting in formatting the code to strictly adhere to flake8 standards without compromising logic structure.
    
*   **Documentation:** Generating the initial structure of the technical documentation.