"""
Test Cases and Advanced Examples for MAPF Solver
"""

# Example 1: Custom Scenario with Obstacles
from grid import MicrofluidicGrid, Droplet
from solver import MAPFSolver, analyze_solution

def advanced_example_1():
    """
    Example: Maze-like structure with narrow passages.
    """
    print("\n" + "="*60)
    print("ADVANCED EXAMPLE 1: Maze-Like Microfluidic Structure")
    print("="*60)
    
    # Create grid with maze-like structure
    grid = MicrofluidicGrid(width=12, height=12)
    
    # Add obstacles forming a maze
    maze_walls = [
        # Vertical walls
        (3, 2), (3, 3), (3, 4), (3, 5),
        (6, 6), (6, 7), (6, 8), (6, 9),
        (9, 2), (9, 3), (9, 4), (9, 5),
        # Horizontal walls
        (2, 6), (3, 6), (4, 6),
        (7, 4), (8, 4), (9, 4),
    ]
    
    for wall in maze_walls:
        grid.add_obstacle(wall)
    
    # Create droplets that must navigate maze
    droplets = [
        Droplet(id=0, start=(1, 1), goal=(10, 10)),
        Droplet(id=1, start=(10, 1), goal=(1, 10)),
        Droplet(id=2, start=(6, 1), goal=(6, 10)),
    ]
    
    solver = MAPFSolver(grid, droplets)
    success = solver.solve(max_time=150)
    
    if success:
        print("Solution found!")
        solver.print_solution_summary()
        analyze_solution(solver)
    else:
        print("No solution found")
    
    return solver


def advanced_example_2():
    
    print("\n" + "="*60)
    print("ADVANCED EXAMPLE 2: Asymmetric Routing")
    print("="*60)
    
    grid = MicrofluidicGrid(width=14, height=10)
    
    # Create droplets with vary asymmetric paths
    droplets = [
        Droplet(id=0, start=(1, 1), goal=(12, 8), color='red'),
        Droplet(id=1, start=(1, 5), goal=(12, 2), color='blue'),
        Droplet(id=2, start=(1, 9), goal=(12, 9), color='green'),
        Droplet(id=3, start=(7, 1), goal=(7, 8), color='orange'),
    ]
    
    # Solve
    solver = MAPFSolver(grid, droplets)
    success = solver.solve(max_time=120)
    
    if success:
        print("✓ Solution found!")
        for i, (droplet, path) in enumerate(solver.get_solution().items()):
            print(f"  Droplet {droplet.id}: {len(path)} steps")
    
    return solver


def advanced_example_3():
    """
    Example: Dense packing scenario.
    Multiple droplets in close proximity.
    """
    print("\n" + "="*60)
    print("ADVANCED EXAMPLE 3: Dense Packing")
    print("="*60)
    
    grid = MicrofluidicGrid(width=8, height=8)
    
    # Create droplets in grid pattern (dense packing)
    droplets = [
        Droplet(id=0, start=(1, 1), goal=(6, 6)),
        Droplet(id=1, start=(6, 1), goal=(1, 6)),
        Droplet(id=2, start=(1, 6), goal=(6, 1)),
        Droplet(id=3, start=(6, 6), goal=(1, 1)),
    ]
    
    # Solve
    solver = MAPFSolver(grid, droplets)
    success = solver.solve(max_time=100)
    
    if success:
        print("Solution found with dense interactions!")
        solution = solver.get_solution()
        
        # Analyze interference
        max_time = solver.get_max_time()
        overlaps = {}
        
        for t in range(max_time):
            positions = [solver.get_position_at_time(d, t) for d in droplets]
            for i, pos in enumerate(positions):
                if pos and positions.count(pos) > 1:
                    overlaps[t] = overlaps.get(t, 0) + 1
        
        if overlaps:
            print(f"  Collision attempts prevented: {len(overlaps)} time steps")
        else:
            print(f"  No collisions!")
    
    return solver


def stress_test_1():
    """
    Stress test: Large grid with many droplets.
    """
    print("\n" + "="*60)
    print("STRESS TEST 1: Large Grid, Many Droplets")
    print("="*60)
    
    grid = MicrofluidicGrid(width=25, height=25)
    
    # Create many droplets
    droplets = []
    droplet_id = 0
    
    # Create droplets in a grid pattern
    for x in range(2, 22, 5):
        for y in range(2, 22, 5):
            goal_x = 24 - x
            goal_y = 24 - y
            droplets.append(
                Droplet(id=droplet_id, start=(x, y), goal=(goal_x, goal_y))
            )
            droplet_id += 1
    
    print(f"  Grid: 25x25")
    print(f"  Droplets: {len(droplets)}")
    
    solver = MAPFSolver(grid, droplets)
    success = solver.solve(max_time=200)
    
    if success:
        print(f"Solution found in {solver.solve_time:.3f} seconds")
        print(f"Max path length: {solver.get_max_time()} steps")
    else:
        print("No solution found within timeout")
    
    return solver


