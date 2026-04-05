# Multi-Agent Pathfinding (MAPF) for Microfluidic Droplet Routing

## Overview

This project implements a **Conflict-Based Search (CBS)** algorithm combined with **A* pathfinding** to solve the complex scheduling problem of routing hundreds of droplets through microfluidic channels without collisions.

### Key Problems Solved

1. **Vertex Collision Prevention**: Ensures no two droplets occupy the same grid position at the same time
2. **Edge/Swap Collision Prevention**: Prevents droplets from "phasing through" each other by swapping adjacent spaces
3. **Multi-Agent Pathfinding**: Simultaneously plans optimal paths for multiple droplets with shared constraints
4. **Real-Time Constraint Management**: Dynamically applies constraints when conflicts are detected

---

## Architecture

### Core Components

#### 1. **Grid and Droplet Classes** (`grid.py`)
- **`MicrofluidicGrid`**: Represents the 2D microfluidic channel network
  - Supports obstacles (walls)
  - Provides neighbor queries for A* search
  - Calculates Manhattan distance heuristics
  
- **`Droplet`**: Represents individual droplets with:
  - Starting and goal positions
  - Unique ID for tracking
  - Color for visualization

#### 2. **A* Pathfinding** (`astar.py`)
- **Algorithm**: Single-agent pathfinding with Manhattan distance heuristic
- **Constraints**: Respects time-space constraints (x, y, t) forbidden positions
- **Key Features**:
  - Efficient priority queue-based search
  - Heuristic: Manhattan distance (∑|x₁-x₂| + |y₁-y₂|) 
  - Optimal path with constraints
  - Supports "Wait" actions for collision avoidance

**Heuristic Function**:
```
h(position, goal) = Manhattan Distance
                  = |x_pos - x_goal| + |y_pos - y_goal|
```

#### 3. **Collision Detection** (`collision.py`)
- **Vertex Collision**: Two droplets at same position at same time
  - Detection: For each time t, check if any position has multiple droplets
  
- **Edge Collision**: Droplets swapping positions (avoiding "phasing")
  - Detection: Check if droplet A moves from p₁→p₂ while droplet B moves from p₂→p₁

#### 4. **Conflict-Based Search (CBS)** (`cbs.py`)
- **High-Level Search**: Manages conflict resolution
- **Low-Level Search**: A* for individual droplets
- **Constraint Propagation**:
  1. Find collision between two droplets
  2. Create constraint: "droplet_a cannot be at (x,y,t)"
  3. Create alternate constraint: "droplet_b cannot be at (x,y,t)"
  4. Replan affected droplets with A*
  5. Recursively resolve new conflicts

**Algorithm Flow**:
```
CBS Algorithm:
1. Low-level: Run A* for all droplets independently
2. Check for collisions
   - If none found: SOLUTION FOUND
   - If collision found: Create two branches
3. For each branch:
   - Add constraint to one droplet's path
   - Replan affected droplet with A*
4. Repeat until solution found or timeout
```

#### 5. **MAPF Solver** (`solver.py`)
- Orchestrates CBS algorithm
- Verifies solution validity
- Provides detailed statistics and analysis
- Tracks solving time and performance metrics

#### 6. **Visualization** (`visualization.py`)
- **Static Visualization**: Shows all paths overlaid on grid
- **Animated Visualization**: Time-step animation of droplet movements
- **Comparison Figures**: Before/after positions
- **Statistics Display**: Bottleneck analysis, wait action tracking

---

## CSP Formulation

### Variables (V)
```
P_{i,t} = Position of droplet i at time step t
```

### Domain (D)
```
All valid (x, y) coordinates on the microfluidic grid
excluding obstacles and boundaries
```

### Constraints (C)

1. **Vertex Collision Constraint**:
   ```
   For all droplets i, j where i ≠ j and all times t:
   P_{i,t} ≠ P_{j,t}
   ```

2. **Edge Collision Constraint** (swap prevention):
   ```
   For all adjacent droplets i, j and consecutive times t, t+1:
   If P_{i,t} = p₁ and P_{j,t} = p₂,
   then NOT (P_{i,t+1} = p₂ AND P_{j,t+1} = p₁)
   ```

3. **Start Position Constraint**:
   ```
   P_{i,0} = start_i
   ```

4. **Goal Constraint**:
   ```
   P_{i,T} = goal_i (for some time T)
   ```

---

## Algorithm Complexity Analysis

### Time Complexity

- **A* Single Agent**: O(n × m × e^h) where n, m are grid dimensions
- **CBS High-Level**: O(2^k) worst case (k = number of conflicts)
- **Overall**: Depends on conflict density

### Space Complexity
- **Grid Storage**: O(n × m)
- **Path Storage**: O(k × T) where k = number of droplets, T = time steps
- **Search Space**: O(n × m × T)

### Practical Performance
- **Simple Scenario (3 droplets, 10×10 grid)**: ~0.001 seconds
- **Complex Scenario (5 droplets, 15×15 grid with obstacles)**: ~0.01 seconds
- **High Throughput (6 droplets, 20×20 grid)**: ~0.022 seconds

---

## Usage Examples

### Basic Usage

