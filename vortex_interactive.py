"""
vortex_interactive.py

Enables real-time (ish) changes to SLM pattern using tkinter GUI
"""

import numpy as np
import cv2
import tkinter as tk
from screeninfo import get_monitors

# Setup monitors and matrices related to screen size
monitors = get_monitors()
if len(monitors) > 1:
    slm_monitor = monitors[1]
    print("[vortex.py] Secondary monitor set as SLM display.")
else:
    slm_monitor = monitors[0]
    print("[vortex.py][DEBUG] SLM not detected. Will display SLM in secondary window on primary monitor.")

H = slm_monitor.width
V = slm_monitor.height

x = np.arange(-H/2, H/2)
y = np.arange(-V/2, V/2)
X, Y = np.meshgrid(x, y)

# Create SLM window
slm_window_name = 'SLM'
if len(monitors) > 1:
    cv2.namedWindow(slm_window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow(slm_window_name, slm_monitor.x, slm_monitor.y)
    cv2.setWindowProperty(slm_window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
else:
    cv2.namedWindow(slm_window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(slm_window_name, 1200, 900)

# Create control window
root = tk.Tk()
root.title("SLM Controls")
root.geometry("360x400")

# Function to close all created windows
def quit_program():
    """Safely close Tkinter and OpenCV windows"""
    cv2.destroyAllWindows()
    root.destroy()

# Function to take values from control panel window and set l, n_x, n_y
def read_params():
    """Read values from entry boxes and return integers with defaults"""
    try:
        l = int(entry_l.get())
    except ValueError:
        l = 1
    try:
        n_x = int(entry_nx.get())
    except ValueError:
        n_x = 50
    try:
        n_y = int(entry_ny.get())
    except ValueError:
        n_y = 50
    try: 
        x_0 = int(entry_x0.get())
    except ValueError:
        x_0 = 0
    try: 
        y_0 = int(entry_y0.get())
    except ValueError:
        y_0 = 0
    return l, n_x, n_y, x_0, y_0

# Function to update SLM window with those values
def update_slm():
    """Compute hologram and display in SLM window; auto-called by Tkinter"""
    l, n_x, n_y, x_0, y_0 = read_params()

    phi = np.angle((X - x_0) + 1j * (Y - y_0))
    gx = n_x / H
    gy = n_y / V
    hologram = np.mod(l * phi + 2 * np.pi * (Y * gy + X * gx), 2 * np.pi)
    scaled = (hologram / hologram.max() * 255).astype(np.uint8)

    cv2.imshow(slm_window_name, scaled)

    # Check for ESC key to quit
    if cv2.waitKey(1) == 27:
        quit_program()
    else:
        root.after(30, update_slm)  # ~33 FPS

# Controls for l, n_x, and n_y
tk.Label(root, text="Topological Charge (l)").pack()
entry_l = tk.Entry(root)
entry_l.insert(0, "2")
entry_l.pack()

tk.Label(root, text="X Groove Count (n_x)").pack()
entry_nx = tk.Entry(root)
entry_nx.insert(0, "50")
entry_nx.pack()

tk.Label(root, text="Y Groove Count (n_y)").pack()
entry_ny = tk.Entry(root)
entry_ny.insert(0, "50")
entry_ny.pack()

tk.Label(root, text="Horizontal Center Shift (x_0)").pack()
entry_x0 = tk.Entry(root)
entry_x0.insert(0, "0")
entry_x0.pack()

tk.Label(root, text="Vertical Center Shift (y_0)").pack()
entry_y0 = tk.Entry(root)
entry_y0.insert(0, "0")
entry_y0.pack()

tk.Button(root, text="Quit", command=quit_program, bg='red', fg='white').pack(pady=10)

update_slm()
root.mainloop()
