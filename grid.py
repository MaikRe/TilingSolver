import tkinter as tk
import numpy as np

# Default grid size and tile size
tile_size = 20  # Size of each tile on the canvas
zoom_factor = 1  # Initial zoom factor
zoom_min = 0.5  # Minimum zoom level
zoom_max = 2  # Maximum zoom level

# Initialize the grid with zeros (open tiles)
grid_size = (64, 40)  # Initial grid size (rows, columns)
grid = np.zeros(grid_size, dtype=int)

# Create a Tkinter window
root = tk.Tk()
root.title("Tile Grid Drawer")

# Variables for panning
offset_x, offset_y = 0, 0
drag_start_x, drag_start_y = None, None
drag_threshold = 5  # Threshold distance to distinguish between click and drag

# List to keep the history of the grid for undo functionality
history = []

# Create a canvas to draw the grid
canvas = tk.Canvas(root, width=grid_size[1] * tile_size, height=grid_size[0] * tile_size)
canvas.pack()

# Function to draw the grid on the canvas
def draw_grid():
    canvas.delete("all")  # Clear the canvas before drawing
    for row in range(grid_size[0]):
        for col in range(grid_size[1]):
            color = "black" if grid[row, col] == -1 else "white"
            canvas.create_rectangle(col * tile_size + offset_x, row * tile_size + offset_y,
                                    (col + 1) * tile_size + offset_x, (row + 1) * tile_size + offset_y,
                                    fill=color, outline="gray")

# Mouse click handler to draw rectangles
def on_canvas_click(event):
    global drag_start_x, drag_start_y
    col = (event.x - offset_x) // tile_size
    row = (event.y - offset_y) // tile_size

    if drag_start_x is None or drag_start_y is None:
        drag_start_x, drag_start_y = event.x, event.y

    if event.num == 1:  # Left-click (paint)
        # Left-click: Block the tile (paint from white to black)
        if grid[row, col] == 0:
            grid[row, col] = -1  # Mark as blocked
    elif event.num == 3:  # Right-click (erase)
        # Right-click: Unblock the tile (paint from black to white)
        if grid[row, col] == -1:
            grid[row, col] = 0  # Mark as open

    # Redraw the grid after modifying the tile
    draw_grid()

# Mouse wheel to zoom in and out
def on_zoom(event):
    global tile_size, zoom_factor
    if event.delta > 0:
        zoom_factor = min(zoom_factor + 0.1, zoom_max)  # Zoom in
    else:
        zoom_factor = max(zoom_factor - 0.1, zoom_min)  # Zoom out
    tile_size = int(30 * zoom_factor)  # Adjust tile size
    canvas.config(width=grid_size[1] * tile_size, height=grid_size[0] * tile_size)  # Adjust canvas size
    draw_grid()  # Redraw the grid

# Mouse drag handler for panning
def on_canvas_drag(event):
    global offset_x, offset_y
    if abs(event.x - drag_start_x) > drag_threshold or abs(event.y - drag_start_y) > drag_threshold:
        offset_x = event.x - drag_start_x
        offset_y = event.y - drag_start_y
        draw_grid()  # Redraw the grid with the new offsets

# Store the starting position of the drag
def on_canvas_drag_start(event):
    global drag_start_x, drag_start_y
    drag_start_x = event.x - offset_x
    drag_start_y = event.y - offset_y

# Function to show the final grid as a 2D array
def show_final_grid():
    print(grid)

# Grid resizing controls
resize_frame = tk.Frame(root)
resize_frame.pack()

tk.Label(resize_frame, text="Rows:").pack(side="left")
row_entry = tk.Entry(resize_frame)
row_entry.insert(0, grid_size[0])
row_entry.pack(side="left")

tk.Label(resize_frame, text="Cols:").pack(side="left")
col_entry = tk.Entry(resize_frame)
col_entry.insert(0, grid_size[1])
col_entry.pack(side="left")


# Function to resize the grid
def resize_grid():
    global grid_size, grid
    try:
        rows = int(row_entry.get())
        cols = int(col_entry.get())
        # Ensure the new grid is valid
        if rows <= 0 or cols <= 0:
            raise ValueError("Grid dimensions must be positive.")
        grid_size = (rows, cols)
        grid = np.zeros(grid_size, dtype=int)
        canvas.config(width=cols * tile_size, height=rows * tile_size)
        draw_grid()
    except ValueError:
        print("Invalid grid dimensions")
resize_button = tk.Button(resize_frame, text="Resize Grid", command=resize_grid)
resize_button.pack(side="left")

# Button to print the final grid when finished drawing
show_button = tk.Button(root, text="Show Final Grid", command=show_final_grid)
show_button.pack()

# Bind mouse events to the canvas
canvas.bind("<Button-1>", on_canvas_click)  # Left-click for painting
canvas.bind("<Button-3>", on_canvas_click)  # Right-click for erasing
canvas.bind("<B2-Motion>", on_canvas_drag)  # Dragging to pan
canvas.bind("<ButtonPress-2>", on_canvas_drag_start)  # Start dragging
canvas.bind("<MouseWheel>", on_zoom)  # Scroll for zoom

# Initial grid drawing
draw_grid()

# Start the Tkinter event loop
root.mainloop()
