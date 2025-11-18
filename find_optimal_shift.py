"""
find_optimal_shift.py

After running 'vortex_cam_auto.py' to generate a fully imaged beam dataset (see that file
for more details), this script will compute Gaussian fits along four axial slices of the
vortex beam, for each imaged beam. From there, it will find the SLM offset for which the
parameters of those four Gaussians are most similar, corresponding to a symmetric vortex. 

"""
import tkinter as tk
from tkinter import ttk
import os

import numpy as np
import matplotlib.pyplot as plt
import cv2
from scipy.optimize import curve_fit
from numpy.typing import NDArray
import time
from datetime import datetime

# --- code to select file to analyze ---
def select_file():
    print("[find_optimal_shift.py] Selected file:", selected_file.get())
    root.destroy()

# Folder to list files from
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")
files = os.listdir(data_dir)

root = tk.Tk()
root.geometry("300x100") 
root.title("Select a dataset to analyze.")

selected_file = tk.StringVar(value=files[0])

dropdown = ttk.Combobox(root, textvariable=selected_file, values=files)
dropdown.pack(padx=20, pady=20)

button = tk.Button(root, text="OK", command=select_file)
button.pack(pady=10)

root.mainloop()

# --- load in dataset ---
print("[find_optimal_shift.py] Starting Analysis...")
beam_data = np.load(f"{data_dir}/{selected_file.get()}")

frames = beam_data['frames']
x_off = beam_data['x_offset_arr']
y_off = beam_data['y_offset_arr']

# --- analysis functions ---
def find_annulus_center(img, show_plot:bool = False, debug: bool = False):
    '''
    Find the center of the dark region in the middle of the vortex beam by inverting image,
    masking all the brightest stuff to 255 and everything else to 0, then 
    '''
    img_inv = img.max() - img
    img_inv = cv2.blur(img_inv, (5,5)) # smooth over imaged impurities

    # set to zero if not in 98% brightest of inverse
    mask = img_inv >= 0.99*img_inv.max()
    img_inv_masked = img_inv.copy()
    img_inv_masked[mask] = 255
    img_inv_masked[~mask] = 0

    if debug:
        plt.imshow(img_inv_masked, cmap='gray')
        plt.axis('off')

    # locate all connected regions left
    _, mask2 = cv2.threshold(img_inv_masked, 254, 255, cv2.THRESH_BINARY)
    num_labels, _, stats, centroids = cv2.connectedComponentsWithStats(mask2, connectivity=8)

    # all blobs that don't touch the border
    h, w = img.shape
    inner_blobs = []
    for i in range(0, num_labels):  # skip background
        x, y, blob_width, blob_height, _ = stats[i]
        if x > 0 and y > 0 and x+blob_width < w-1 and y+blob_height < h-1:
            inner_blobs.append(i)

    # take blob centroid closest to center
    x_img_center, y_img_center = int(w/2), int(h/2)
    min_distance = np.inf
    for i in inner_blobs:
        cx, cy = centroids[i]  # centroids are floats
        dist_center = (x_img_center - cx)**2 + (y_img_center - cy)**2
        if dist_center < min_distance:
            x_center, y_center = round(cx), round(cy)
            min_distance = dist_center
    
    # show beam with center located
    if show_plot and not debug:
        plt.scatter(x_center, y_center, color='red', marker='x', s=100, label='Center of Vortex')
        plt.legend()
        plt.axis('off')
        plt.imshow(img, cmap='gray')

    return x_center, y_center

def create_intensity_dict(img, x_center, y_center, smooth: bool):
    if smooth:
        img = cv2.blur(img, (10,10))

    center_row = img[y_center]
    center_col = img.T[x_center]

    left_intensity  = center_row[:x_center+1]
    right_intensity = center_row[x_center:]
    up_intensity    = center_col[:y_center+1]
    down_intensity  = center_col[y_center:]

    intensity_dict = {
        "left": left_intensity,
        "right": right_intensity,
        "up": up_intensity,
        "down": down_intensity
    }

    return intensity_dict

