import tkinter as tk
from tkinter import ttk
import scrollableframe as sf


if __name__ == '__main__':
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=10)
    root.rowconfigure(0, weight=1)
    root.minsize(width=400, height=300)

    frame = sf.ScrollableFrame(root)
    frame.grid(column=0, row=0, sticky=tk.NSEW)
    frame.populate(50)

    btn = ttk.Button(root,
                     text='test',
                     command=lambda: frame.check())
    btn.grid(column=0, row=1, sticky=tk.S)

    root.mainloop()
