import tkinter as tk
from tkinter import ttk
import scrollableframe as sf


def populate(cnt):
    for i in range(cnt):
        sframe.add_widget(f'Label {i}')


def check(widgets):
    for widget in widgets:
        if widget.visible:
            print(f'{widget["text"]}: {widget.visible}')
    print()


if __name__ == '__main__':
    root = tk.Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=10)
    root.rowconfigure(0, weight=1)
    root.minsize(width=400, height=300)

    sframe = sf.ScrollableFrame(root)
    sframe.grid(column=0, row=0, sticky=tk.NSEW)
    populate(5)

    btn_frame = ttk.Frame(root)
    btn_frame.grid(column=0, row=1, sticky=tk.EW)

    add_btn = ttk.Button(btn_frame,
                         text='add',
                         command=lambda: sframe.add_widget(f'Add Lbl'))
    add_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

    test_btn = ttk.Button(btn_frame,
                          text='test',
                          command=lambda: check(sframe.widgets))
    test_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

    root.mainloop()