def gaussian(x,a,b,c):
        return a * np.exp(-(x - b)**2 / (2*c**2))

def fit_gaussians(intensity_dict):
    '''
    Given the four intensity profiles, return a dictionary giving
    the fitted parameters of each
    '''
    param_dict = {}

    for key in intensity_dict.keys():
        intensity = intensity_dict[key]
        x = np.arange(0, len(intensity),1)
        try:
            params, _ = curve_fit(gaussian, x, intensity)
            param_dict[key] = params
        except RuntimeError:
            param_dict[key] = [1e6, 2e6, 3e6]

    return param_dict

def plot_intensities(img, desired_x, desired_y, x_center, y_center, intensity_dict, param_dict, time_txt, smooth: bool, ui_dir: bool = True):
    '''
    From beam center, go left, right, up, and down to boarder and collect brightnesses
    along the way. Show all four intensity curves and the image with all four of those
    mapped and color-coded.

    Parameters
    ----------
    img : NDArray
        numpy array of 0 - 255 brightness values for image
    desired_x, desired_y : int
        SLM pixel offset
    x_center, y_center : int
        pixel center of beam profile from find_annulus_center function
    intensity_dict : dict
        A dictionary of the four intensity slices, output of 'create_intensity_dict' function
    param_dict : dict
        A dictionary of the Gaussian parameters, output of 'fit_gaussians'
    time_txt : String
        A string saying whether this is pre- or post-alignment.
    smooth : bool
        If true, smooth image before computing intensity profile. Almost always desired.
    ui_dir : bool
        If true, will create direction based on file selection from ui. If false, will be chosen
        as current date and time

    Returns
    -------
    i
    '''
    if smooth:
        img = cv2.blur(img, (10,10)) # smooth over imaged impurities

    # define figure and grid spacing
    fig = plt.figure(figsize=(16, 8))
    gs = fig.add_gridspec(4, 3, width_ratios=[1, 1, 1.6])  

    # 2x2 square plots (take rows 0-3, cols 0-1)
    ax1 = fig.add_subplot(gs[0:2, 0])   # top-left
    ax2 = fig.add_subplot(gs[0:2, 1])   # top-right
    ax3 = fig.add_subplot(gs[2:4, 0])   # bottom-left
    ax4 = fig.add_subplot(gs[2:4, 1])   # bottom-right
    ax_ls = [ax1, ax2, ax3, ax4]

    # Image (span all 4 rows in last col)
    ax_img = fig.add_subplot(gs[:, 2])

    # plot the supposed Gaussians
    direction_ls = ["left","right","up","down"]
    color_ls = ["forestgreen","dodgerblue","red","darkorchid"]
    i = 0
    for ax in [ax1, ax2, ax3, ax4]:
        direction = direction_ls[i]
        x_range = np.arange(0, len(intensity_dict[direction]),1)
        ax.scatter(x_range, intensity_dict[direction], s=6, color=color_ls[i])
        ax.plot(x_range, gaussian(x_range, *param_dict[direction]), color = 'black', linewidth = 3)
        ax.set_ylim(0,265)
        ax.set_box_aspect(1)
        i += 1

    # axis labels for intensity plots
    from matplotlib.transforms import Bbox
    bbox = Bbox.union([ax.get_position() for ax in ax_ls])
    big_ax = fig.add_axes(bbox, frameon=False)
    big_ax.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)
    big_ax.set_xlabel("Pixels", fontsize = 12)
    big_ax.set_ylabel("Intensity", fontsize = 12)

    # show imaged beam
    ax_img.imshow(img, cmap='gray')
    ax_img.axis('off')

    # make colored lines on image
    linewidth = 5
    ax_img.plot([0, x_center], [y_center, y_center], color_ls[0], linestyle='-', linewidth=linewidth)  # left, from (0, y_center) to (x_center, y_center)
    ax_img.plot([x_center, img.shape[1]-1], [y_center, y_center], color_ls[1], linestyle='-', linewidth=linewidth)  # right, from (x_center, y_center) to (img.shape[0], y_center)
    ax_img.plot([x_center, x_center], [0, y_center], color_ls[2], linestyle='-', linewidth=linewidth)  # up, from (x_center, 0) to (x_center, y_center)
    ax_img.plot([x_center, x_center], [y_center, img.shape[0]-1], color_ls[3], linestyle='-', linewidth=linewidth)  # down, from (x_center, y_center) to (x_center, img.shape[1])
    ax_img.set_title(f"Beam profile for x-offset = {desired_x} pixels, y-offset = {desired_y} pixels")

    if smooth:
        smooth_txt = 'smoothed'
    else:
        smooth_txt = 'raw'
    fig.suptitle(f"Axial intensity profiles of {smooth_txt} imaged vortex beam", fontsize = 20)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if ui_dir:
        fig_dir = os.path.join(script_dir, f"fig/{selected_file.get()}")
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        fig_dir = os.path.join(script_dir, f"fig/{timestamp}")
    os.makedirs(fig_dir, exist_ok=True)
    filename = os.path.join(fig_dir, f"intensity_{time_txt}_alignment.png")
    plt.savefig(filename)

