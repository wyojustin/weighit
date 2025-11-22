import tkinter as tk
import tkinter.font as tkfont

root = tk.Tk()

# Try switching 1.0, 1.5, 2.0, 2.5, 3.0
root.tk.call("tk", "scaling", 2.0)

for size in [20, 40, 80]:
    tk.Label(root, text=f"Size {size}", font=("Helvetica", size)).pack()

root.mainloop()
