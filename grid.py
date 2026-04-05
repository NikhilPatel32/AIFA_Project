"""
Grid and Droplet representations for microfluidic pathfinding.
"""
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Set, Optional


class Direction(Enum):
    NORTH = (0, 1)
    SOUTH = (0, -1)
    EAST = (1, 0)
    WEST = (-1, 0)
    WAIT = (0, 0)

    def get_offset(self) -> Tuple[int, int]:
        return self.value


@dataclass
class Droplet:
    id: int
    start: Tuple[int, int]
    goal: Tuple[int, int]
    color: str = "blue"

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        if not isinstance(other, Droplet):
            return False
        return self.id == other.id


class MicrofluidicGrid:
    """Represents the microfluidic grid with obstacles and valid coordinates."""

    def __init__(self, width: int, height: int, obstacles: Optional[Set[Tuple[int, int]]] = None):
        self.width = width
        self.height = height
        self.obstacles = obstacles if obstacles is not None else set()

    def is_valid(self, pos: Tuple[int, int]) -> bool:
        """Check if a position is valid (within bounds and not an obstacle)."""
        x, y = pos
        return (
            0 <= x < self.width and
            0 <= y < self.height and
            pos not in self.obstacles
        )

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Get all valid neighboring positions (4-connected)."""
        x, y = pos
        neighbors = []
        
        for direction in Direction:
            if direction == Direction.WAIT:
                continue
            dx, dy = direction.get_offset()
            neighbor = (x + dx, y + dy)
            if self.is_valid(neighbor):
                neighbors.append(neighbor)
        
        # Always include WAIT action (staying in place)
        neighbors.append(pos)
        return neighbors

    def manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def add_obstacle(self, pos: Tuple[int, int]):
        """Add an obstacle at the given position."""
        if self.is_valid(pos):
            self.obstacles.add(pos)

    def remove_obstacle(self, pos: Tuple[int, int]):
        """Remove an obstacle at the given position."""
        self.obstacles.discard(pos)
