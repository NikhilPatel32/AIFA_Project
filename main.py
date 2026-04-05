import matplotlib.pyplot as plt
from grid import MicrofluidicGrid, Droplet
from solver import MAPFSolver, analyze_solution


def create_simple_scenario():
    """Create a simple test scenario with 3 droplets."""
    
    grid = MicrofluidicGrid(width=10, height=10)

    droplets = [
        Droplet(id=0, start=(1, 1), goal=(8, 8), color='red'),
        Droplet(id=1, start=(1, 8), goal=(8, 1), color='blue'),
        Droplet(id=2, start=(5, 5), goal=(5, 1), color='green'),
    ]

    return grid, droplets


def create_complex_scenario():
    """Create a more complex scenario with obstacles and more droplets."""
    grid = MicrofluidicGrid(width=15, height=15)

    for x in range(5, 10):
        grid.add_obstacle((x, 7))
    
    for y in range(3, 7):
        grid.add_obstacle((7, y))

    droplets = [
        Droplet(id=0, start=(2, 2), goal=(12, 12), color='red'),
        Droplet(id=1, start=(2, 12), goal=(12, 2), color='blue'),
        Droplet(id=2, start=(12, 12), goal=(2, 2), color='green'),
        Droplet(id=3, start=(7, 2), goal=(7, 12), color='orange'),
        Droplet(id=4, start=(2, 7), goal=(12, 7), color='purple'),
    ]

    return grid, droplets


def create_high_throughput_scenario():
    """Create a high-throughput scenario with many droplets."""
    grid = MicrofluidicGrid(width=20, height=20)

    for x in range(0, 20, 3):
        for y in range(0, 20):
            if (x, y) != (0, 0) and (x, y) != (19, 19):
                pass

    droplets = []
    droplet_id = 0
    
    for y in range(2, 18, 3):
        goal_y = 18 - y
        droplets.append(
            Droplet(id=droplet_id, start=(1, y), goal=(18, goal_y), color='auto')
        )
        droplet_id += 1

    return grid, droplets


def run_scenario(grid: MicrofluidicGrid, droplets: list, scenario_name: str):
    """Run a complete scenario and visualize the results."""
    print(f"\n{'='*60}")
    print(f"Running scenario: {scenario_name}")
    print(f"{'='*60}")
    print(f"Grid: {grid.width} x {grid.height}")
    print(f"Droplets: {len(droplets)}")
    print(f"Obstacles: {len(grid.obstacles)}")

    solver = MAPFSolver(grid, droplets)

    print("\nSolving with CBS + A*...")
    success = solver.solve(max_time=100)

    if success:
        print(f"Solution found in {solver.solve_time:.3f} seconds")

        solver.print_solution_summary()
        analyze_solution(solver)

        solution = solver.get_solution()
        return True
    else:
        print(" No solution found")
        return False


def main():
    print("\n" + "="*60)
    print("MULTI-AGENT PATHFINDING FOR MICROFLUIDIC SYSTEMS")
    print("Conflict-Based Search (CBS) + A* Search")
    print("="*60)

    grid1, droplets1 = create_simple_scenario()
    run_scenario(grid1, droplets1, "Simple Scenario")

    grid2, droplets2 = create_complex_scenario()
    run_scenario(grid2, droplets2, "Complex Scenario with Obstacles")

    grid3, droplets3 = create_high_throughput_scenario()
    run_scenario(grid3, droplets3, "High Throughput Scenario")


def create_animated_demo():
    """Create an animated demonstration."""
    print("\nCreating animated demonstration...")
    
    grid, droplets = create_simple_scenario()
    solver = MAPFSolver(grid, droplets)
    
    if solver.solve(max_time=100):
        solution = solver.get_solution()

if __name__ == "__main__":
    main()