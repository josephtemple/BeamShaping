import numpy as np
import cv2
from screeninfo import get_monitors

# Set the SLM monitor to be the SECOND monitor 
monitors = get_monitors()
if len(monitors) > 1:
    slm_monitor = monitors[1]
    print("[vortex.py] Secondary monitor set as SLM display.")
else:
    slm_monitor = monitors[0] 
    print("[vortex.py][DEBUG] SLM not detected. Will display SLM in secondary window.")

# Set size of SLM (H pixels x V pixels)
H = slm_monitor.width  
V = slm_monitor.height 

# Screen coordinates
x = np.arange(-H/2, H/2)
y = np.arange(-V/2, V/2)
X, Y = np.meshgrid(x, y)

# Runtime variables
x_shift = 220   # shift center horizontally (right if positive, left if negative)
y_shift = -100   # shift center vertically (down if positive, up if negative)

l = 2    # Topological charge
nx = 50  # Number of horizontal grooves
ny = 50  # Number of vertical grooves

# Calculate grating vector components
phi = np.angle((X - x_shift) + 1j * (Y - y_shift))
gx = nx / H
gy = ny / V

# Hologram phase pattern
hologram = np.mod(l * phi + 2 * np.pi * (Y * gy + X * gx), 2 * np.pi)
scaled_hologram = (hologram / hologram.max()) * 255  
scaled_hologram = scaled_hologram.astype(np.uint8)    # stores hologram as an 8bit unsigned integer 

# If second monitor is connected, set SLM to display full screen on that
if len(monitors) > 1:
    # Display SLM on secondary monitor
    cv2.namedWindow('SLM', cv2.WND_PROP_FULLSCREEN)       # create window for hologram to be displayed on
    cv2.moveWindow('SLM', slm_monitor.x, slm_monitor.y)   # move that window to the SLM monitor
    cv2.setWindowProperty('SLM', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)  # make the window full screen

    print("[vortex.py] Hologram displaying on SLM. Ensure mouse cursor is on primary monitor. Press ESC to close.")
# If not, run SLM in 'debug mode' as a window on primary monitor
else:
    # Display SLM on secondary monitor
    cv2.namedWindow('SLM', cv2.WINDOW_NORMAL)       # create window for hologram to be displayed on
    cv2.resizeWindow('SLM', 800, 600)               # make that window 800 x 600

cv2.imshow('SLM', scaled_hologram)                  # show hologram on SLM

while True:
    key = cv2.waitKey(0)
    if key == 27:  # ESC key
        cv2.destroyAllWindows()
        break
    else:
        continue   # Any other key -> ignore and keep window open