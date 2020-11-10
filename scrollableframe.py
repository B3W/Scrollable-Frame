import autoscrollbar as asb
import enum
import math
import tkinter as tk
from tkinter import ttk


@enum.unique
class WidgetType(enum.Enum):
    '''Enum defining possible types of widgets'''
    WTYPE_ROOT_CONTAINER = enum.auto()      # Widget is a root container
    WTYPE_NONROOT_CONTAINER = enum.auto()   # Widget is non-root container
    WTYPE_LEAF = enum.auto()                # Widget is a leaf (non-container)


class ScrollableFrame(ttk.Frame):
    '''
    UI element displaying widgets that can be scrolled through. UI element also
    dynamically determines which widgets in the scrollable region are visible.
    '''
    def __init__(self, master, *args, **kwargs):
        # Initialize root frame
        ttk.Frame.__init__(self, master, *args, **kwargs)

        self.columnconfigure(0, weight=1)  # Canvas/Scrollable Frame
        self.columnconfigure(1, weight=0)  # AutoScrollbar
        self.rowconfigure(0, weight=1)

        self.widgets = []
        self.num_widgets = 0
        self.configuring = False
        self.wtype = WidgetType.WTYPE_ROOT_CONTAINER
        self.depth = 0  # Attibute indicating 'distance' from root container
        self.initial_check = False
        self.visible_start_index = -1
        self.VISIBLE_START_INDEX_BUFFER = 3
        self.visible_end_index = -1
        self.VISIBLE_END_INDEX_BUFFER = 3

        # Initialize Canvas to hold 'scrollable' frame
        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.wtype = WidgetType.WTYPE_NONROOT_CONTAINER
        self.canvas_frame.depth = self.canvas_frame.master.depth + 1
        self.canvas_frame.grid(column=0, row=0, sticky=tk.NSEW)

        self.canvas = tk.Canvas(self.canvas_frame, highlightthickness=0)
        self.canvas.wtype = WidgetType.WTYPE_NONROOT_CONTAINER
        self.canvas.depth = self.canvas.master.depth + 1
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize vertical AutoScrollbar and link to the Canvas
        self.vsb = asb.AutoScrollbar(self,
                                     column=1, row=0,
                                     orient=tk.VERTICAL,
                                     command=self.canvas.yview)

        self.canvas.configure(yscrollcommand=self.vsb.set)

        # Initialize 'scrollable' frame for actual message content
        self.widget_frame = ttk.Frame(self.canvas)
        self.widget_frame.wtype = WidgetType.WTYPE_NONROOT_CONTAINER
        self.widget_frame.depth = self.widget_frame.master.depth + 1
        self.widget_frame.columnconfigure(0, weight=1)

        canvas_win_location = (0, 0)
        self.cframe_id = self.canvas.create_window(canvas_win_location,
                                                   window=self.widget_frame,
                                                   anchor='nw')

        # Bind callbacks for when the Message Frame/Canvas is resized
        self.widget_frame.bind('<Configure>', self.__update_scrollregion)
        self.canvas.bind('<Configure>', self.__on_canvas_configure)

        # Bind callbacks for the mouse wheel
        self.widget_frame.bind('<Enter>', self.__bind_mousewheel)
        self.widget_frame.bind('<Leave>', self.__unbind_mousewheel)

    def scroll_bottom(self):
        self.canvas.update_idletasks()  # Let canvas finish layout calculations
        self.canvas.yview_moveto(1.0)   # Scroll to bottom of canvas
        self._check_visible_widget_range()

    def __update_visible_widgets(self, start_index, end_index):
        '''Updates which widgets are designated as visible'''
        if not self.initial_check:
            # Set initial values for visible widgets
            self.initial_check = True

            new_start_index = start_index - self.VISIBLE_START_INDEX_BUFFER
            new_start_index = max(0, new_start_index)
            self.visible_start_index = new_start_index

            new_end_index = end_index + self.VISIBLE_END_INDEX_BUFFER
            new_end_index = min(self.num_widgets - 1, new_end_index)
            self.visible_end_index = new_end_index

            for i in range(new_start_index, new_end_index + 1):
                self.widgets[i].visible = True
        else:
            # Update which widgets are now visible/not visible
            new_start_index = start_index - self.VISIBLE_START_INDEX_BUFFER
            new_start_index = max(0, new_start_index)

            if new_start_index < self.visible_start_index:
                for i in range(new_start_index, self.visible_start_index):
                    self.widgets[i].visible = True
            else:
                for i in range(self.visible_start_index, new_start_index):
                    self.widgets[i].visible = False

            self.visible_start_index = new_start_index

            new_end_index = end_index + self.VISIBLE_END_INDEX_BUFFER
            new_end_index = min(self.num_widgets - 1, new_end_index)

            if new_end_index < self.visible_end_index:
                for i in range(self.visible_end_index, new_end_index, -1):
                    self.widgets[i].visible = False
            else:
                for i in range(new_end_index, self.visible_end_index, -1):
                    self.widgets[i].visible = True

            self.visible_end_index = new_end_index

    def _check_visible_widget_range(self):
        '''Retrieves first and last visible widget in the scrollable frame'''
        if len(self.widgets) == 0:
            # No widgets == none visible
            return

        top = self.__get_first_visible_widget()

        if top is None or top.wtype != WidgetType.WTYPE_LEAF:
            # If the top is not recogized then none visible
            return

        # Get index of first visible widget in list
        top_index = self.widgets.index(top)

        bottom = self.__get_last_visible_widget()
        bottom_index = 0

        if bottom is None or bottom.wtype != WidgetType.WTYPE_LEAF:
            # Not enough widgets to cover the root container
            bottom_index = len(self.widgets) - 1
        else:
            # Get index of last visible widget in list
            bottom_index = self.widgets.index(bottom)

        self.__update_visible_widgets(top_index, bottom_index)

    def __get_first_visible_widget(self):
        '''Retrieves the first visible widget in the scrollable frame'''
        x = self.winfo_rootx() + 5
        y = self.winfo_rooty() + 5

        return self.winfo_containing(x, y)

    def __get_last_visible_widget(self):
        '''Retrieves the last visible widget in the scrollable frame'''
        x = self.winfo_rootx() + 5
        y = self.winfo_rooty() + self.winfo_height() - 5

        return self.winfo_containing(x, y)

    # CALLBACKS
    def __on_canvas_configure(self, event):
        '''Callback for canvas's <Configure> event'''
        if not self.configuring:
            # Configure and then delay until next config to lower CPU load
            self.configuring = True

            width = event.width
            self.__configure_canvas(width, False)
            self.after(75, self.__configure_canvas, width, True)

    def __configure_canvas(self, width, reset):
        self.canvas.itemconfigure(self.cframe_id, width=width)
        self._check_visible_widget_range()
        self.configuring = not reset

    def __update_scrollregion(self, event=None):
        '''Callback for inner frame's <Configure> event'''
        self.canvas.configure(scrollregion=self.canvas.bbox(tk.ALL))

    def __bind_mousewheel(self, event):
        '''Callback for inner frame's <Enter> event'''
        # Bind the root scrollable widget to the scrolling callback
        self.canvas.bind_all('<MouseWheel>', self.__on_mousewheel)

    def __unbind_mousewheel(self, event):
        '''Callback for inner frame's <Leave> event'''
        # Unbind the root scrollable widget from the scrolling callback
        self.canvas.unbind_all('<MouseWheel>')

    def __on_mousewheel(self, event):
        '''Callback for all widget's <Mousewheel> event'''
        # Do not allow scrolling if scrollbars are hidden
        if self.vsb.hidden:
            return

        # Get sign of delta then reverse to get scroll direction
        scroll_dir = -1 * int(math.copysign(1, event.delta))
        self.canvas.yview_scroll(scroll_dir, 'units')
        self._check_visible_widget_range()
