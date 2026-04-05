"""
Interactive animated visualization of droplet routing
"""
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches
from grid import MicrofluidicGrid, Droplet
from solver import MAPFSolver


def show_animation():
    print("Creating animated simulation with 6 droplets and reaction chambers...\n")
    
    grid = MicrofluidicGrid(width=22, height=22)
    
    # Single vertical barrier
    for y in range(8, 14):
        grid.add_obstacle((11, y))
    
    # Small horizontal block
    for x in range(5, 8):
        grid.add_obstacle((x, 8))
    
    # Defined reaction chambers (zones)
    reaction_chambers = {
        'R1': ((1, 1), (3, 3)),         
        'R2': ((20, 1), (22, 3)),       
        'R3': ((1, 20), (3, 22)),       
        'R4': ((20, 20), (22, 22)),     
        'MIX': ((10, 10), (12, 12)),    
    }
    
    # Created 6 droplets with multi-chamber routing (proven solvable pattern)
    droplets = [
        Droplet(id=0, start=(2, 2), goal=(20, 20), color='red'),    
        Droplet(id=1, start=(20, 2), goal=(2, 20), color='blue'),     
        Droplet(id=2, start=(2, 20), goal=(20, 2), color='green'),    
        Droplet(id=3, start=(20, 20), goal=(2, 2), color='orange'),  
        Droplet(id=4, start=(2, 11), goal=(20, 11), color='purple'),  
        Droplet(id=5, start=(20, 11), goal=(2, 11), color='cyan'),    
    ]
    
    print(f"Grid: {grid.width}×{grid.height}")
    print(f"Droplets: {len(droplets)}")
    print(f"Reaction Chambers: {len(reaction_chambers)}")
    print("Solving...")
    
    # Solved the routing problem
    solver = MAPFSolver(grid, droplets)
    success = solver.solve(max_time=300)
    
    if success:
        print(f"Solution found in {solver.solve_time:.4f} seconds")
        print(f"Simulation duration: {solver.get_max_time()} time steps\n")
        
       
        solution = solver.get_solution()
        print("Playing animation with enhanced UI (close window to exit)...")
        create_enhanced_animation(grid, droplets, solution, reaction_chambers)
        
        # Print summary
        print("\n" + "="*60)
        print("ANIMATION COMPLETE")
        print("="*60)
        solver.print_solution_summary()
        
    else:
        print("No solution found")


def create_enhanced_animation(grid, droplets, solution, reaction_chambers):
    """Create enhanced animation with reaction chambers and path traces."""
    max_time = max(len(path) for path in solution.values())
    
    fig, ax = plt.subplots(figsize=(14, 14))
    
    ax.set_xlim(-1, grid.width)
    ax.set_ylim(-1, grid.height)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2)
    
    for i in range(grid.width + 1):
        ax.axvline(i - 0.5, color='lightgray', linewidth=0.5, alpha=0.3)
    for i in range(grid.height + 1):
        ax.axhline(i - 0.5, color='lightgray', linewidth=0.5, alpha=0.3)

    for obs in grid.obstacles:
        rect = patches.Rectangle((obs[0] - 0.45, obs[1] - 0.45), 0.9, 0.9,
                                 linewidth=1, edgecolor='darkgray', 
                                 facecolor='lightgray', alpha=0.7)
        ax.add_patch(rect)
    
    #reaction chambers
    colors_chambers = ['#FFE6E6', '#E6F2FF', '#E6FFE6', '#FFF9E6', '#F0E6FF']
    for idx, (chamber_name, (p1, p2)) in enumerate(reaction_chambers.items()):
        x1, y1 = p1
        x2, y2 = p2
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        rect = patches.Rectangle((x1 - 0.5, y1 - 0.5), width, height,
                                 linewidth=2, edgecolor='purple', 
                                 facecolor=colors_chambers[idx % len(colors_chambers)],
                                 alpha=0.3, linestyle='--')
        ax.add_patch(rect)
        ax.text(x1 + width/2 - 0.2, y1 + height/2, chamber_name,
               fontsize=10, fontweight='bold', color='purple')
    
    color_map = {
        0: 'red', 1: 'blue', 2: 'green', 3: 'orange', 4: 'purple',
        5: 'cyan', 6: 'magenta', 7: 'yellow', 8: 'lime', 9: 'brown'
    }
    
    # Created scatter plots for droplets
    scatter = {}
    for droplet in droplets:
        scatter[droplet.id] = ax.scatter([], [], s=300, c=color_map[droplet.id],
                                        edgecolors='black', linewidth=2, 
                                        zorder=10, label=f'D{droplet.id}')
    
    # Paths
    path_lines = {}
    for droplet in droplets:
        path_lines[droplet.id], = ax.plot([], [], color=color_map[droplet.id],
                                         alpha=0.4, linewidth=2, linestyle='-')
    
    time_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, 
                       fontsize=11, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    status_text = ax.text(0.02, 0.88, '', transform=ax.transAxes, 
                         fontsize=10, verticalalignment='top', color='darkgreen')
    collision_text = ax.text(0.02, 0.80, '', transform=ax.transAxes,
                            fontsize=9, verticalalignment='top', color='red')
    
    
    ax.legend(loc='upper right', ncol=2, fontsize=8, framealpha=0.9)
    
    def update(frame):
        time_text.set_text(f"Time Step: {frame}")
        
        # Update droplet positions
        droplet_at_goal = 0
        for droplet in droplets:
            if frame < len(solution[droplet]):
                pos = solution[droplet][frame]
                scatter[droplet.id].set_offsets([[pos[0], pos[1]]])
                
                # Update path trail
                path = solution[droplet][:frame + 1]
                x_coords = [p[0] for p in path]
                y_coords = [p[1] for p in path]
                path_lines[droplet.id].set_data(x_coords, y_coords)
                
                # Check if at goal
                if pos == droplet.goal:
                    droplet_at_goal += 1
        
        status_text.set_text(f"Droplets at goal: {droplet_at_goal}/{len(droplets)}")
        
        # Check for collisions at this time
        positions_now = {}
        for droplet in droplets:
            if frame < len(solution[droplet]):
                pos = solution[droplet][frame]
                if pos not in positions_now:
                    positions_now[pos] = []
                positions_now[pos].append(droplet.id)
        
        collision_detected = False
        for pos, dlist in positions_now.items():
            if len(dlist) > 1:
                collision_detected = True
                break
        
        if collision_detected:
            collision_text.set_text(f"COLLISION DETECTED! (Should not happen)")
        else:
            collision_text.set_text(f"No collisions")
        
        ax.set_title(f"Microfluidic Droplet Routing - Conflict-Based Search\n"
                    f"Time: {frame}/{max_time} | Droplets: {len(droplets)} | Obstacles: {len(grid.obstacles)}",
                    fontsize=12, fontweight='bold')
        
        return list(scatter.values()) + list(path_lines.values()) + [time_text, status_text, collision_text]
    
   
    anim = FuncAnimation(fig, update, frames=max_time, interval=400, blit=True, repeat=True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    show_animation()
