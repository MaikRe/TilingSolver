import tkinter as tk
import numpy as np

# Default grid size and tile size
tile_size = 20  # Size of each tile on the canvas
zoom_factor = 1  # Initial zoom factor
zoom_min = 0.5  # Minimum zoom level
zoom_max = 2  # Maximum zoom level

# Initialize the grid with zeros (open tiles)
grid_size = (32, 40)  # Initial grid size (rows, columns)
grid = np.full(grid_size, -1, dtype=int)
temp_grid = np.full(grid.shape, -1)

# Create a Tkinter window
root = tk.Tk()
root.title("Tile Grid Drawer")

# Variables for panning and drawing
offset_x, offset_y = 0, 0
drag_start_x, drag_start_y = None, None
drag_threshold = 5  # Threshold distance to distinguish between click and drag
is_drawing = False  # Flag to track if we're currently drawing
is_erasing = False  # Flag to track if we're currently drawing
color = 1
# List to keep the history of the grid for undo functionality
history = []

# Create a canvas to draw the grid
canvas = tk.Canvas(
    root, width=grid.shape[1] * tile_size, height=grid.shape[0] * tile_size)
canvas.pack()
canvas.focus_set()

# Function to draw the grid on the canvas


def draw_grid():
    colors = ["white", "green", "red",
              "saddle brown", "yellow", "blue", "white"]
    canvas.delete("all")  # Clear the canvas before drawing
    for row in range(grid.shape[0]):
        for col in range(grid.shape[1]):
            color = "white"
            if grid[row, col] == -1:
                pass
            else:
                color = colors[grid[row, col]-1]
            canvas.create_rectangle(col * tile_size + offset_x, row * tile_size + offset_y,
                                    (col + 1) * tile_size +
                                    offset_x, (row + 1) * tile_size + offset_y,
                                    fill=color, outline="gray")

# Mouse click handler to start the drawing process


def on_canvas_mouse_move(event):
    global drag_start_x, drag_start_y, is_drawing, is_erasing, color
    col = (event.x - offset_x) // tile_size
    row = (event.y - offset_y) // tile_size

    # Set the start position for drawing if it's the first click
    if drag_start_x is None or drag_start_y is None:
        drag_start_x, drag_start_y = event.x, event.y

    # Begin drawing when the mouse is pressed

    # if is_erasing:  # Right-click (erase)
    #     # Right-click: Unblock the tile (paint from black to white)
    #     grid[row, col] = 0  # Mark as open
    # elif is_drawing:
    #     # Left-click: Block the tile (paint from white to black)
    #     grid[row, col] = color  # Mark as blocked
    col_start = (drag_start_x - offset_x) // tile_size
    row_start = (drag_start_y - offset_y) // tile_size
    col_end = (event.x - offset_x) // tile_size
    row_end = (event.y - offset_y) // tile_size

    # Ensure the start and end coordinates are ordered
    col_start, col_end = min(col_start, col_end), max(col_start, col_end)
    row_start, row_end = min(row_start, row_end), max(row_start, row_end)
    # Paint or erase all tiles within the selected rectangle
    for row in range(row_start, row_end + 1):
        for col in range(col_start, col_end + 1):
            if is_erasing:  # Right-click (erase)
                # Right-click: Unblock the tile (paint from black to white)
                grid[row, col] = -1  # Mark as open
            elif is_drawing:
                # Left-click: Block the tile (paint from white to black)
                grid[row, col] = color  # Mark as blocked

    # Redraw the grid after modifying the tile
    draw_grid()

# Mouse drag handler for painting rectangles


def on_canvas_drag(event):
    global drag_start_x, drag_start_y, is_drawing
    if is_drawing:
        col_start = (drag_start_x - offset_x) // tile_size
        row_start = (drag_start_y - offset_y) // tile_size
        col_end = (event.x - offset_x) // tile_size
        row_end = (event.y - offset_y) // tile_size

        # Ensure the start and end coordinates are ordered
        col_start, col_end = min(col_start, col_end), max(col_start, col_end)
        row_start, row_end = min(row_start, row_end), max(row_start, row_end)

        # Paint or erase all tiles within the selected rectangle
        for row in range(row_start, row_end + 1):
            for col in range(col_start, col_end + 1):
                if event.state & 0x0001:  # Left-click (paint)
                    if grid[row, col] == 0:
                        grid[row, col] = -1  # Mark as blocked
                elif event.state & 0x0002:  # Right-click (erase)
                    if grid[row, col] == -1:
                        grid[row, col] = 0  # Mark as open

        draw_grid()

