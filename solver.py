"""
MAPF Solver - Integration of CBS algorithm with A* for microfluidic pathfinding.
"""
from typing import Dict, List, Tuple, Optional
import time

from grid import MicrofluidicGrid, Droplet, Direction
from cbs import ConflictBasedSearch
from collision import CollisionDetector


class MAPFSolver:
    """Multi-Agent Pathfinding solver combining CBS and A*."""

    def __init__(self, grid: MicrofluidicGrid, droplets: List[Droplet]):
        """
        Initialize the MAPF solver.
        
        Args:
            grid: The microfluidic grid
            droplets: List of droplets to route
        """
        self.grid = grid
        self.droplets = droplets
        self.cbs = ConflictBasedSearch(grid, droplets)
        self.solution = None
        self.solve_time = 0

    def solve(self, max_time: int = 100) -> bool:
        start_time = time.time()
        self.solution = self.cbs.solve(max_time)
        self.solve_time = time.time() - start_time
        return self.solution is not None

    def get_solution(self) -> Optional[Dict[Droplet, List[Tuple[int, int]]]]:
        """Get the solution paths."""
        return self.solution

    def get_position_at_time(self, droplet: Droplet, t: int) -> Optional[Tuple[int, int]]:
        if self.solution is None or droplet not in self.solution:
            return None
        
        path = self.solution[droplet]
        if t < len(path):
            return path[t]
        else:
            return path[-1] if path else None

    def get_max_time(self) -> int:
        """Get the maximum time the solution takes."""
        if self.solution is None:
            return 0
        return max(len(path) for path in self.solution.values())

    def verify_solution(self) -> Tuple[bool, List[str]]:
        if self.solution is None:
            return False, ["No solution found"]

        errors = []

    
        for droplet, path in self.solution.items():
            if path[-1] != droplet.goal:
                errors.append(f"Droplet {droplet.id} doesn't reach goal: {path[-1]} != {droplet.goal}")

        # Check for collisions
        if CollisionDetector.has_collisions(self.solution):
            errors.append("Solution contains collisions")

        return len(errors) == 0, errors

    def print_solution_summary(self):
        """Print a summary of the solution."""
        if self.solution is None:
            print("No solution found")
            return

        print(f"\n{'='*60}")
        print(f"MAPF Solution Summary")
        print(f"{'='*60}")
        print(f"Number of droplets: {len(self.droplets)}")
        print(f"Grid size: {self.grid.width} x {self.grid.height}")
        print(f"Solve time: {self.solve_time:.3f} seconds")
        print(f"Maximum path length: {self.get_max_time()} time steps")
        print(f"\nPaths:")

        for droplet, path in self.solution.items():
            path_str = " -> ".join(str(pos) for pos in path[:5])
            if len(path) > 5:
                path_str += f" ... -> {path[-1]}"
            print(f"  Droplet {droplet.id}: {droplet.start} {path_str}")


        is_valid, errors = self.verify_solution()
        print(f"\nSolution valid: {is_valid}")
        if errors:
            for error in errors:
                print(f"  - {error}")

        print(f"{'='*60}\n")


def analyze_solution(solver: MAPFSolver):
    if solver.solution is None:
        print("No solution to analyze")
        return

    print("\n" + "="*60)
    print("DETAILED SOLUTION ANALYSIS")
    print("="*60)

    max_time = solver.get_max_time()


    intersections = {}
    for t in range(max_time):
        for droplet, path in solver.solution.items():
            if t < len(path):
                pos = path[t]
                if pos not in intersections:
                    intersections[pos] = []
                intersections[pos].append((t, droplet.id))

    # Find busiest intersections
    busy_intersections = sorted(
        [(pos, len(times)) for pos, times in intersections.items()],
        key=lambda x: x[1],
        reverse=True
    )

    print(f"\nBusiest intersections (top 5):")
    for pos, count in busy_intersections[:5]:
        print(f"  Position {pos}: {count} droplet-time visits")

    # Analyze wait actions
    wait_stats = {}
    for droplet, path in solver.solution.items():
        waits = 0
        for i in range(len(path) - 1):
            if path[i] == path[i + 1]:
                waits += 1
        wait_stats[droplet.id] = waits

    print(f"\nWait action usage:")
    total_waits = sum(wait_stats.values())
    for droplet_id, waits in sorted(wait_stats.items()):
        print(f"  Droplet {droplet_id}: {waits} wait steps")
    print(f"  Total: {total_waits} wait steps")

    print(f"{'='*60}\n")
