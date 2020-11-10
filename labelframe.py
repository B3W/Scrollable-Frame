import tkinter as tk
from tkinter import ttk
from scrollableframe import ScrollableFrame
from scrollableframe import WidgetType


class LabelFrame(ScrollableFrame):
    '''Derived class that defines logic for adding a widget to the frame'''
    def add_label(self, text):
        label = ttk.Label(self.widget_frame, text=text, anchor=tk.CENTER)
        label.wtype = WidgetType.WTYPE_LEAF
        label.depth = label.master.depth + 1
        label.visible = False
        label.grid(column=0, row=self.num_widgets, sticky=tk.EW)
        self.widgets.append(label)
        self.num_widgets += 1
        self._check_visible_widget_range()
