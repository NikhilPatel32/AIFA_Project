"""
Collision detection for droplets on the microfluidic grid.
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from grid import Droplet


@dataclass
class Collision:
    droplet_a: Droplet
    droplet_b: Droplet
    time: int
    type: str  # 'vertex' or 'edge'
    location: Tuple[int, int]


class CollisionDetector:

    @staticmethod
    def detect_vertex_collision(
        paths: Dict[Droplet, List[Tuple[int, int]]]
    ) -> Optional[Collision]:
        max_time = max(len(path) for path in paths.values())
        
        for t in range(max_time):
            positions_at_t = {}
            
            for droplet, path in paths.items():
                if t < len(path):
                    pos = path[t]
                    if pos not in positions_at_t:
                        positions_at_t[pos] = []
                    positions_at_t[pos].append(droplet)
            
            # Check for collisions
            for pos, droplets in positions_at_t.items():
                if len(droplets) > 1:
                    return Collision(
                        droplet_a=droplets[0],
                        droplet_b=droplets[1],
                        time=t,
                        type='vertex',
                        location=pos
                    )
        
        return None

    @staticmethod
    def detect_edge_collision(
        paths: Dict[Droplet, List[Tuple[int, int]]]
    ) -> Optional[Collision]:
        """
        Detect edge collisions (two droplets swapping positions in adjacent time steps).
        This prevents droplets from "phasing through" each other.
        
        Args:
            paths: Dictionary mapping droplets to their paths
        
        Returns:
            First collision found, or None if no collisions
        """
        max_time = max(len(path) for path in paths.values()) - 1
        droplet_list = list(paths.keys())
        
        for t in range(max_time):
            for i, droplet_a in enumerate(droplet_list):
                for droplet_b in droplet_list[i + 1:]:
                    path_a = paths[droplet_a]
                    path_b = paths[droplet_b]
                    
                    if t + 1 < len(path_a) and t + 1 < len(path_b):
                        pos_a_t = path_a[t]
                        pos_a_next = path_a[t + 1]
                        pos_b_t = path_b[t]
                        pos_b_next = path_b[t + 1]
                        
                        # Check if they swapped
                        if pos_a_t == pos_b_next and pos_b_t == pos_a_next:
                            return Collision(
                                droplet_a=droplet_a,
                                droplet_b=droplet_b,
                                time=t,
                                type='edge',
                                location=pos_a_t
                            )
        
        return None

    @staticmethod
    def check_all_collisions(
        paths: Dict[Droplet, List[Tuple[int, int]]]
    ) -> List[Collision]:
        collisions = []
        
        # Check vertex collisions
        vertex_collision = CollisionDetector.detect_vertex_collision(paths)
        if vertex_collision:
            collisions.append(vertex_collision)
        
        # Check edge collisions
        edge_collision = CollisionDetector.detect_edge_collision(paths)
        if edge_collision:
            collisions.append(edge_collision)
        
        return collisions

    @staticmethod
    def has_collisions(paths: Dict[Droplet, List[Tuple[int, int]]]) -> bool:
        return CollisionDetector.detect_vertex_collision(paths) is not None or \
               CollisionDetector.detect_edge_collision(paths) is not None
