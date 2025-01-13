from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button

# Function to visualize the grid
def visualize_grids(grids, squares, titles):
    current_index = 0

    fig, ax = plt.subplots(figsize=(8, 8))
    plt.subplots_adjust(bottom=0.2)

    def draw_grid(grid, title):
        ax.clear()
        ax.set_xlim(0, grid.shape[1])
        ax.set_ylim(0, grid.shape[0])
        ax.set_aspect('equal')
        ax.invert_yaxis()

        # Define colors for each square size
        color_map = {
            3: 'blue',
            2: 'green',
            4: 'red',
            5: 'purple',
            6: 'orange'  # Add colors as needed
        }

        # Draw squares and handle different tile types
        drawn = set()
        for i in range(grid.shape[0]):
            for j in range(grid.shape[1]):
                label = grid[i, j]

                if label == -1:  # Blocked square
                    rect = plt.Rectangle(
                        (j, i), 1, 1, edgecolor='black', facecolor='black', linewidth=2
                    )
                    ax.add_patch(rect)
                elif label == 0:  # Unused square
                    rect = plt.Rectangle(
                        (j, i), 1, 1, edgecolor='black', facecolor='white', linewidth=2
                    )
                    ax.add_patch(rect)
                elif label > 0 and label not in drawn:  # Squares to be drawn
                    drawn.add(label)

                    # Find the size of the square from the input squares
                    size = next(size for size, lbl in squares if lbl == label)
                    color = color_map.get(size, 'gray')

                    # Find the top-left corner of the square
                    for x in range(i, i + size):
                        for y in range(j, j + size):
                            if 0 <= x < grid.shape[0] and 0 <= y < grid.shape[1] and grid[x, y] == label:
                                top_left = (y, x)
                                break
                        else:
                            continue
                        break

                    # Draw the square as a rectangle
                    rect = plt.Rectangle(
                        top_left, size, size, edgecolor='black', facecolor=color, linewidth=2
                    )
                    ax.add_patch(rect)

        ax.set_title(title)
        ax.axis('off')
        fig.canvas.draw()

    def on_prev(event):
        nonlocal current_index
        current_index = (current_index - 1) % len(grids)
        draw_grid(grids[current_index], titles[current_index])

    def on_next(event):
        nonlocal current_index
        current_index = (current_index + 1) % len(grids)
        draw_grid(grids[current_index], titles[current_index])

    # Add navigation buttons
    axprev = plt.axes([0.1, 0.05, 0.1, 0.075])
    axnext = plt.axes([0.8, 0.05, 0.1, 0.075])
    bprev = Button(axprev, 'Previous')
    bnext = Button(axnext, 'Next')
    bprev.on_clicked(on_prev)
    bnext.on_clicked(on_next)

    # Initial draw
    draw_grid(grids[current_index], titles[current_index])
    plt.show()

# Create and solve the model
def optimize_placement(grid, squares, num_mandatory):
    model = cp_model.CpModel()
    rows, cols = grid.shape

    # Decision variables
    placements = {}
    for s_id, (size, label) in enumerate(squares):
        for i in range(rows - size + 1):
            for j in range(cols - size + 1):
                placements[(s_id, i, j)] = model.NewBoolVar(f'square_{label}_at_{i}_{j}')

    # Constraints
    for s_id, (size, label) in enumerate(squares):
        # Ensure each square is placed exactly once for mandatory squares
        if label <= num_mandatory:  # Mandatory squares have labels <= 8
            model.Add(sum(placements[(s_id, i, j)] for i in range(rows - size + 1) for j in range(cols - size + 1)) == 1)
        else:  # Optional squares can be placed at most once
            model.Add(sum(placements[(s_id, i, j)] for i in range(rows - size + 1) for j in range(cols - size + 1)) <= 1)

        # Ensure squares are placed within valid regions
        for i in range(rows - size + 1):
            for j in range(cols - size + 1):
                if np.any(grid[i:i + size, j:j + size] == -1):
                    model.Add(placements[(s_id, i, j)] == 0)

    # Non-overlap constraint
    for i in range(rows):
        for j in range(cols):
            overlap = []
            for s_id, (size, label) in enumerate(squares):
                for di in range(size):
                    for dj in range(size):
                        if 0 <= i - di < rows - size + 1 and 0 <= j - dj < cols - size + 1:
                            overlap.append(placements[(s_id, i - di, j - dj)])
            if overlap:
                model.Add(sum(overlap) <= 1)

    # Objective: Prioritize mandatory squares and maximize optional square placement
    model.Maximize(
        10 * sum(placements[(s_id, i, j)] for s_id, (size, label) in enumerate(squares) if label < num_mandatory for i in range(rows - size + 1) for j in range(cols - size + 1))
        + sum(placements[(s_id, i, j)] for s_id, (size, label) in enumerate(squares) if label >= num_mandatory for i in range(rows - size + 1) for j in range(cols - size + 1))
    )

    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Update grid with placements
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for s_id, (size, label) in enumerate(squares):
            for i in range(rows - size + 1):
                for j in range(cols - size + 1):
                    if solver.Value(placements[(s_id, i, j)]) == 1:
                        grid[i:i + size, j:j + size] = label
        print(f"Status: {status}")
    else:
        print("No solution found!")

    return grid

# Initialize the grid with blocked areas
grid_size = (16, 20)
grid = np.zeros(grid_size, dtype=int)
grid[10:16, 17:20] = -1  # Center 3x3 is blocked
grid[15:16, 13:20] = -1  # Center 3x3 is blocked

# Define squares (size, label)
mandatory_squares = [(5, i) for i in range(1, 12)]  # Sizes 3x3, labels 1-8
optional_squares = [(2, i) for i in range(12, 17)]  # Sizes 2x2, labels 9-10
squares = mandatory_squares + optional_squares

# Optimize placement and generate multiple unique solutions
def find_unique_solutions(grid, squares, max_solutions=5, max_attempts=15, num_mandatory=0):
    solutions = []
    seen_grids = set()

    for attempt in range(max_attempts):
        temp_grid = grid.copy()
        result_grid = optimize_placement(temp_grid, squares, num_mandatory)

        # Convert grid to a tuple for hashable comparison
        grid_tuple = tuple(map(tuple, result_grid))

        # Check if solution is unique
        if grid_tuple not in seen_grids:
            seen_grids.add(grid_tuple)
            solutions.append(result_grid)

        # Stop if we have enough solutions
        if len(solutions) >= max_solutions:
            break

    return solutions

# Generate solutions
solutions = find_unique_solutions(grid, squares, max_solutions=5, max_attempts=30, num_mandatory=len(mandatory_squares))

titles = [f"Solution {i + 1}" for i in range(len(solutions))]

# Visualize all solutions
visualize_grids(solutions, squares, titles)
