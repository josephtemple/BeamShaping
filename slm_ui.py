"""
slm_ui.py

Contains the UI for setting specific parameters of the SLM hologram (l, nx, ny) as well as the 
details of the imaging pixel sweep. That is, what offsets from perfectly centeres we will image
the beam for.
"""
import tkinter as tk
from tkinter import ttk

class SLMControlsUI():
    def __init__(self, master):
        # window setup
        self.master = master
        master.title("SLM Controls")
        frame_top = ttk.Frame(master)
        frame_top.pack(padx=10, pady=5, fill="x")

        # box and label for topological charge
        ttk.Label(frame_top, text="Topological Charge (l)", justify="center").pack()
        self.top_charge = tk.StringVar(value="2")
        self.top_charge_entry = ttk.Entry(frame_top, width=20, textvariable = self.top_charge)
        self.top_charge_entry.pack(pady=2)

        # box and label for n_x
        ttk.Label(frame_top, text="Horizontal Grooves (nₓ)", justify="center").pack()
        self.nx = tk.StringVar(value="100")
        self.nx_entry = ttk.Entry(frame_top, width=20, textvariable = self.nx)
        self.nx_entry.pack(pady=2)

        # box and label for n_y
        ttk.Label(frame_top, text="Vertical Grooves (nᵧ)", justify="center").pack()
        self.ny = tk.StringVar(value="100")
        self.ny_entry = ttk.Entry(frame_top, width=20, textvariable = self.ny)
        self.ny_entry.pack(pady=2)

        # 3 boxes and labels side by side for range to sweep x over and stepsize
        frame_x = ttk.Frame(master)
        frame_x.pack(padx=10, pady=5)

        ttk.Label(frame_x, text="x-offset start").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(frame_x, text="x-offset stop").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_x, text="x-step size").grid(row=0, column=2, padx=5, pady=2)

        self.x_start = tk.StringVar(value="-100")
        self.x_stop = tk.StringVar(value="100")
        self.x_step = tk.StringVar(value="10")

        self.x_start_entry = ttk.Entry(frame_x, width=10, textvariable = self.x_start)
        self.x_stop_entry = ttk.Entry(frame_x, width=10, textvariable = self.x_stop)
        self.x_step_entry = ttk.Entry(frame_x, width=10, textvariable = self.x_step)

        self.x_start_entry.grid(row=1, column=0, padx=5, pady=2)
        self.x_stop_entry.grid(row=1, column=1, padx=5, pady=2)
        self.x_step_entry.grid(row=1, column=2, padx=5, pady=2)

        # 3 boxes and labels side by side for range to sweep y over and stepsize
        frame_y = ttk.Frame(master)
        frame_y.pack(padx=10, pady=5)

        ttk.Label(frame_y, text="y-offset start").grid(row=0, column=0, padx=5, pady=2)
        ttk.Label(frame_y, text="y-offset stop").grid(row=0, column=1, padx=5, pady=2)
        ttk.Label(frame_y, text="y-step size").grid(row=0, column=2, padx=5, pady=2)

        self.y_start = tk.StringVar(value="-100")
        self.y_stop = tk.StringVar(value="100")
        self.y_step = tk.StringVar(value="10")

        self.y_start_entry = ttk.Entry(frame_y, width=10, textvariable = self.y_start)
        self.y_stop_entry = ttk.Entry(frame_y, width=10, textvariable = self.y_stop)
        self.y_step_entry = ttk.Entry(frame_y, width=10, textvariable = self.y_step)

        self.y_start_entry.grid(row=1, column=0, padx=5, pady=2)
        self.y_stop_entry.grid(row=1, column=1, padx=5, pady=2)
        self.y_step_entry.grid(row=1, column=2, padx=5, pady=2)

        # buttons to quit and start data gathering
        frame_buttons = ttk.Frame(master)
        frame_buttons.pack(pady=10)

        quit_btn = tk.Button(frame_buttons, text="QUIT", bg="red", fg="white", command=master.destroy)
        quit_btn.grid(row=0, column=0, padx=20)

        self.gather_clicked = False

        gather_btn = tk.Button(frame_buttons, text="GATHER", bg="green", fg="white", command=self.gather_button)
        gather_btn.grid(row=0, column=1, padx=20)

    def gather_button(self):
        if not self.gather_clicked:
            self.gather_clicked = True
            print("Data Gathering has begun! Closing UI...")

            self.values = self.get_values()
            # close the window
            self.master.destroy()

    def get_values(self):
        ui_value_dict = {
            "l" : int(self.top_charge.get()),
            "nx" : int(self.nx.get()),
            "ny" : int(self.ny.get()),

            "x_start" : int(self.x_start.get()),
            "x_stop" : int(self.x_stop.get()),
            "x_step" : int(self.x_step.get()),

            "y_start" : int(self.y_start.get()),
            "y_stop" : int(self.y_stop.get()),
            "y_step" : int(self.y_step.get()),

            "gather_clicked" : self.gather_clicked
        }
        return ui_value_dict       


if __name__ == "__main__":
    root = tk.Tk()
    app = SLMControlsUI(root)
    root.mainloop()



