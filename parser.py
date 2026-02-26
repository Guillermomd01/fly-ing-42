import sys
from typing import Dict, List, Any
from zone import Zone, TypeZone, Graph
from drone import Drone


class Parser():
    """Responsible for transforming raw map files
    into a structured simulation environment.

    This class acts as the 'world-builder,' surgically extracting
    network topologies, drone fleet parameters, and metadata
    to ensure a high-fidelity logistics model.
    """
    def __init__(self, file_name: str) -> None:
        """
        Initializes the parser and triggers the automated
        world-building sequence.
        """
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.graph: Graph = Graph()
        self.start_node: str | None = None
        self.end_node: str | None = None

        self.parse()

    def _extract_metadata(self, line: str) -> Dict[str, str]:
        """
        Surgically extracts bracketed metadata to customize hub
        and link attributes.

        This method parses 'key=value' pairs within square brackets, allowing
        for dynamic property assignment like zone types, colors,
        and capacities.
        """
        if "[" not in line or "]" not in line:
            return {}

        inicio: int = line.find("[") + 1
        fin: int = line.find("]")
        content: str = line[inicio:fin]

        metadata: Dict[str, str] = {}
        for item in content.split():
            if "=" in item:
                k, v = item.split("=", 1)
                metadata[k] = v
        return metadata

    def parse(self) -> None:
        """
        Executes a rigorous line-by-line audit of the map file.

        It identifies and dispatches commands for drone counts,
        hub definitions, and network connections while filtering
        comments and invalid entries.
        """
        try:
            with open(self.file_name, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if ":" not in line:
                        self._error("Necessary ':' ", line_num)

                    prefix, rest = line.split(":", 1)
                    prefix = prefix.strip()

                    metadata: Dict[str, str] = self._extract_metadata(rest)
                    pos_bracket: int = rest.find("[")
                    payload: str = rest[
                        :pos_bracket] if pos_bracket != -1 else rest
                    data_list: List[str] = payload.strip().split()

                    if prefix == "nb_drones":
                        self._handle_nb_drones(data_list, line_num)

                    elif prefix in ["hub", "start_hub", "end_hub"]:
                        self._handle_hub(prefix, data_list, metadata, line_num)

                    elif prefix == "connection":
                        self._handle_connection(data_list, metadata, line_num)

            self._final_check()

        except FileNotFoundError:
            print(f"Error: File '{self.file_name}' dosen't exist.")
            sys.exit(1)

    def _handle_nb_drones(self, data: List[str], line_num: int) -> None:
        """
        Processes and validates the total drone count for the mission.

        Initializes the fleet within the graph using a standardized
        'waiting' state to prepare for strategic deployment.
        """
        try:
            count: int = int(data[0])
            if count <= 0:
                raise ValueError
            self.nb_drones = count
            self.graph.drones = [
                Drone(id=i, mode="waiting", turns=0, turns_until_arrival=0)
                for i in range(1, count + 1)]
        except (ValueError, IndexError):
            self._error("nb_drones must be positive integer", line_num)

    def _handle_hub(self, prefix: str,
                    data: List[str], meta: Dict[str, str],
                    line_num: int) -> None:
        if len(data) < 3:
            self._error("Invalid format hub (necesary x y)", line_num)

        name: str = data[0]
        x: str = data[1]
        y: str = data[2]
        if "-" in name:
            self._error(f"Name zone invalid '{name}': not '-'", line_num)

        type_mapping: Dict[str, TypeZone] = {
            "priority": TypeZone.priority,
            "restricted": TypeZone.restricted,
            "blocked": TypeZone.blocked,
            "normal": TypeZone.normal
        }
        z_type: TypeZone = type_mapping.get(
            meta.get("zone", "normal"), TypeZone.normal)

        new_zone: Zone = Zone(
            coords=(int(x), int(y)),
            name=name,
            color=meta.get("color", "white"),
            type_zone=z_type,
            max_drones=int(meta.get("max_drones", 1)),
            real_drones=0
        )
        if new_zone.max_drones <= 0:
            self._error("Max drones must be greater than 0", line_num)
        self.graph.add_zone(new_zone)

        if prefix == "start_hub":
            if self.start_node:
                self._error("Only one a start_hub", line_num)
            self.start_node = name
        elif prefix == "end_hub":
            if self.end_node:
                self._error("Only one a end_hub", line_num)
            self.end_node = name

    def _handle_connection(self, data: List[str],
                           meta: Dict[str, str],
                           line_num: int) -> None:
        """
        Establishes bidirectional flight corridors between hubs.

        Configures the 'max_link_capacity' to ensure the simulation
        respects the physical flow limits of the network.
        """
        if not data or "-" not in data[0]:
            self._error("Invalid format (A-B)", line_num)

        nodes: List[str] = data[0].split("-")
        z1: str = nodes[0]
        z2: str = nodes[1]
        if z1 not in self.graph.zones or z2 not in self.graph.zones:
            self._error(
                f"Conexion failed: ({z1} or {z2}) dosen't exist", line_num)

        capacity: int = int(meta.get("max_link_capacity", 1))
        self.graph.add_connection(z1, z2, capacity)

    def _final_check(self) -> None:
        """
        Performs a final safety audit to verify simulation readiness.

        Ensures that both entry and exit hubs are defined and
        that the drone fleet is properly registered before launch.
        """
        if not self.start_node or not self.end_node:
            print("Error:  'start_hub' and 'end_hub'.")
            sys.exit(1)
        if self.nb_drones <= 0:
            print("Error: There are not drones for missioon.")
            sys.exit(1)

    def _error(self, message: str, line_num: int) -> Any:
        """
        Centralized error reporter that terminates
        the process on critical failures.
        """
        print(f"Error in line {line_num}: {message}")
        sys.exit(1)
