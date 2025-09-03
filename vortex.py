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
    print("[vortex.py][ERROR] SLM not detected. Please connect and configure the device as a SECONDARY monitor." \
    "\nUsing primary monitor instead.")

# Set size of SLM (H pixels x V pixels)
H = slm_monitor.width  
V = slm_monitor.height 

# Screen coordinates
x = np.arange(-H/2, H/2)
y = np.arange(-V/2, V/2)
X, Y = np.meshgrid(x, y)

# --- Hologram Calculation ---
# Azimuthal angle for each point
phi = np.angle(X + 1j * Y)

l = 2    # Topological charge
nx = 50  # Number of horizontal grooves
ny = 50  # Number of vertical grooves

# Calculate grating vector components
gx = nx / H
gy = ny / V

# Hologram phase pattern
hologram = np.mod(l * phi + 2 * np.pi * (Y * gy + X * gx), 2 * np.pi)
scaled_hologram = (hologram / hologram.max()) * 255  
scaled_hologram = scaled_hologram.astype(np.uint8)    # stores hologram as an 8bit unsigned integer 

# Display SLM on secondary monitor
cv2.namedWindow('SLM', cv2.WND_PROP_FULLSCREEN)       # create window for hologram to be displayed on
cv2.moveWindow('SLM', slm_monitor.x, slm_monitor.y)   # move that window to the SLM monitor
cv2.setWindowProperty('SLM', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)  # make the window full screen
cv2.imshow('SLM', scaled_hologram)                    # show hologram on SLM

print("[vortex.py] Hologram displaying on SLM. Ensure mouse cursor is on primary monitor. Press ANY KEY to close.")
cv2.waitKey(0)   # Wait until any key is pressed, then close the SLM window