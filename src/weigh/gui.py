import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from .logger_core import (
    log_entry,
    undo_last_entry,
    totals_today_weight,
    get_sources_dict,
    get_types_dict,
)
import threading
import time
import os
import sys


ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")


def load_asset(name):
    return Image.open(os.path.join(ASSET_DIR, name))


class WeighGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.option_add("*Font", "Noto Sans 40")
        self.option_add("*Button.Font", "Noto Sans 32")
        self.option_add("*Label.Font", "Noto Sans 40")
        self.option_add("*Font", "helvetica 40")
        
        
        # Make fullscreen
        self.attributes("-fullscreen", True)
        
        # Allow ESC to close
        self.bind("<Escape>", lambda e: self.destroy())

        self.tk.call("tk", "scaling", 1.4)
        self.title("PineTab Food Logger")
        self.geometry("1280x800")
        self.configure(bg="white")

        self.current_weight = tk.DoubleVar(value=0.00)

        self.build_top_row()
        self.build_middle_row()
        self.build_bottom_row()
        self.build_bottom_controls()
        
        # simulate scale polling
        self.poll_scale()

    # -------------------------------------------------------

    def build_top_row(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="x", pady=10)

        # Pantry logo
        slfp = load_asset("slfp_logo.png")
        slfp.thumbnail((9999, 300))
        
        slfp_img = ImageTk.PhotoImage(slfp)
        self.slfp_img = slfp_img  # keep reference
        tk.Label(frame, image=slfp_img, bg="white").pack(side="left", padx=20)

        # Weight display
        self.weight_label = tk.Label(
            frame,
            text="0.00 lb",
            font=("Helvetica", 48, "bold"),
            bg="white",
        )
        self.weight_label.pack(side="left", expand=True)

        # Scale icon
        scale = load_asset("scale_icon.png")
        scale.thumbnail((9999, 300))
        scale_img = ImageTk.PhotoImage(scale)
        self.scale_img = scale_img
        tk.Label(frame, image=scale_img, bg="white").pack(side="right", padx=20)

    # -------------------------------------------------------

    def build_middle_row(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="x", pady=20)

        # Source dropdown
        tk.Label(frame, text="Source:", font=("Helvetica", 20), bg="white").pack(side="left", padx=10)

        self.source_var = tk.StringVar()
        self.source_dropdown = ttk.Combobox(
            frame,
            textvariable=self.source_var,
            state="readonly",
            width=20,
            font=("Helvetica", 20),
            values=list(get_sources_dict().keys())
        )
        self.source_dropdown.pack(side="left", padx=10)

        types = list(get_types_dict().keys())

        for t in types:
            btn = tk.Button(
                frame,
                text=t,
                font=("Helvetica", 18),
                width=10,
                height=2,
                command=lambda ty=t: self.log_type(ty),
            )
            btn.pack(side="left", padx=10)

    # -------------------------------------------------------

    def build_bottom_row(self):
        frame = tk.Frame(self, bg="white")
        frame.pack(fill="x", pady=20)

        self.daily_label = tk.Label(
            frame,
            text="Daily Total: 0.00 lb",
            font=("Helvetica", 24),
            bg="white",
        )
        self.daily_label.pack()

    # -------------------------------------------------------

    def build_bottom_controls(self):
        frame = ttk.Frame(self)
        frame.pack(fill="x", pady=15)

        quit_btn = ttk.Button(frame, text="CLOSE", command=self.destroy)
        quit_btn.pack(side="left", expand=True, fill="x", padx=20)

        reset_btn = ttk.Button(frame, text="RESET", command=self.reset_ui)
        reset_btn.pack(side="right", expand=True, fill="x", padx=20)

    def log_type(self, food_type):
        src = self.source_var.get()
        if not src:
            return

        log_entry(self.current_weight.get(), src, food_type)
        self.update_daily_totals()

    # -------------------------------------------------------

    def update_daily_totals(self):
        total = totals_today_weight()
        self.daily_label.configure(text=f"Daily Total: {total:.2f} lb")

    # -------------------------------------------------------

    def poll_scale(self):
        # Placeholder for real HID interface
        # For now display small noise
        new_weight = round((time.time() % 10) + 0.17, 2)
        self.current_weight.set(new_weight)
        self.weight_label.configure(text=f"{new_weight:.2f} lb")

        self.after(500, self.poll_scale)

    def reset_ui(self):
        self.weight_var.set("0.0")
        if self.source_values:
            self.source_var.set(self.source_values[0])

# ---------------------------------------------------------------

def main():
    app = WeighGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
