import tkinter as tk
import numpy as np

# Grid size and tile size
grid_size = (16, 20)
tile_size = 30  # Size of each tile on the canvas

# Create a Tkinter window
root = tk.Tk()
root.title("Tile Grid Drawer")

# Initialize the grid with zeros (open tiles)
grid = np.zeros(grid_size, dtype=int)

# Create a canvas to draw the grid
canvas = tk.Canvas(root, width=grid_size[1] * tile_size, height=grid_size[0] * tile_size)
canvas.pack()

# Function to draw the grid on the canvas
def draw_grid():
    for row in range(grid_size[0]):
        for col in range(grid_size[1]):
            color = "black" if grid[row, col] == -1 else "white"
            canvas.create_rectangle(col * tile_size, row * tile_size,
                                    (col + 1) * tile_size, (row + 1) * tile_size,
                                    fill=color, outline="gray")

# Mouse click handler to toggle tiles between open and blocked
def on_canvas_click(event):
    col = event.x // tile_size
    row = event.y // tile_size

    # Toggle between open (0) and blocked (-1)
    if grid[row, col] == 0:
        grid[row, col] = -1
    else:
        grid[row, col] = 0

    # Redraw the grid after the update
    draw_grid()

# Bind the left mouse click to the canvas
canvas.bind("<Button-1>", on_canvas_click)

# Draw the initial grid
draw_grid()

# Function to show the final grid as a 2D array
def show_final_grid():
    print(grid)

# Add a button to print the grid when finished drawing
show_button = tk.Button(root, text="Show Final Grid", command=show_final_grid)
show_button.pack()

# Start the Tkinter event loop
root.mainloop()
