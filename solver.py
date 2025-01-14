from ortools.sat.python import cp_model
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
import time
start_time = time.time()
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
            3: 'red',
            2: 'green',
            4: 'saddlebrown',
            5: 'yellow',
            6: 'blue'  # Add colors as needed
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
                elif label > 0:  # Squares to be drawn
                    # drawn.add(label)

                    # Draw the square as a rectangle
                    rect = plt.Rectangle(
                        (j, i), 1, 1, edgecolor='black', facecolor=color_map.get(label, 'gray'), linewidth=1
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
    plt.savefig('solution.pdf')

# Create and solve the model
# Create and solve the model
def optimize_placement(grid, mandatory_sizes):
    model = cp_model.CpModel()
    rows, cols = grid.shape

    placements = {}
    total_placements = {}  # Total placement variables for each size

    # Decision variables for placements
    for size in mandatory_sizes.keys():
        total_placements[size] = model.NewIntVar(0, rows * cols, f'total_placement_size_{size}')
        placements[size] = {}
        for i in range(rows - size + 1):
            for j in range(cols - size + 1):
                placements[size][(i, j)] = model.NewBoolVar(f'square_size_{size}_at_{i}_{j}')

    # Boundary constraint: Prevent tiles from being placed on blocked areas
    for size, placement_dict in placements.items():
        for (i, j), var in placement_dict.items():
            # Check if any part of the square overlaps with blocked areas (-1)
            if np.any(grid[i:i + size, j:j + size] == -1):
                model.Add(var == 0)

    # Non-overlap constraint
    for i in range(rows):
        for j in range(cols):
            overlap = []
            for size, placement_dict in placements.items():
                for di in range(size):
                    for dj in range(size):
                        if 0 <= i - di < rows - size + 1 and 0 <= j - dj < cols - size + 1:
                            overlap.append(placement_dict[(i - di, j - dj)])
            if overlap:
                model.Add(sum(overlap) <= 1)

    # Ensure minimum placement for mandatory sizes
    for size, min_count in mandatory_sizes.items():
        model.Add(
            sum(placements[size][(i, j)] for i in range(rows - size + 1) for j in range(cols - size + 1)) >= min_count
        )

    # Objective: Maximize placement of all squares
    model.Maximize(
        sum(100 * total_placements[size] for size in mandatory_sizes.keys()) +  # Reward mandatory squares
        sum(size * size * total_placements[size] for size in mandatory_sizes.keys()) -  # Reward optional squares
        sum(grid[i, j] == 0 for i in range(rows) for j in range(cols))  # Penalize empty spaces
    )


    return model, placements


def solve_model(model, grid, placements):
    rows, cols = grid.shape
    # Solve the model
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    # Update grid with placements
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for size, placement_dict in placements.items():
            for (i, j), var in placement_dict.items():
                if solver.Value(var) == 1:
                    grid[i:i + size, j:j + size] = size
        print(f"Status: {solver.StatusName(status)}")
    else:
        print("No solution found!")

    return grid

# Initialize the grid with blocked areas
grid_size = (16, 20)
try:
    grid = np.loadtxt("grid_formatted.txt", dtype=int)
    print("Grid loaded from 'grid_formatted.txt'.")
except FileNotFoundError:
    exit()


# def construct_squares_list(mandatory_squares, optional_squares):
#     # Calculate num_mandatory as the sum of the second numbers in the mandatory_squares list
#     num_mandatory = sum(count for _, count in mandatory_squares)
#     index = 1
#     # Build the mandatory squares list
#     squares = []
#     for size, count in mandatory_squares:
#         if count > 0:
#             for i in range(1, count + 1):
#                 squares.extend([(size, index)])
#                 index += 1

#     # Append the optional squares list
#     for size, count in optional_squares:
#         if count > 0:
#             for i in range(1 + num_mandatory, count + 1 + num_mandatory):
#                 squares.extend([(size, index)])
#                 index += 1

#     return squares, num_mandatory


# # Define squares (size, label)
# mandatory_squares = [(2, 0), (3, 0), (4, 2), (5, 15),
#                      (6, 0), (8, 1)]  # Sizes 3x3, labels 1-8
# optional_squares = [(2, 5), (3, 5), (4, 5), (5, 0),
#                     (6, 0), (8, 0)]  # Sizes 3x3, labels 1-8
# squares, mandatory = construct_squares_list(
#     mandatory_squares, optional_squares)
# mandatory_squares = [(5, i) for i in range(1, 12)]  # Sizes 3x3, labels 1-8
# optional_squares = [(2, i) for i in range(12, 17)]  # Sizes 2x2, labels 9-10
# squares = mandatory_squares + optional_squares
# print(squares)
mandatory_sizes = {2:0, 3:9, 4:5, 5:37, 6:1, 8:1}  # Minimum required placements for specific sizes

# Optimize placement and generate solutions
# Optimize placement and generate multiple unique solutions


def find_unique_solutions(grid, mandatory_sizes, max_solutions=1, max_attempts=15, num_mandatory=0):
    solutions = []
    seen_grids = set()

    model, placements = optimize_placement(grid, mandatory_sizes)
    for attempt in range(max_attempts):
        temp_grid = grid.copy()
        result_grid = solve_model(model, temp_grid, placements)
        # print(result_grid)

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
solutions = find_unique_solutions(grid, mandatory_sizes, max_solutions=1, max_attempts=10)

titles = [f"Solution {i + 1}" for i in range(len(solutions))]

# Visualize all solutions
print("--- %s seconds ---" % (time.time() - start_time))
visualize_grids(solutions, mandatory_sizes, titles)