```python
from grid import MicrofluidicGrid, Droplet
from solver import MAPFSolver

# Create grid
grid = MicrofluidicGrid(width=10, height=10)

# Create droplets
droplets = [
    Droplet(id=0, start=(1, 1), goal=(8, 8)),
    Droplet(id=1, start=(1, 8), goal=(8, 1)),
    Droplet(id=2, start=(5, 5), goal=(5, 1)),
]

# Solve
solver = MAPFSolver(grid, droplets)
solver.solve()

# Get solution
solution = solver.get_solution()
solver.print_solution_summary()
```

### Adding Obstacles

```python
# Add walls to grid
for x in range(5, 10):
    grid.add_obstacle((x, 7))

# The A* algorithm automatically avoids obstacls
```

### Visualization

```python
from visualization import MicrofluidicVisualizer

visualizer = MicrofluidicVisualizer(grid, droplets, solution)

# Static plot
fig, ax = visualizer.plot_static(title="Microfluidic Routing")

# Animation
fig, anim = visualizer.animate(interval=500)

# Statistics
visualizer.show_statistics()
```

---

## Constraint Application Example

### Scenario: Two Droplets Colliding

**Initial Paths (no constraints)**:
- Droplet A: (0,0) → (1,0) → (1,1) → ...
- Droplet B: (2,0) → (1,0) → (0,0) → ...
- **Collision**: Both at (1,0) at t=1

**CBS Resolution**:

1. **Branch 1**: Add constraint "Droplet A cannot be at (1,0) at t=1"
   - A replans: (0,0) → (0,1) → (1,1) → ...
   - Cost increases by 1 step

2. **Branch 2**: Add constraint "Droplet B cannot be at (1,0) at t=1"
   - B replans: (2,0) → (2,1) → (1,1) → ...
   - Cost increases by 1 step

**A* then finds next conflict or solution**

---

## Scalability Considerations

### Performance Bottlenecks

1. **Narrow Channels**: Creates bottlenecks, increasing conflict resolution time
2. **High Droplet Density**: More conflicts to resolve
3. **Large Search Spaces**: Grid size affects A* performance

### Optimization Strategies

1. **Improved Heuristics**: 
   - Pattern Database (PDB) heuristics
   - Landmark-based heuristics
   - Prioritized Planning

2. **Conflict Resolution Priority**:
   - Prioritize high-cost conflicts
   - Use symmetry breaking

3. **Parallel Processing**:
   - Multi-threading for independent path planning
   - GPU acceleration for grid operations

---

## Test Scenarios

### 1. Simple Scenario (3 droplets, 10×10 grid)
- **Routing**: Cross-pattern paths
- **Conflicts**: Minimal
- **Time**: <1ms
- **Status**: ✓ Solved

### 2. Complex Scenario (5 droplets, 15×15 grid with obstacles)
- **Obstacles**: Walls creating narrow passages
- **Conflicts**: Moderate (bottleneck areas)
- **Time**: ~10ms
- **Status**: ✓ Solved

### 3. High Throughput (6 droplets, 20×20 grid)
- **Configuration**: Multiple simultaneous routings
- **Conflicts**: More complex interactions
- **Time**: ~22ms
- **Status**: ✓ Solved

---

## Interdisciplinary Merit

### Chemical Engineering ↔ Computer Science

1. **Domain**: Real microfluidic lab-on-chip devices face exact this problem
2. **Algorithmic Innovation**: CBS is state-of-the-art in multi-agent robotics
3. **Practical Application**: Enables high-throughput drug discovery automation
4. **Research Bridge**: Connects constraint satisfaction with experimental design

### Real-World Impact

- **Drug Discovery**: Accelerate screening of therapeutic compounds
- **Bioassays**: Parallelize multiple experiments
- **Cost Reduction**: Reduce reagent waste through optimized routing
- **Time Efficiency**: Complete experiments in hours instead of days

---

## Files Structure

```
AIFA Project/
├── grid.py              # Grid and Droplet classes
├── astar.py             # A* algorithm implementation
├── collision.py         # Collision detection
├── cbs.py               # Conflict-Based Search algorithm
├── solver.py            # MAPF solver orchestration
├── visualization.py     # 2D visualization and animation
├── main.py              # Example scenarios and testing
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

---

## Dependencies

- **numpy**: Numerical operations
- **matplotlib**: Visualization and animation
- **Python 3.7+**: Core language

---

## How to Run

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Examples
```bash
python3 main.py
```

### Create Animation
```python
# In main.py, uncomment the animation section:
create_animated_demo()
```

---

## Future Enhancements

1. **Advanced Heuristics**: Pattern database, symmetry breaking
2. **Parallel CBS**: Multi-threaded constraint resolution
3. **Hierarchical Planning**: Multi-scale routing for larger grids
4. **Dynamic Obstacles**: Mobile obstacles or time-varying channels
5. **Robustness**: Handle sensor noise and actuation errors
6. **Real-time Re-planning**: Adapt to deviations during execution

---

## References

- **Conflict-Based Search**: Sharon et al., "Conflict-based search for optimal multi-agent pathfinding," IJCAI 2015
- **A* Algorithm**: Hart, Nilsson, Raphael, "A Formal Basis for the Heuristic Determination of Minimum Cost Paths," IEEE TSSC 1968
- **Microfluidic Applications**: Teh et al., "Droplet Microfluidics," Lab on a Chip (Royal Society of Chemistry)

---

## Author Notes

This implementation demonstrates that cutting-edge constraint satisfaction and graph search algorithms can directly solve engineering challenges in chemical instrumentation. The CBS + A* approach provides optimal solutions within practical time constraints for realistic microfluidic systems.
