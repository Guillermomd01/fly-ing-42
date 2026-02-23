

class Drone():
    def __init__(self, id: int, mode: str = "idle",
                 turns: int = 0,
                 turns_until_arrival: int = 0) -> None:
        self.id = id
        self.state = mode
        self.turns = turns
        self.turns_until_arrival = turns_until_arrival
        self.current_zone = None
        self.route = []
        self.is_active = True
        self.target_restricted = None
        self.priority = 0

    def get_next_path_step(self) -> str:
        """Devuelve el siguiente paso en la ruta sin quitarlo."""
        return self.route[0] if self.route else None

    def move_to(self, zone_name: str):
        """Actualiza la posición tras un movimiento normal."""
        self.current_zone = zone_name
        if self.route:
            self.route.pop(0)

    def start_restricted_move(self, target_name: str):
        """Inicia la transición a zona restringida."""
        self.state = "moving_restricted"
        self.target_restricted = target_name

    def complete_move(self):
        """Finaliza el movimiento restringido."""
        self.current_zone = self.target_restricted
        self.state = "idle"
        self.target_restricted = None
        if self.route:
            self.route.pop(0)
