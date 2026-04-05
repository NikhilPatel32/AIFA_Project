import heapq
from typing import List, Tuple, Dict, Optional, Set
from grid import MicrofluidicGrid, Droplet


class AStarNode:

    def __init__(self, pos: Tuple[int, int], g: int = 0, h: int = 0):
        self.pos = pos
        self.g = g
        self.h = h
        self.f = g + h
        self.parent = None

    def __lt__(self, other):
        """priority queue comparison."""
        return self.f < other.f

    def __eq__(self, other):
        return isinstance(other, AStarNode) and self.pos == other.pos

    def __hash__(self):
        return hash(self.pos)


class AStar:
    """A* pathfinding algorithm with Manhattan distance heuristic."""

    def __init__(self, grid: MicrofluidicGrid):
        self.grid = grid

    def heuristic(self, pos: Tuple[int, int], goal: Tuple[int, int]) -> int:
        return self.grid.manhattan_distance(pos, goal)

    def find_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        max_time: int = 1000,
        constraints: Optional[Dict[Tuple[int, int, int], bool]] = None
    ) -> Optional[List[Tuple[int, int]]]:
        if not self.grid.is_valid(start) or not self.grid.is_valid(goal):
            return None

        constraints = constraints or {}
        open_set = []
        start_node = AStarNode(start, g=0, h=self.heuristic(start, goal))
        heapq.heappush(open_set, start_node)

        closed_set = set()
        g_score = {start: 0}
        parent = {start: None}

        while open_set:
            current_node = heapq.heappop(open_set)
            current_pos = current_node.pos
            current_time = current_node.g

            if current_pos == goal:
                # Reconstruct path
                path = []
                pos = goal
                while pos is not None:
                    path.append(pos)
                    pos = parent[pos]
                return path[::-1]

            if current_pos in closed_set or current_time >= max_time:
                continue

            closed_set.add(current_pos)

            # Explore neighbors
            for neighbor in self.grid.get_neighbors(current_pos):
                if neighbor in closed_set:
                    continue

                next_time = current_time + 1
                
                # Check constraint
                if (neighbor[0], neighbor[1], next_time) in constraints:
                    continue

                tentative_g = g_score[current_pos] + 1

                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    g_score[neighbor] = tentative_g
                    h = self.heuristic(neighbor, goal)
                    new_node = AStarNode(neighbor, g=tentative_g, h=h)
                    heapq.heappush(open_set, new_node)
                    parent[neighbor] = current_pos

        return None  # No path found

    def find_path_with_time(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int],
        max_time: int = 1000,
        constraints: Optional[Dict] = None
    ) -> Optional[List[Tuple[int, int]]]:
        path = self.find_path(start, goal, max_time, constraints)
        
        if path is None:
            return None
        
        # Extend path to max_time by waiting at goal
        while len(path) < max_time:
            path.append(goal)
        
        return path
