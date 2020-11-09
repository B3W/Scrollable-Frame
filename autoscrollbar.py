'''
Module providing a scrollbar widget which can auto hide itself.
'''
import tkinter as tk
from tkinter import ttk


class AutoScrollbar(ttk.Scrollbar):
    '''
    A scrollbar that hides itself if it's not needed. Only
    works if you use the grid geometry manager.
    Reference: https://stackoverflow.com/q/41095385
    '''
    def __init__(self, master, column, row, span=1, *args, **kwargs):
        '''
        Initialize AutoScrollbar
        :param master: Parent widget for this Scrollbar
        :param column: Which column in master's grid to place Scrollbar
        :param row: Which row in master's grid to place Scrollbar
        :param span: Equivalent to 'rowspan' if vertical orientation,
        equivalent to 'columnspan' if horizontal orientation
        '''
        ttk.Scrollbar.__init__(self, master, *args, **kwargs)
        self.column = column
        self.row = row
        self.span = span
        self.hidden = False  # Flag tracking if scrollbar is visible

        # Initially set the scrollbar visible
        # Will get reversed in initial call to 'set' function if necessary
        self.__show()

    def set(self, lo, hi):
        '''
        Determines the displayed region of the AutoScrollbar
        '''
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # Only need to hide if the AutoScrollbar is currently visible
            if not self.hidden:
                self.__hide()
        else:
            # Only need to show if the AutoScrollbar is currently not visible
            if self.hidden:
                self.__show()

        ttk.Scrollbar.set(self, lo, hi)

    def __show(self):
        '''
        Helper function for making AutoScrollbar visible
        '''
        # NOTE  The 'orient' attribute of Scrollbar is a '_tkinter.Tcl_Obj'
        #       so it must be converted to 'str' before comparison
        orient = str(self.cget('orient'))

        if orient == tk.VERTICAL:
            sticky = (tk.N, tk.S)
            self.grid(column=self.column, row=self.row,
                      rowspan=self.span, sticky=sticky)
        else:
            sticky = (tk.E, tk.W)
            self.grid(column=self.column, row=self.row,
                      columnspan=self.span, sticky=sticky)

        self.hidden = False

    def __hide(self):
        '''
        Helper function for hiding AutoScrollbar
        '''
        self.grid_forget()
        self.hidden = True

    def pack(self, **kw):
        raise(tk.TclError, "cannot use pack with this widget")

    def place(self, **kw):
        raise(tk.TclError, "cannot use place with this widget")