def find_most_gaussian_offsets(frames: NDArray, x_off: NDArray, y_off: NDArray):
    '''
    Finds intensity profiles of all images in a dataset
    '''
    centers_arr = np.zeros(len(frames)*2, dtype=int).reshape(len(frames),2)
    param_arr = np.zeros(len(frames), dtype=object)
    i = 0
    start = time.time()
    for img in frames:
        x_center, y_center = find_annulus_center(img, show_plot = False, debug = False)
        centers_arr[i] = [x_center, y_center]
        i += 1
    center_elapsed = time.time() - start
    print("Time to find all centers:",center_elapsed)

    i=0
    start = time.time()
    for img in frames:
        x_center, y_center = centers_arr[i]
        intensity_dict = create_intensity_dict(img, x_center, y_center, smooth = True)
        param_dict = fit_gaussians(intensity_dict)
        param_arr[i] = param_dict
        i+=1
    fit_elapsed = time.time() - start
    print("Time to fit all the Gaussians:",fit_elapsed)
    
    start = time.time()
    loss = np.zeros(len(frames))
    i=0
    for params in param_arr:
        a_ls = np.array([])
        c_ls = np.array([])
        for direction in params.keys():
            a, _, c = params[direction]
            a_ls = np.append(a_ls, a)
            c_ls = np.append(c_ls, c)

        loss[i] = len(a_ls) * (np.sum((a_ls - a_ls.mean())**2) + np.sum((c_ls - c_ls.mean())**2))
        i += 1
    loss_elapsed = time.time() - start
    print("Time to compute all losses:", loss_elapsed)
    
    idx = np.argmin(loss)
    best_x_off = x_off[idx]
    best_y_off = y_off[idx]

    return best_x_off, best_y_off

# --- plot and save image intensities before alignment ---
desired_idx = np.where((x_off == 0) & (y_off == 0))[0][0]
img = frames[desired_idx]
x_center, y_center = find_annulus_center(img, show_plot = True, debug = False)
intensity_dict = create_intensity_dict(img, x_center, y_center, smooth = True)
param_dict = fit_gaussians(intensity_dict)
plot_intensities(img, 0, 0, x_center, y_center, intensity_dict, param_dict, "before", smooth = True)

# --- run analysis ---
best_x_off, best_y_off = find_most_gaussian_offsets(frames, x_off, y_off)
print("Best x:", best_x_off)
print("Best y:", best_y_off)

desired_idx = np.where((x_off == best_x_off) & (y_off == best_y_off))[0][0]
img = frames[desired_idx]
x_center, y_center = find_annulus_center(img, show_plot = True, debug = False)
intensity_dict = create_intensity_dict(img, x_center, y_center, smooth = True)
param_dict = fit_gaussians(intensity_dict)
plot_intensities(img, best_x_off, best_x_off, x_center, y_center, intensity_dict, param_dict, "after", smooth = True)

# --- done ---
print("[find_optimal_shift.py] Analysis complete, figures saved to './fig' directory.")