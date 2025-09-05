[WIP]

Hello! This project is in fulfillment of the Undergraduate Research required for physics majors at Arkansas Tech University, performed under the advisorship of Dr. Jessica Young. This description will become more thorough as more things happen, but in short the goal is to leverage machine learning techniques for the calibration of a spatial light modulator (SLM), and perhaps correct for non-Gaussian-ness in the initial beam. Time will tell!

Note: To ensure correct package dependencies, create a new conda environment with Python 3.13.5 by running ``conda env create -f environment.yml`` from a terminal in a local clone of this repository. This creates a new environment named "BeamShaping" in which all the requisite packages are pre-installed. Note that you can change the name of the environment if you change it in the yml *before* running the conda create.

Fair warning, when running 'vortex.py' if an SLM (or any secondary monitor) is not connected, the hologram will be shown directly on the primary monitor, in fullscreen, without an 'x' in the corner to close it. Be not afraid. Pressing any key will close the hologram.
