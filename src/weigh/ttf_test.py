import tkinter as tk
from tkinter import font as tkfont

root = tk.Tk()

try:
    f = tkfont.Font(family="DejaVu Sans", size=40)
    tk.Label(root, text="DejaVu Sans 40", font=f).pack()
    print("Loaded TrueType font successfully.")
except Exception as e:
    print("Failed:", e)

root.mainloop()