# Mouse release handler to stop the drawing process


def on_canvas_grab(event):
    global is_drawing
    global is_erasing
    global drag_start_x, drag_start_y

    if event.num == 1:
        is_drawing = True
    elif event.num == 3:
        is_erasing = True
    if drag_start_x is None or drag_start_y is None:
        drag_start_x, drag_start_y = event.x, event.y


def on_canvas_release(event):
    global is_erasing
    global is_drawing
    if event.num == 1:
        is_drawing = False
    elif event.num == 3:
        is_erasing = False
    global drag_start_x, drag_start_y
    drag_start_x, drag_start_y = None, None


def key_press(event):
    global color
    color = int(event.keysym)

# Mouse wheel to zoom in and out


def on_zoom(event):
    global tile_size, zoom_factor
    if event.delta > 0:
        zoom_factor = min(zoom_factor + 0.1, zoom_max)  # Zoom in
    else:
        zoom_factor = max(zoom_factor - 0.1, zoom_min)  # Zoom out
    tile_size = int(20 * zoom_factor)  # Adjust tile size based on zoom
    # Adjust canvas size
    canvas.config(width=grid_size[1] * tile_size,
                  height=grid_size[0] * tile_size)
    draw_grid()  # Redraw the grid with updated zoom

# Mouse drag handler for panning


def on_canvas_drag_pan(event):
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

# Function to show the final grid as a 2D array and save to a file


def show_final_grid():
    # Print the grid to the console (or use this data in the game)
    arr = grid.copy()
    arr[arr != -1] = 0

    # Save the grid to a text file
    np.savetxt("grid.txt", grid, fmt="%d")
    np.savetxt("grid_formatted.txt", arr, fmt="%d")
    print("Grid saved to 'grid.txt'.")

# Function to load the grid from a file if it exists


# Grid resizing controls
resize_frame = tk.Frame(root)
resize_frame.pack()

tk.Label(resize_frame, text="Rows:").pack(side="left")
row_entry = tk.Entry(resize_frame)
row_entry.pack(side="left")

tk.Label(resize_frame, text="Cols:").pack(side="left")
col_entry = tk.Entry(resize_frame)
col_entry.pack(side="left")



def load_grid():
    global grid
    try:
        grid = np.loadtxt("grid.txt", dtype=int)
        print("Grid loaded from 'grid.txt'.")
        row_entry.delete(0, -1)
        col_entry.delete(0, -1)

    except FileNotFoundError:
        print("No saved grid found, starting with an empty grid.")
    row_entry.insert(0, grid.shape[0])
    col_entry.insert(0, grid.shape[1])

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
        new_grid = np.full(grid_size, -1, dtype=int)
        min_width = min(grid.shape[0], new_grid.shape[0])
        min_height = min(grid.shape[1], new_grid.shape[1])
        new_grid[0:min_width, 0:min_height] = grid[0:min_width, 0:min_height]
        grid = new_grid
        canvas.config(width=cols * tile_size + 10,
                      height=rows * tile_size + 10)
        draw_grid()
    except ValueError:
        print("Invalid grid dimensions")


resize_button = tk.Button(
    resize_frame, text="Resize Grid", command=resize_grid)
resize_button.pack(side="left")

# Button to print the final grid when finished drawing and save it
show_button = tk.Button(root, text="Show Final Grid", command=show_final_grid)
show_button.pack()


# Bind mouse events to the canvas
canvas.bind("<B1-Motion>", on_canvas_mouse_move)  # Left-click for painting
canvas.bind("<B3-Motion>", on_canvas_mouse_move)  # Left-click for painting
canvas.bind("<ButtonPress-1>", on_canvas_grab)  # Stop drawing on release
canvas.bind("<ButtonRelease-1>", on_canvas_release)  # Stop drawing on release
canvas.bind("<ButtonPress-3>", on_canvas_grab)  # Stop drawing on release
canvas.bind("<ButtonRelease-3>", on_canvas_release)  # Stop drawing on release
# canvas.bind("<B1-Motion>", on_canvas_drag)  # Left-click for painting
canvas.bind("<B2-Motion>", on_canvas_drag_pan)  # Dragging to pan
canvas.bind("<ButtonPress-2>", on_canvas_drag_start)  # Start dragging
canvas.bind("<MouseWheel>", on_zoom)  # Scroll for zoom
canvas.bind("<KeyPress>", key_press)

# Load the grid from a file when the program starts
load_grid()

# Initial grid drawing
draw_grid()

# Start the Tkinter event loop
root.mainloop()
