"""
Conflict-Based Search (CBS) algorithm 
"""
from typing import Dict, List, Tuple, Optional, Set
from copy import deepcopy
import heapq
from dataclasses import dataclass, field

from grid import MicrofluidicGrid, Droplet
from astar import AStar
from collision import CollisionDetector, Collision


@dataclass(order=True)
class CBSNode:
    cost: int
    id: int = field(compare=False)
    paths: Dict[Droplet, List[Tuple[int, int]]] = field(default_factory=dict, compare=False)
    constraints: Set[Tuple] = field(default_factory=set, compare=False)
    collisions: List[Collision] = field(default_factory=list, compare=False)


class ConflictBasedSearch:
    """
    Conflict-Based Search (CBS) algorithm.
    High-level: Manages constraint satisfaction and resolves conflicts.
    Low-level: Uses A* for individual droplet pathfinding.
    """

    def __init__(self, grid: MicrofluidicGrid, droplets: List[Droplet], max_iterations: int = 1000):
        
        self.grid = grid
        self.droplets = droplets
        self.max_iterations = max_iterations
        self.astar = AStar(grid)
        self.node_counter = 0

    def low_level_search(
        self,
        droplet: Droplet,
        constraints: Set[Tuple]
    ) -> Optional[List[Tuple[int, int]]]:
        # Convert constraints to dictionary format for A*
        constraint_dict = {}
        for x, y, t in constraints:
            constraint_dict[(x, y, t)] = True
        
        # Find path using A* with constraints
        path = self.astar.find_path(
            droplet.start,
            droplet.goal,
            max_time=100,
            constraints=constraint_dict
        )
        
        return path

    def extract_constraints(self, collision: Collision) -> Tuple[Set[Tuple], Set[Tuple]]:
        """
        Extract constraints from a collision.
        Creates two constraint sets: one for each droplet involved.
        
        Args:
            collision: The collision to resolve
        """
        constraints_a = set()
        constraints_b = set()
        
        x, y = collision.location
        t = collision.time
        
        if collision.type == 'vertex':
            # Vertex collision: prevent both from being at (x, y, t)
            constraints_a.add((x, y, t))
            constraints_b.add((x, y, t))
        
        elif collision.type == 'edge':
            # Edge collision: prevent swap
            constraints_a.add((x, y, t))
            constraints_b.add((x, y, t))
        
        return constraints_a, constraints_b

    def solve(self, max_time: int = 100) -> Optional[Dict[Droplet, List[Tuple[int, int]]]]:
       
        # Initial low-level search (no constraints)
        initial_paths = {}
        for droplet in self.droplets:
            path = self.low_level_search(droplet, set())
            if path is None:
                return None  # No individual path found
            initial_paths[droplet] = path
        
        # Create initial CBS node
        initial_cost = sum(len(path) for path in initial_paths.values())
        root_node = CBSNode(
            cost=initial_cost,
            id=self.node_counter,
            paths=initial_paths,
            constraints=set()
        )
        self.node_counter += 1
        
        open_set = [root_node]
        closed_set = []
        
        iteration = 0
        while open_set and iteration < self.max_iterations:
            iteration += 1
            
            # Get best node
            current = heapq.heappop(open_set)
            closed_set.append(current)
            
            # Check for collisions
            detector = CollisionDetector()
            collision = detector.detect_vertex_collision(current.paths)
            
            if collision is None:
                collision = detector.detect_edge_collision(current.paths)
            
            if collision is None:
                # No collision found - solution found!
                return current.paths
            
            # Split on conflict
            constraints_a, constraints_b = self.extract_constraints(collision)
            
            # Generate two new nodes by adding constraints
            for constraints in [constraints_a, constraints_b]:
                if collision.type == 'vertex':
                    new_constraints = current.constraints | constraints
                    new_paths = deepcopy(current.paths)
                    
                    # Replan for the affected droplet
                    affected_droplet = collision.droplet_a if constraints == constraints_a else collision.droplet_b
                    new_path = self.low_level_search(affected_droplet, new_constraints)
                    
                    if new_path is not None:
                        new_paths[affected_droplet] = new_path
                        new_cost = sum(len(path) for path in new_paths.values())
                        
                        new_node = CBSNode(
                            cost=new_cost,
                            id=self.node_counter,
                            paths=new_paths,
                            constraints=new_constraints
                        )
                        self.node_counter += 1
                        heapq.heappush(open_set, new_node)
        
        return None  # No solution found