def stress_test_2():
    """
    Stress test: Grid with many obstacles and narrow passages.
    """
    print("\n" + "="*60)
    print("STRESS TEST 2: Complex Obstacles, Narrow Passages")
    print("="*60)
    
    grid = MicrofluidicGrid(width=20, height=20)
    
    for i in range(5, 20, 2):
        for j in range(5):
            grid.add_obstacle((i, j))
            grid.add_obstacle((j, i))
    
    
    droplets = [
        Droplet(id=0, start=(1, 1), goal=(18, 18)),
        Droplet(id=1, start=(18, 1), goal=(1, 18)),
        Droplet(id=2, start=(1, 18), goal=(18, 1)),
        Droplet(id=3, start=(10, 10), goal=(10, 1)),
    ]
    
    print(f"  Grid: 20x20 with {len(grid.obstacles)} obstacles")
    print(f"  Droplets: {len(droplets)}")
    
    solver = MAPFSolver(grid, droplets)
    success = solver.solve(max_time=250)
    
    if success:
        print(f" Solution found in {solver.solve_time:.3f} seconds")
        is_valid, errors = solver.verify_solution()
        print(f"  Valid: {is_valid}")
        if errors:
            for error in errors:
                print(f"    - {error}")
    else:
        print(" No solution found")
    
    return solver

def run_all_examples():
    """Run all advanced examples and tests."""
    print("\n" + "="*70)
    print("ADVANCED EXAMPLES AND STRESS TESTS")
    print("="*70)
    
    results = {}
    
    # Advanced examples
    print("\n### ADVANCED EXAMPLES ###\n")
    
    try:
        print("Running Example 1...")
        solver1 = advanced_example_1()
        results['Example 1: Maze'] = solver1.get_solution() is not None
    except Exception as e:
        print(f"Error: {e}")
        results['Example 1: Maze'] = False
    
    try:
        print("\nRunning Example 2...")
        solver2 = advanced_example_2()
        results['Example 2: Asymmetric'] = solver2.get_solution() is not None
    except Exception as e:
        print(f"Error: {e}")
        results['Example 2: Asymmetric'] = False
    
    try:
        print("\nRunning Example 3...")
        solver3 = advanced_example_3()
        results['Example 3: Dense'] = solver3.get_solution() is not None
    except Exception as e:
        print(f"Error: {e}")
        results['Example 3: Dense'] = False
    
    # Stress tests
    print("\n### STRESS TESTS ###\n")
    
    try:
        print("Running Stress Test 1...")
        solver_s1 = stress_test_1()
        results['Stress 1: Large Grid'] = solver_s1.get_solution() is not None
    except Exception as e:
        print(f"Error: {e}")
        results['Stress 1: Large Grid'] = False
    
    try:
        print("\nRunning Stress Test 2...")
        solver_s2 = stress_test_2()
        results['Stress 2: Complex Obstacles'] = solver_s2.get_solution() is not None
    except Exception as e:
        print(f"Error: {e}")
        results['Stress 2: Complex Obstacles'] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
    
    print("\n" + "="*70 + "\n")
    
    return results


# Performance comparison
def performance_comparison():
    """Compare performance across different grid sizes."""
    print("\n" + "="*60)
    print("PERFORMANCE COMPARISON")
    print("="*60)
    print(f"{'Grid Size':<15} {'Droplets':<15} {'Time (ms)':<15} {'Status':<15}")
    print("-" * 60)
    
    test_configs = [
        (8, 8, 2),
        (10, 10, 3),
        (15, 15, 5),
        (20, 20, 6),
    ]
    
    for width, height, num_droplets in test_configs:
        grid = MicrofluidicGrid(width, height)
        
        # Create droplets in spiral pattern
        droplets = []
        for i in range(num_droplets):
            angle = (i * 360) / num_droplets
            import math
            x = int(width / 2 + (width / 4) * math.cos(math.radians(angle)))
            y = int(height / 2 + (height / 4) * math.sin(math.radians(angle)))
            goal_x = width - 1 - x
            goal_y = height - 1 - y
            droplets.append(Droplet(id=i, start=(x, y), goal=(goal_x, goal_y)))
        
        solver = MAPFSolver(grid, droplets)
        success = solver.solve(max_time=200)
        
        time_ms = solver.solve_time * 1000
        status = "Solved" if success else "Failed"
        
        print(f"{width}x{height}:<15 {num_droplets}:<15 {time_ms:>12.2f}ms  {status:<15}")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("ADVANCED TEST SUITE FOR MAPF MICROFLUIDIC SOLVER")
    print("="*70)
    
    # Run all tests
    results = run_all_examples()
    
    # Performance analysis
    performance_comparison()
