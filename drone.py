from typing import List, Optional


class Drone():
    def __init__(self, id: int, mode: str = "idle", turns: int = 0,
                 turns_until_arrival: int = 0) -> None:
        """
        Represents an autonomous agent within the logistics network.

        This class manages the drone's individual state, operational
        priority, and path execution, handling both instantaneous and
        multi-turn movements.
        """
        self.id = id
        self.state = mode
        self.turns = turns
        self.turns_until_arrival = turns_until_arrival
        self.current_zone: Optional[str] = None
        self.route: List[str] = []
        self.is_active = True
        self.target_restricted: Optional[str] = None
        self.priority = 0

    def get_next_path_step(self) -> Optional[str]:
        """
        Return at the immediate next destination in
        the drone's assigned route.
        """
        return self.route[0] if self.route else None

    def move_to(self, zone_name: str) -> None:
        """
        Updates the drone's position for standard, single-turn transitions.
        """
        self.current_zone = zone_name
        if self.route:
            self.route.pop(0)

    def start_restricted_move(self, target_name: str) -> None:
        """
        Initiates a multi-turn transition into a high-securit
          or restricted zone.

        This state locks the drone into a 'moving_restricted' mode,
        preventing other actions until the transition sequence is finalized.
        """
        self.state = "moving_restricted"
        self.target_restricted = target_name

    def complete_move(self) -> None:
        """
        Finalizes a restricted transition, updating
        the current zone and resetting state.
        """
        self.current_zone = self.target_restricted
        self.state = "idle"
        self.target_restricted = None
        if self.route:
            self.route.pop(0)
