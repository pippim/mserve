# -*- coding: utf-8 -*-
#==============================================================================
#
#       toolkit.py - tkinter (took kit interface) functions
#
#==============================================================================

# identical imports in mserve
from __future__ import print_function       # Must be first import
from __future__ import with_statement       # Error handling for file opens

# Must be before tkinter and released from interactive. Required to insert
# from clipboard.
#import gtk                     # Doesn't work. Use xclip instead
#gtk.set_interactive(False)

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as font
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import tkinter.scrolledtext as scrolledtext
    PYTHON_VER = "3"
except ImportError:  # Python 2
    import Tkinter as tk
    import ttk
    import tkFont as font
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext
    PYTHON_VER = "2"
# print ("Python version: ", PYTHON_VER)

import time
from datetime import datetime
from ttkwidgets import CheckboxTreeview
from collections import OrderedDict, namedtuple

import global_variables as g
import external as ext      # Time formatting routines
import image as img

'''
List all objects in play next song
https://stackoverflow.com/questions/60978666/get-list-of-toplevels-on-tkinter
'''
LAST_TIME = 0.0             # So headings only appear once during recursion
WIDGET_COUNT = 0             # Last call's subtotal
#import pprint


def list_widgets(level, scan="All"):
    """
    List all widgets of a certain type (or "All") for object

    widget_list: [<Tkinter.Label instance at 0x7f16387b63f8>]
                               instance_hex: 0x7f16387b63f8
    """
    global LAST_TIME, WIDGET_COUNT
    now = time.time()
    if not int(now) == int(LAST_TIME):
        if WIDGET_COUNT > 0:
            # Print total from last run
            print('Number of widgets:', WIDGET_COUNT)
            WIDGET_COUNT = 0
        print('\n============= list_widgets() called at:', ext.t(now), '=============')
        LAST_TIME = now

    for k, v in level.children.items():

        if isinstance(v, tk.Toplevel) and (scan == "All" or scan == "Toplevel"):
            print('Toplevel :', 'key;', k, 'value:', v)

        elif isinstance(v, tk.Frame) and (scan == "All" or scan == "Frame"):
            print('Frame    :', k, v)
            if not isinstance(v, tk.Frame):
                print("ERROR: Not a tkinter Frame !!!!!!!")

        elif (isinstance(v, tk.Label)) and (scan == "All" or scan == "Label"):
            # elif isinstance(v, tk.Label) and (scan=="Label" or scan=="All"):
            # elif isinstance(v, tk.Label) and (scan=="Label"):
            # elif isinstance(v, tk.Label):  all were BROKEN but now work???
            print('Label    :', k, v)
            instance_hex = hex(int(k))
            tkinter_label = '<Tkinter.Label instance at ' + \
                            instance_hex + '>'
            print('\t Instance :', k, tkinter_label)
            if not isinstance(v, tk.Label):
                print("ERROR: Not a tkinter Label !!!!!!!", scan)
            
        elif isinstance(v, tk.Button) and (scan == "All" or scan == "Button"):
            print('Button   :', k, v)

        elif isinstance(v, ttk.Treeview) and (scan == "All" or scan == "Treeview"):
            print('Treeview :', k, v)

        elif isinstance(v, tk.Scrollbar) and (scan == "All" or scan == "Scrollbar"):
            print('Scrollbar:', k, v)

        elif isinstance(v, tk.Menu) and (scan == "All" or scan == "Menu"):
            print('Menu     :', k, v)

        elif isinstance(v, tk.Canvas) and (scan == "All" or scan == "Canvas"):
            print('Canvas   :', k, v)

        elif scan == "All" or scan == "Other":
            print('Other    :', k, v)

        else:
            # This instance doesn't match but drill down and return
            print("No match scanning for:", scan)
            toplevels(v, scan=scan)
            WIDGET_COUNT += 1
            return

        print('\t Geometry  :', v.winfo_geometry(),
              "x-offset:", v.winfo_x(), "y-offset:", v.winfo_y())

        try:
            # pprint.pprint(v.config())
            print('\t Text      :', v.cget('text'))
        except tk.TclError:
            pass

        try:
            # pprint.pprint(v.config())
            print('\t Font      :', v.cget('font'))
            try:
                tt_font = font.Font(font=label['font'])
                print(tt_font.actual())
            except NameError:
                # Maybe try something like this instead:
                #         # Creating a Font object of "TkDefaultFont"
                #         self.defaultFont = font.nametofont("TkDefaultFont")
                print("tt_font = font.Font(font=label['font']): 'label' is undefined???")
        except tk.TclError:
            pass

        try:
            print('\t Foreground:', v.cget('fg'), 'Background:', v.cget('bg'))
        except tk.TclError:
            pass

        keys = v.keys()
        for key in keys:
            print("\t Attribute : {:<20}".format(key), end=' ')
            value = v[key]
            value_type = type(value)
            try:
                print('Type: {:<25} Value: {}'.format(str(value_type), value))
            except TypeError:
                # <_tkinter_TCL_Obj> doesn't format properly...
                print('Type:', value_type, 'value:', value)

        list_widgets(v, scan=scan)
        WIDGET_COUNT += 1


def config_all_labels(level, **kwargs):
    """ Configure all tk labels within a frame (doesn't work for toplevel?).

        level = frame name, eg self.play_frm

        **kwargs = tkinter_button.configure(keywords and values). For example:
            fg="#000000", bg="#ffffff", pad x=5

    """

    global LAST_TIME, WIDGET_COUNT
    now = time.time()
    if not int(now) == int(LAST_TIME):
        if WIDGET_COUNT > 0:
            # print('Number of widgets:', WIDGET_COUNT)
            WIDGET_COUNT = 0
        # print('\n========= config_all_labels() called at:', ext.t(now),'=========')
        LAST_TIME = now

    for k, v in level.children.items():

        if isinstance(v, tk.Label):
            '''
            print('Label    :', k, v)
            wrapper = kwargs
            print('\t **kwargs :', wrapper)
            instance_hex = hex(int(k))
            tkinter_label = ('<Tkinter.Label instance at ' + \
                             instance_hex + '>')
            print('\t Instance :', k, tkinter_label)
            #tkinter_label.configure(**kwargs)      # THIS IS STRING!
            '''
            if v["image"] == "":
                # We can't configure image labels that have a value
                v.configure(**kwargs)

        config_all_labels(v, **kwargs)
        WIDGET_COUNT += 1


def config_all_buttons(level, **kwargs):
    """ Configure all tk buttons within a frame (doesn't work for toplevel?).

        level = frame name, eg self.play_btn

        **kwargs = tkinter_button.configure(keywords and values). For example:
            fg="#000000", bg="#ffffff", pad x=5
    """
    for k, v in level.children.items():

        if isinstance(v, tk.Button):
            if v["image"] == "":
                # We can't configure image labels that have a value
                v.configure(**kwargs)

        config_all_buttons(v, **kwargs)


def config_all_canvas(level, **kwargs):
    """ Configure all tk canvass within a frame

        level = frame name, eg self.play_F3_panel

        **kwargs = tkinter_button.configure(keywords and values). For example:
            fg="#000000", bg="#ffffff", pad x=5
    """
    for k, v in level.children.items():

        if isinstance(v, tk.Canvas):
            v.configure(**kwargs)

        config_all_canvas(v, **kwargs)


# ==============================================================================
#
#       CustomScrolledText class - scrollable text with tag highlighting
#
# ==============================================================================


class CustomScrolledText(scrolledtext.ScrolledText):
    """ A text widget with a new method, highlight_pattern()

        REQUIRES:

            import tkinter.scrolledtext as scrolledtext


        TODO: Direct copied from ~/mserve/encoding.py so put into toolkit.py

    example:

    text = CustomScrolledText()
    text.tag_configure("red", foreground="#ff0000")
    text.highlight_pattern("this should be red", "red")

    The highlight_pattern method is a simplified python
    version of the tcl code at http://wiki.tcl.tk/3246
    """

    def __init__(self, *args, **kwargs):
        scrolledtext.ScrolledText.__init__(self, *args, **kwargs)

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        """Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        """

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
            if index == "":
                break
            # degenerate pattern which matches zero-length strings
            if count.get() == 0:
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")

    def unhighlight_pattern(self, pattern, tag, start="1.0", end="end",
                            regexp=False):
        """Remove the given tag to all text that matches the given pattern
        """

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
            if index == "":
                break
            # degenerate pattern which matches zero-length strings
            if count.get() == 0:
                break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_remove(tag, "matchStart", "matchEnd")


# ==============================================================================
#
#       DictTreeview class - Define Data Dictionary Driven treeview
#
# ==============================================================================


class DictTreeview:
    """ Use list of column data dictionaries to create treeview

        Data dictionaries reduce programmer burden of specifying which
        columns to display, the order of the columns and in the future
        filtering which rows are displayed for tree.insert() operations.
    """
    def __init__(self, tree_dict, toplevel, master_frame, show='headings', columns=(),
                 sbar_width=12):

        self.toplevel = toplevel
        self.master_frame = master_frame    # Master frame for treeview frame
        self.tree_dict = tree_dict          # Data dictionary
        self.attached = OrderedDict()       # Mgs attached, detached, skipped

        ''' Key fields may be hidden. Add as last column not displayed.
        '''
        columns_list = list(columns)
        for d in self.tree_dict:
            if d['select_order'] == 0 and d['key'] is True:
                # Add to list
                columns_list.append(d['column'])

        columns = tuple(columns_list)
        self.columns = columns              # Column names in treeview
        self.column_widths = []             # The width of each treeview column

        # Create a frame for the treeview and scrollbar(s).
        self.frame = tk.Frame(master_frame)
        tk.Grid.rowconfigure(self.frame, 0, weight=1)
        tk.Grid.columnconfigure(self.frame, 0, weight=1)
        self.frame.grid(row=0, column=0, sticky=tk.NSEW)

        ''' CheckboxTreeview List Box, Columns and Headings '''
        # Call first_selected, next_selected to get dictionaries in order
        # columns = build_columns()
        # Move show=show, below after column configuration
        self.tree = CheckboxTreeview(self.frame, columns=columns)
        self.tree['displaycolumns'] = self.columns

        # Set selected columns
        self.last_column = 0
        for curr in range(1, len(columns) + 1):
            for d in self.tree_dict:
                if d['select_order'] == curr:
                    # We found the current column to display
                    if d['column'] != columns[curr - 1]:
                        print('toolkit.py DictTreeview(): Columns do not match.\nDictionary:',
                              d['column'], '\ncolumns tuple:', columns[curr - 1])
                        exit()

                    # Format current column
                    # print(d['column'], d['display_width'], d['display_min_width'], 'stretch:', d['stretch'])
                    self.tree.column(d['column'], width=d['display_width'],
                                     minwidth=d['display_min_width'],
                                     anchor=d['anchor'], stretch=d['stretch'])
                    self.tree.heading(d['column'], text=d['heading'])
                    self.last_column += 1

        # Set unselected columns that are key fields
        for d in self.tree_dict:
            if d['select_order'] == 0 and d['key'] is True:
                # Format current column
                # print(d['column'], d['display_width'], d['display_min_width'], 'stretch:', d['stretch'])
                self.tree.column(d['column'], width=0, minwidth=0)
                self.tree.heading(d['column'], text=d['heading'])
                self.last_column += 1

        # Move show below column config as per:
        #   https://stackoverflow.com/a/67839537/6929343
        self.tree['show'] = show

        # DEBUGGING -  Dump out column values
        #for col in columns:
        #    print(self.tree.column(col))
        #    print(self.tree.heading(col))

        style = ttk.Style()
        print('style.theme_names():', style.theme_names())
        style.configure("Treeview.Heading", font=(None, g.MED_FONT),
                        rowheight=int(g.MED_FONT * 2.2))
        row_height = int(g.MON_FONTSIZE * 2.2)
        style.configure("Treeview", font=(None, g.MON_FONTSIZE),
                        rowheight=row_height)
        style.configure('Treeview', indent=row_height + 6)

        ''' Create images for checked, unchecked and tristate '''
        self.checkboxes = img.make_checkboxes(row_height - 8, 'black',
                                              'white', 'deepskyblue')
        self.tree.tag_configure("unchecked", image=self.checkboxes[0])
        self.tree.tag_configure("tristate", image=self.checkboxes[1])
        self.tree.tag_configure("checked", image=self.checkboxes[2])

        ''' Create images for open, close and empty '''
        width = row_height - 9
        self.triangles = []  # list to prevent Garbage Collection
        # TODO: If triangles created already, they are not remade so lost here!
        img.make_triangles(self.triangles, width, 'black', 'grey')

        ''' Configure tag for row highlight '''
        self.tree.tag_configure('highlight', background='lightblue')
        self.tree.bind('<Motion>', self.highlight_row)
        self.tree.bind("<Leave>", self.leave)
        self.last_row = None

        ''' Put on grid '''
        self.tree.grid(row=0, column=0, sticky=tk.NSEW)

        ''' Treeview Scrollbars '''
        # Create a vertical scrollbar linked to the frame.
        v_scroll = tk.Scrollbar(self.frame, orient=tk.VERTICAL, width=sbar_width,
                                command=self.tree.yview)
        v_scroll.grid(row=0, column=1, sticky=tk.NS)
        self.tree.configure(yscrollcommand=v_scroll.set)

        # Create a horizontal scrollbar linked to the frame.
        h_scroll = tk.Scrollbar(self.frame, orient=tk.HORIZONTAL, width=sbar_width,
                                command=self.tree.xview)
        h_scroll.grid(row=1, column=0, sticky=tk.EW)
        self.tree.configure(xscrollcommand=h_scroll.set)
        self.col_count = 0
        # print('columns:', self.columns)

    def insert(self, parent_iid="", row=None, iid="", tags="unchecked"):
        """ Insert new row into treeview. """
        if row is None:
            print('toolkit.py - dict_tree.insert() - row is required parameter')
            return

        values = []
        for col in self.columns:
            data_dict = get_dict_column(col, self.tree_dict)

            # DEBUGGING - Print first 10 encounters
            #self.col_count += 1
            #if self.col_count < 10:
            #    print(data_dict)
            #    print(row)
            #elif self.col_count == 10:
            #    print('column count reached:', self.col_count)

            unmasked_value = row[data_dict['var_name']]
            if data_dict['format'] is not None:
                mask = data_dict['format']
                try:
                    values.append(mask.format(unmasked_value))
                except ValueError:
                    print('Invalid format:', data_dict['format'],
                          'var_name:', data_dict['var_name'],
                          'rwo_id:', row['Id'],)
                    values.append("KeyError:" + str(unmasked_value))
                except KeyError:
                    values.append("KeyError:" + str(unmasked_value))
            else:
                values.append(unmasked_value)

        self.tree.insert(parent_iid, tk.END, iid=iid, values=values, tags=tags)
        self.tree.tag_bind(iid, '<Motion>', self.highlight_row)


    def update_column(self, iid, search, value):
        """ Update column with new value """

        # Get all column values
        values = self.tree.item(iid, "values")

        # Loop through all columns in treeview
        for col in self.columns:
            # Get data dictionary for current column
            data_dict = get_dict_column(col, self.tree_dict)
            # Does data dictionary column name match search name?
            if data_dict['column'] != search:
                continue  # Try next element

            #print('values:', values)
            view_order = data_dict['select_order']
            if view_order < 1 or view_order > len(values):
                print('toolkit.py.update_column() search column ERROR:', search)
                print('    invalid view_order retrieved:', view_order, 'max:', len(values))
                print_dict_columns(self.tree_dict)
                return None

            values_l = list(values)
            values_l[view_order - 1] = value
            self.tree.item(iid, values=values_l)
            return True

        print('toolkit.py.update_column() search column not found:', search)
        print_dict_columns(self.tree_dict)
        print('values:', values)
        return None

    def highlight_row(self, event):
        """ Cursor hovering over row highlights it in light blue

            TODO: Port to mserve chronology treeview.

        """
        tree = event.widget
        item = tree.identify_row(event.y)
        tree.tk.call(tree, "tag", "remove", "highlight")
        tree.tk.call(tree, "tag", "add", "highlight", item)
        self.last_row = item

    def leave(self, event):
        """
        Un-highlight row just left
        :param event:
        :return:
        """
        if self.last_row is not None:
            tree = event.widget
            tree.tk.call(self.tree, "tag", "remove", "highlight")
            self.last_row = None

    def column_value(self, values, search):
        """
            Gets value matching treeview column name from treeview row.
            Primarily used to get message_id which may be hidden column.
            As of July 15, 2021 message_id is a key field in every view.

            Notes:
            ======
                NOT tested for 'tree' (column #0)
                Does NOT do formatting

            :param values is treeview row of values
            :param search is string for data dictionary field name
            :returns matching value from passed values list

        """

        # Loop through all columns in treeview
        for col in self.columns:
            # Get data dictionary for current column
            data_dict = get_dict_column(col, self.tree_dict)
            # Does data dictionary column name match search name?
            if data_dict['column'] != search:
                continue  # Try next element

            #print('values:', values)
            view_order = data_dict['select_order']
            if view_order == 0 and data_dict['key'] is True:
                # TODO: Currently only support 1 hidden key field as last
                #       column which is invisible in treeview.
                return values[len(self.columns) - 1]
            #print('column #:', view_order, 'column name:', search)
            # July 18 bug:
            # message_id = self.lib_view.column_value(values, "message_id")
            # return values[view_order - 1]
            # IndexError: string index out of range
            if view_order < 1 or view_order > len(values):
                # NOTE: After writing this code error never occurred. At time
                #       of writing also removed some garbage code just before
                #       bottom return statement.
                print('toolkit.py.column_value() search column ERROR:', search)
                print('    invalid view_order retrieved:', view_order, 'max:', len(values))
                print_dict_columns(self.tree_dict)
                return None

            return values[view_order - 1]

        print('toolkit.py.column_value() search column not found:', search)
        print_dict_columns(self.tree_dict)
        print('values:', values)
        return None

    def column_width(self, search):
        """
            Gets column width matching treeview column name from treeview.
            Used for painting red rectangles over columns on screenshot.

            Notes:
            ======
                NOT tested for 'tree' (column #0)
                Does NOT do formatting

            :param search is string for data dictionary field name
            :returns column width for passed column number

        """

        # If column number past last column it's an error
        for col in self.columns:
            # Get data dictionary for current column
            #         self.column_widths = []             # The width of each treeview column
            data_dict = get_dict_column(col, self.tree_dict)
            if search > len(self.columns):
                print('toolkit.py.column_width() search column ERROR:', search)
                print('    invalid view_order retrieved:', view_order, 'max:', len(values))
                print(data_dict['var_name'])
                print_dict_columns(self.tree_dict)
                return None

            return values[view_order - 1]

        print('toolkit.py.column_value() search column not found:', search)
        print_dict_columns(self.tree_dict)
        print('values:', values)
        return None

    def is_attached(self, msgId):
        return self.attached[msgId] is True

    def is_detached(self, msgId):
        return self.attached[msgId] is False

    def is_skipped(self, msgId):
        return self.attached[msgId] is None


def select_dict_all(dict_list):
    for curr in range(1, len(dict_list)):
        for d in dict_list:
            d['select_order'] = curr


def unselect_dict_all(dict_list):
    for d in dict_list:
        d['select_order'] = 0


def select_dict_columns(columns, dict_list):
    """ Select columns in order.
        Returns nothing because list is changed in place.

        :param  columns list or tuple of column names in gmail message header
        :param  dict_list is list of dictionaries

    """
    unselect_dict_all(dict_list)
    curr = 1

    for column in columns:
        for i, d in enumerate(dict_list):
            if d['column'] == column:
                d['select_order'] = curr
                dict_list[i] = d
                curr += 1
                break


def unselect_dict_columns(columns, dict_list):
    """ Unselect columns.
        Returns nothing because list is changed in place.

        :param  columns list or tuple of column names in gmail message header
        :param  dict_list is list of dictionaries

    """
    unselect_dict_all(dict_list)
    curr = 1

    # TODO: after removing a column rest must be renumbered !!!
    for column in columns:
        for i, d in enumerate(dict_list):
            if d['column'] == column:
                d['select_order'] = curr
                dict_list[i] = d
                curr += 1
                break


def get_dict_column(column, dict_list):
    """ Return data dictionary for search column
    """
    for d in dict_list:
        if d['column'] == column:
            return d


def print_dict_columns(dict_list):
    """ For debugging purposes.
         {"column": "snippet", "heading": "Snippet", "sql_table": "Header",
          "var_name": "snippet", "select_order": 0, "unselect_order": 9,
          "anchor": "wrap", "instance": str, "format": None, "display_width": 60,
          "display_min_width": 10, "display_long": 100, "stretch": 1}

    """
    print('\nDATA DICTIONARY\n==============================')
    ''' TODO: Print in selected order first, then unselected order '''
    for d in dict_list:
        print('\ncolumn         :', d['column'],      '  \theading          :',
              d['heading'],        '\tsql_table     :', d['sql_table'])
        print('  var_name     :', d['var_name'],      '    \tselect_order     :',
              d['select_order'], '\t\tunselect_order:', d['unselect_order'])
        print('  anchor       :', d['anchor'],        '\t\tinstance  :',
              d['instance'],       '\tformat        :', d['format'])
        print('  display_width:', d['display_width'], '\t\tdisplay_min_width:',
              d['display_min_width'], '\t\tdisplay_long  :',
              d['display_long'])
        print('  stretch      :', d['stretch'], '\t\tkey              :',
              d['key'])


class SearchText:
    """ Search for string in text and highlight it from:
    https://www.geeksforgeeks.org/search-string-in-text-using-python-tkinter/
    """
    def __init__(self, view, column=None, find_str=None, find_op='in'):
        # root window is the parent window
        self.view = view
        self.toplevel = view.toplevel
        self.tree = view.tree
        self.dict = view.tree_dict
        self.attached = view.attached
        self.column = column
        self.find_str = find_str
        self.find_op = find_op
        # print('column:', column, 'find_str:', find_str)

        if self.find_str is not None:
            return  # search string passed, no need for frame

        self.frame = tk.Frame(self.toplevel)
        self.frame.grid()

        # adding label to search box
        tk.Label(self.frame, text='Text to find:').pack(side=tk.LEFT)

        # adding of single line text box
        self.edit = tk.Entry(self.frame)

        # positioning of text box
        self.edit.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        # setting focus
        self.edit.focus_set()

        # adding of search button  TODO: Expand with tooltips
        but2 = tk.Button(self.frame, text='???  Close')
        but2.pack(side=tk.RIGHT)
        but2.config(command=self.close)

        butt = tk.Button(self.frame, text='????  Find')
        butt.pack(side=tk.RIGHT)
        butt.config(command=self.find)

    def find(self):
        """ Search treeview for string all string columns
        """
        if self.find_str is not None:
            print('toolkit.py.SearchText.find_one() should have been called.')
            self.find_one()
            return

        # ext.t_init('reattach')
        self.reattach()         # Put back items excluded on last search
        # ext.t_end('no print')   # For 1200 messages 0.00529 seconds

        # returns to widget currently in focus
        s = self.edit.get()

        if s:
            for iid in self.tree.get_children():
                # searches for desired string
                values = self.tree.item(iid)['values']

                if any(s.lower() in t.lower() for t in values if isinstance(t, basestring)):
                    # Searching all columns of basestring type
                    continue

                self.tree.detach(iid)
                self.attached[iid] = False

        self.edit.focus_set()

    def find_one(self):
        """ Search treeview for single column of any type (not just strings)
            There is no GUI input for search text.
        """
        self.reattach()         # Put back items excluded on last search

        s = self.find_str
        for iid in self.tree.get_children():
            # searches for desired string
            values = self.tree.item(iid)['values']
            one_value = self.view.column_value(values, self.column)

            if self.find_op == 'in':
                if s.lower() in one_value.lower():
                    #print('iid:', iid, 'values:', values)
                    continue
            elif self.find_op == '<=':
                if s > one_value:
                    #print('iid:', iid, 'values:', values)
                    continue
            else:
                # Limited number of operations supported on Aug 2, 2021.
                print('toolkit.py.SearchText.find_one() invalid find_op:',
                      self.find_op)

            self.tree.detach(iid)
            self.attached[iid] = False


    def reattach(self):
        """ Reattach items detached
            NOTE: Sort order drastically changes. Consider repopulate
                  instead.
        """
        i_r = -1  # https://stackoverflow.com/a/47055786/6929343
        for msgId in self.attached.keys():
            # If not attached then reattach it
            if self.attached[msgId] is False:
                i_r += 1
                self.tree.reattach(msgId, '', i_r)
                self.attached[msgId] = True

    def close(self):
        """ Remove find search bar """
        self.reattach()
        if self.find_str is None:
            self.frame.grid_remove()  # Next pack is faster this way?


'''
Publish to: https://stackoverflow.com/a/51425272/6929343

TODO -  We are looping through all columns. We only want the ones
        in currently visible scrolled region.
'''

try:  # Python 3
    import tkinter as tk
except ImportError:  # Python 2
    import Tkinter as tk
from PIL import Image, ImageTk
from collections import namedtuple
from os import popen
BUTTON_HEIGHT = 63                  # Button region to black out during move


class MoveTreeviewColumn:
    """ Shift treeview column to preferred order """

    def __init__(self, toplevel, treeview, row_release=None):

        self.toplevel = toplevel
        self.treeview = treeview
        self.row_release = row_release      # Button-Release not on heading
        self.eligible_for_callback = False  # If button-release in cell region
        self.region = None                  # Region of treeview clicked

        self.col_cover_top = None           # toplevel move columns
        self.col_top_is_active = False      # column move in progress?
        self.canvas = None                  # tk Canvas with column photos
        self.col_being_moved = None         # Column being moved in '#?' form
        self.col_swapped = False            # Did we swap a column?

        self.images = []                    # GIC protected image list
        self.canvas_names = []              # treeview column names
        self.canvas_widths = []             # matching widths
        self.canvas_objects = []            # List of canvas objects
        self.canvas_x_offsets = []          # matching x-offsets within canvas

        self.canvas_index = None            # Canvas index being moved
        self.canvas_name = None             # Treeview column name
        self.canvas_object = None           # Canvas item object being moved
        self.canvas_original_x = None       # Canvas item starting offset
        self.start_mouse_pos = None         # Starting position to calc delta

        self.treeview.bind("<ButtonPress-1>", self.start)
        self.treeview.bind("<ButtonRelease-1>", self.stop)
        self.treeview.bind("<B1-Motion>", self.motion)

    def close(self):
        self.treeview.unbind("<ButtonPress-1>")
        self.treeview.unbind("<ButtonRelease-1>")
        self.treeview.unbind("<B1-Motion>")

    def start(self, event):
        """
            Button 1 was just pressed for library treeview or backups treeview

        :param event: tkinter event
        :return:
        """

        #print('<ButtonPress-1>', event.x, event.y)
        self.region = self.treeview.identify("region", event.x, event.y)

        if self.region != 'heading':
            self.eligible_for_callback = True  # If button-release in cell region
            return

        self.eligible_for_callback = False     # If button-release in cell ignore

        Mouse = namedtuple('Mouse', 'x y')
        # noinspection PyArgumentList
        self.start_mouse_pos = Mouse(event.x, event.y)

        if self.col_cover_top is not None:
            print('toolkit.py MoveTreeviewColumn attempting to create self.col_cover_top a second time.')
            return

        self.create_move_column()
        if self.col_top_is_active is False:
            return  # Released button quickly or error creating top level

        # The column being moved - Recalculated after snap to grid
        self.col_being_moved = self.treeview.identify_column(event.x)
        #print('self.col_being_moved:', self.col_being_moved)
        self.get_source(self.col_being_moved)
        self.treeview.config(cursor='boat red red')  # boat cursor supports red
        self.col_swapped = False
        #print('\n columns BEFORE:', self.canvas_names)

    def stop(self, event):
        """ Determine if we were in motion before we lifted mouse button
        """
        if self.region != 'heading':
            # If button release not on heading call optional row_release
            if self.row_release is not None and self.eligible_for_callback:
                self.row_release(event)
            return

        ''' Destroy toplevel used for moving columns on canvas '''
        if self.col_top_is_active:
            # Destroy top level window covering up old music player position
            if self.col_cover_top is not None:
                if self.col_swapped:
                    #print('columns AFTER :', self.canvas_names)
                    self.treeview["displaycolumns"] = self.canvas_names
                    self.toplevel.update_idletasks()  # just in case
                self.col_cover_top.destroy()
                self.col_cover_top = None
            self.col_top_is_active = False
            self.treeview.config(cursor='')

    def motion(self, event):
        """
        What if only 1 column?

        What if horizontal scroll and non-displayed columns to left or right
        of displayed treeview columns? Need to compare 'displaycolumns' to
        current treeview.

        :param event: Tkinter event with x, y, widget
        :return:
        """
        if self.region != 'heading':
            return

        # Calculate delta - distance travelled since startup or snap to grid
        change = event.x - self.start_mouse_pos.x

        # Calculate new start, middle and ending x offsets for source object
        new_x = int(self.canvas_original_x + change)  # Sometimes we get float?
        new_middle_x = new_x + self.canvas_widths[self.canvas_index] // 2
        new_x2 = new_x + self.canvas_widths[self.canvas_index]
        self.canvas.coords(self.canvas_object, (new_x, 0))  # Move on screen

        ''' Make column snap to next (jump) when over half way -
            Either half of target is covered or half of source
            has moved into target 
        '''
        if change < 0:  # Mouse is moving column to the left
            if self.canvas_index == 0:
                return  # We are already first column on left
            target_index = self.canvas_index - 1
            target_start_x, target_middle_x, target_end_x = self.get_target(
                target_index)
            if new_x > target_middle_x and new_middle_x > target_end_x:
                return  # Not eligible for snap to grid

        elif change > 0:  # Mouse is moving column to the right
            if self.canvas_index == len(self.canvas_x_offsets) - 1:
                return  # We are already last column on right
            target_index = self.canvas_index + 1
            target_start_x, target_middle_x, target_end_x = self.get_target(
                target_index)
            if new_x2 < target_middle_x and new_middle_x < target_start_x:
                return  # Not eligible for snap to grid
        else:
            #print('toolkit.py MoveTreeviewColumn motion() called with no motion.')
            # Common occurrence when mouse moves fraction back and forth
            return  # Mouse didn't change position

        ''' Swap our column and the target column beside us (snap to grid).
            Calculate jump factor and then make mouse jump by same amount
        '''

        ''' Diagnostic section
        print('\n<B1-Motion>', event.x, event.y)
        print('\tcanvas_index   :', self.canvas_index,
              '\ttarget_index:  :', target_index,
              '\toriginal_x     :', self.canvas_original_x)
        print('\tnew_x          :', new_x,
              '\tnew_middle_x   :', new_middle_x,
              '\tnew_x2         :', new_x2)
        print('\ttarget_start_x :', target_start_x,
              '\ttarget_middle_x:', target_middle_x,
              '\ttarget_end_x   :', target_end_x)
        '''

        if target_index < self.canvas_index:
            # snapping to grid on left
            if self.canvas_index == 0:
                return  # Can't go before first column
            new_target_x = self.canvas_x_offsets[target_index] + \
                self.canvas_widths[self.canvas_index]
            new_source_x = self.canvas_x_offsets[target_index]
        else:
            # snapping to grid on right
            if self.canvas_index == len(self.canvas_widths) - 1:
                return  # Can't go past last column
            new_source_x = self.canvas_x_offsets[self.canvas_index] + \
                self.canvas_widths[target_index]
            new_target_x = self.canvas_x_offsets[self.canvas_index]

        # Swap lists at target index and self.canvas_index
        source_old_x = self.canvas.coords(self.canvas_object)[0]
        self.source_to_target(target_index, new_target_x, new_source_x)
        source_new_x = self.canvas.coords(self.canvas_object)[0]
        source_x_jump = source_new_x - source_old_x
        #print('source_x_jump:', source_x_jump)

        # Move mouse on screen to reflect snapping to grid
        self.treeview.unbind("<B1-Motion>")            # Don't call ourself
        ''' If you don't have xdotool installed, activate following code
         current_mouse_xy = self.toplevel.winfo_x() + event.x + source_x_jump
         window_mouse_xy = self.toplevel.winfo_y() + event.y
        # mouse_move_to takes .1 to .14 seconds and flickers new window
        move_mouse_to( current_mouse_xy,  window_mouse_xy)
        # xdotool takes .006 to .012 seconds and no flickering window
        '''
        popen("xdotool mousemove_relative -- " + str(int(source_x_jump)) + " 0")
        self.treeview.bind("<B1-Motion>", self.motion)

        # Recalibrate mouse starting position within toplevel
        Mouse = namedtuple('Mouse', 'x y')
        # noinspection PyArgumentList
        self.start_mouse_pos = Mouse(event.x + source_x_jump, event.y)

        self.col_swapped = True  # We swapped a column so update treeview

    def get_source(self, col_being_moved):
        """ Set self.canvas_xxx instances """
        # Strip treeview '#' from '#?' column number
        self.canvas_index = int(col_being_moved.replace('#', '')) - 1
        self.canvas_name = self.canvas_names[self.canvas_index]
        self.canvas_object = self.canvas_objects[self.canvas_index]
        self.canvas_original_x = self.canvas_x_offsets[self.canvas_index]
        self.canvas.tag_raise(self.canvas_object)  # Top stacking order

    def get_target(self, target_index):
        target_start_x = self.canvas_x_offsets[target_index]
        target_middle_x = target_start_x + \
            self.canvas_widths[target_index] // 2
        if target_index == len(self.canvas_x_offsets) - 1:
            # This is the last column on right so use canvas width
            target_end_x = self.canvas.winfo_width()
        else:
            # This is the last column on right so use canvas width
            target_end_x = self.canvas_x_offsets[target_index + 1]

        return target_start_x, target_middle_x, target_end_x

    @staticmethod
    def swap(lst, x1, x2):
        lst[x1], lst[x2] = lst[x2], lst[x1]  # Swap two elements in list

    def source_to_target(self, target_index, new_target_x, new_source_x):
        """ Swap source and target columns """
        self.swap(self.canvas_names, self.canvas_index, target_index)
        self.swap(self.canvas_objects, self.canvas_index, target_index)
        self.swap(self.canvas_widths, self.canvas_index, target_index)
        self.canvas_x_offsets[self.canvas_index] = new_target_x
        self.canvas_x_offsets[target_index] = new_source_x

        # Swap the two images on canvas
        self.canvas.coords(self.canvas_objects[self.canvas_index],
                           (self.canvas_x_offsets[self.canvas_index], 0))
        self.canvas.coords(self.canvas_objects[target_index],
                           (self.canvas_x_offsets[target_index], 0))

        # Now that columns swapped on canvas, get new variables
        self.col_being_moved = "#" + str(target_index + 1)
        self.get_source(self.col_being_moved)

    def create_move_column(self):
        """
            Create canvas toplevel covering up treeview.
            Canvas divided into rectangles for each column.
            Track <B1-Motion> horizontally to swap with next column.
        """

        if self.col_cover_top is not None:
            print('trying to create self.col_cover_top again!!!')
            return

        self.toplevel.update()              # Refresh current coordinates
        self.col_top_is_active = True

        # create named tuple class with names x, y, w, h
        Geom = namedtuple('Geom', ['x', 'y', 'w', 'h'])

        # noinspection PyArgumentList
        top_geom = Geom(self.toplevel.winfo_x(),
                        self.toplevel.winfo_y(),
                        self.toplevel.winfo_width(),
                        self.toplevel.winfo_height())

        #print('\n tkinter top_geom:', top_geom)

        ''' Take screenshot of treeview region (x, y, w, h)
        '''
        # X11 takes 4.5 seconds first time and .67 seconds subsequent times
        #top_image = x11.screenshot(top_geom.x, top_geom.y,
        #                           top_geom.w, top_geom.h)

        # gnome screenshot entire desktop takes .25 seconds
        top_image = gnome_screenshot(top_geom)

        # Did button get released while we were capturing screen?
        if self.col_top_is_active is False:
            return

        # Mount our column moving window over original treeview
        self.col_cover_top = tk.Toplevel()
        self.col_cover_top.overrideredirect(True)   # No window decorations
        self.col_cover_top.withdraw()
        # No title when undecorated (override direct = true)
        #self.col_cover_top.title("Shift column - bserve")
        self.col_cover_top.grid_columnconfigure(0, weight=1)
        self.col_cover_top.grid_rowconfigure(0, weight=1)

        can_frame = tk.Frame(self.col_cover_top, bg="grey",
                             width=top_geom.w, height=top_geom.h)
        can_frame.grid(column=0, row=0, sticky=tk.NSEW)
        can_frame.grid_columnconfigure(0, weight=1)
        can_frame.grid_rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(can_frame, width=top_geom.w,
                                height=top_geom.h, bg="grey")
        self.canvas.grid(row=0, column=0, sticky='nsew')

        total_width = 0
        self.images = []                    # Reset GIC protected image list
        self.canvas_names = []              # treeview column ids (names)
        self.canvas_widths = []             # matching widths
        self.canvas_objects = []            # List of canvas objects
        self.canvas_x_offsets = []          # matching x-offsets within canvas

        for i, column in enumerate(self.treeview['displaycolumns']):

            col_width = self.treeview.column(column)['width']
            # Create cropped image for column out of screenshot using 1 px
            # border width.  Extra crop from bottom to exclude buttons.
            image = top_image.crop([total_width + 1, 1,
                                    total_width + col_width - 2,
                                    top_geom.h - 63])

            # Make a black background image at original column size
            new_im = Image.new("RGB", (col_width, top_geom.h))

            # Paste cropped column image inside black image making a border
            new_im.paste(image, (2, 2))
            photo = ImageTk.PhotoImage(new_im)
            self.images.append(photo)       # Prevent GIC (garbage collection)
            item = self.canvas.create_image(total_width, 0,
                                            image=photo, anchor=tk.NW)
            self.canvas_names.append(column)
            self.canvas_objects.append(item)
            self.canvas_widths.append(col_width)
            self.canvas_x_offsets.append(total_width)
            total_width += col_width

            # Did button get released while we were formatting canvas?
            if self.col_top_is_active is False:
                return

        # Move the column cover window with canvas over original treeview
        self.col_cover_top.geometry('{}x{}+{}+{}'.format(
            top_geom.w, top_geom.h, top_geom.x, top_geom.y))
        self.col_cover_top.deiconify()  # Forces window to appear
        self.col_cover_top.update()  # This is required for visibility


def move_mouse_to(x, y):
    """ Moves the mouse to an absolute location on the screen.
        Rather slow at .1 second and causes brief screen flicker.
        From: https://stackoverflow.com/a/66808226/6929343
        Visit link for other options under Windows and Mac.
        For Linux use xdotool for .007 response time and no flicker.
    """
    # Create a new temporary root
    temp_root = tk.Tk()
    # Move it to +0+0 and remove the title bar
    temp_root.overrideredirect(True)
    # Make sure the window appears on the screen and handles the `overrideredirect`
    temp_root.update()
    # Generate the event as @a bar nert did
    temp_root.event_generate("<Motion>", warp=True, x=x, y=y)
    # Make sure that tcl handles the event
    temp_root.update()
    # Destroy the root
    temp_root.destroy()


def gnome_screenshot(geom):
    """ Screenshot using old gnome 3.18 standards """

    import gi
    gi.require_version('Gdk', '3.0')
    gi.require_version('Gtk', '3.0')
    gi.require_version('Wnck', '3.0')
    # gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "Wnck": "3.0"})  # Python 3

    from gi.repository import Gdk, GdkPixbuf, Gtk, Wnck

    Gdk.threads_init()  # From: https://stackoverflow.com/questions/15728170/
    while Gtk.events_pending():
        Gtk.main_iteration()

    screen = Wnck.Screen.get_default()
    screen.force_update()
    w = Gdk.get_default_root_window()
    pb = Gdk.pixbuf_get_from_window(w, *geom)
    desk_pixels = pb.read_pixel_bytes().get_data()
    raw_img = Image.frombytes('RGB', (geom.w, geom.h), desk_pixels,
                              'raw', 'RGB', pb.get_rowstride(), 1)
    return raw_img


# ==============================================================================
#
#   toolkit.py - ToolTipsPool, CreateToolTip
#
#   Aug 16/2021 - Copied from message.py which will be remain intact for
#                 tool tips that do not fade in/out. Only it will be reverted
#                 to former state.
#
# ==============================================================================

tt_DEBUG = False        # Print debug events

VISIBLE_DELAY = 750     # ms pause until balloon tip appears (1/2 sec)
VISIBLE_SPAN = 5000     # ms balloon tip remains on screen (3 sec/line)
EXTRA_LINE_SPAN = 3000  # More than 1 line is 3 seconds/line
FADE_IN_SPAN = 500      # 1/4 second to fade in
FADE_OUT_SPAN = 400     # 1/5 second to fade out

''' NOTE: Because a new tip fades in after 3/4 second we have time to
          make old tool tip fade out assuming VISIBLE_DELAY > FADE_TIME '''
if VISIBLE_DELAY < FADE_OUT_SPAN:
    print('VISIBLE_DELAY < FADE_OUT_SPAN')
    exit()


class CommonTip:
    """ Variables common to ToolTips__init__() and add_tip()
        Must appear before first reference (ShowInfo)
    """
    def __init__(self):

        self.dict = {}                  # add_tip() dictionary

        self.widget = None              # "999.999.999" = top.frame.button  1
        self.current_state = None       # enter, press, release or leave    2
        self.current_mouse_xy = 0       # Mouse position within widget      3
        self.window_mouse_xy = 0        # Position when tip window created  4
        self.enter_time = 0.0           # time button was entered           5
        self.leave_time = 0.0           # time button was left              6
        self.motion_time = 0.0          # time button was released          7
        self.press_time = 0.0           # time button was pressed           8
        self.release_time = 0.0         # time button was released          9
        self.visible_delay = 0          # milliseconds before visible       10
        self.visible_span = 0           # milliseconds to keep visible      11
        self.extra_line_span = 0        # milliseconds for extra lines      12
        self.fade_in_span = 0           # milliseconds for fading in        13
        self.fade_out_span = 0          # milliseconds for fading out       14

        # Too much window_ ??
        #  'tip_window' used to be 'window_object'
        #  'text' used to be 'window_text'
        #  'window_fading_in' could be 'fading_in'
        #  'window_fading_out' could be 'fading_out'
        self.tip_window = None          # The tooltip window we created     15
        self.text = None                # Text can be changed by caller     16
        Geometry = namedtuple('Geometry', 'x, y, width, height')
        # noinspection PyArgumentList
        self.window_geom = Geometry(0, 0, 0, 0)                           # 17
        self.window_visible = False     # False when alpha = 0.0          # 18
        # Window is never alpha 0 anymore...
        self.current_alpha = 0.0        # current window alpha            # 19
        self.window_fading_in = False                                     # 20
        self.window_fading_out = False                                    # 21

        self.tool_type = None           # "button", "label", etc.         # 22
        self.name = None                # Widget name for debugging       # 23
        self.fg = None                  # Foreground color (buttons)      # 24
        self.bg = None                  # Background color (buttons)      # 25
        self.normal_text_color = None   # self.widget.itemcget(...)       # 26
        self.normal_button_color = None  # .itemcget("button_color"...)   # 27



class ToolTips(CommonTip):
    """ Manage fading in and fading out of tooltips (balloons).
        Canvas button (rounded rectangles) highlighting upon button focus.
        Tooltips can be buttons, canvas buttons or labels.
        Tooltips are internally tracked by their widget object:
            Toplevel.Frame.Widget.Window
                Where .Window is created here.

        USAGE:

        From Master Toplevel initialize:

            self.tt = ToolTips()

        During screen creation Add tooltip (defaults to type='button'):

            self.tt.add_tip(widget_name, type='canvas_button',
                            text="This button\nDoes that.")

        In future:

            self.tt_remove_tips(widget_toplevel)

        Parent must poll the tooltips every 33 ms or so with:

            self.tt.poll_tips()

        When polling is impractical, fade in and fade out are disabled by:

            VISIBLE_DELAY = 0
            VISIBLE_SPAN = 0
            FADE_TIME = 0
            FADE_STEPS = 0

        TODO: When long pressing button (previous/next song testing) sometimes
              it is ignored while tooltip is fading in. Button press and release
              events are not being tracked in our poll_tips() function. Press
              and hold button then after tooltip fully fades in a pseudo button
              release event occurs and active state returns to normal.
              The error message is usually displayed: "ToolTipsPool.showtip():
              Previous tooltip should not be waiting to be visible".

    """

    def __init__(self):

        """ Duplicate entry_init() """
        CommonTip.__init__(self)        # Recycled class to set self. instances

        self.log_nt = None              # namedtuple time, action, widget, x, y
        self.log_list = []              # list of log dictionaries
        self.deleted_str = "0.0.0"      # flag log entry as deleted
        self.now = time.time()          # Current time

        self.dict = {}                  # Tip dictionary
        self.tips_list = []             # List of Tip dictionaries
        self.tips_index = 0             # Current working Tip dictionary in list


    def dict_to_fields(self):
        """ Cryptic dictionary fields to easy names """
        self.widget = self.dict['widget']                           # 01
        self.current_state = self.dict['current_state']             # 02
        self.current_mouse_xy = self.dict[' current_mouse_xy']      # 03
        self.window_mouse_xy = self.dict[' window_mouse_xy']        # 04
        self.enter_time = self.dict['enter_time']                   # 05
        self.leave_time = self.dict['leave_time']                   # 06
        self.motion_time = self.dict['motion_time']                 # 07
        self.press_time = self.dict['press_time']                   # 08
        self.release_time = self.dict['release_time']               # 09
        self.visible_delay = self.dict['visible_delay']             # 10
        self.visible_span = self.dict['visible_span']               # 11
        self.extra_line_span = self.dict['extra_line_span']         # 12
        self.fade_in_span = self.dict['fade_in_span']               # 13
        self.fade_out_span = self.dict['fade_out_span']             # 14
        self.tip_window = self.dict['tip_window']                   # 15
        self.text = self.dict['text']                               # 16
        self.window_geom = self.dict['window_geom']                 # 17
        self.window_visible = self.dict['window_visible']           # 18
        self.current_alpha = self.dict['current_alpha']             # 19
        self.window_fading_in = self.dict['window_fading_in']       # 20
        self.window_fading_out = self.dict['window_fading_out']     # 21
        self.tool_type = self.dict['tool_type']                     # 22
        self.name = self.dict['name']                               # 23
        self.fg = self.dict['fg']                                   # 24
        self.bg = self.dict['bg']                                   # 25
        self.normal_text_color = self.dict['normal_text_color']     # 26
        self.normal_button_color = self.dict['normal_button_color']  # 27


    def fields_to_dict(self):
        """ Easy names to cryptic dictionary fields """
        self.dict['widget'] = self.widget                           # 01
        self.dict['current_state'] = self.current_state             # 02
        self.dict[' current_mouse_xy'] = self.current_mouse_xy      # 03
        self.dict[' window_mouse_xy'] = self.window_mouse_xy        # 04
        self.dict['enter_time'] = self.enter_time                   # 05
        self.dict['leave_time'] = self.leave_time                   # 06
        self.dict['motion_time'] = self.motion_time                 # 07
        self.dict['press_time'] = self.press_time                   # 08
        self.dict['release_time'] = self.release_time               # 09
        self.dict['visible_delay'] = self.visible_delay             # 10
        self.dict['visible_span'] = self.visible_span               # 11
        self.dict['extra_line_span'] = self.extra_line_span         # 12
        self.dict['fade_in_span'] = self.fade_in_span               # 13
        self.dict['fade_out_span'] = self.fade_out_span             # 14
        self.dict['tip_window'] = self.tip_window                   # 15
        self.dict['text'] = self.text                               # 16
        self.dict['window_geom'] = self.window_geom                 # 17
        self.dict['window_visible'] = self.window_visible           # 18
        self.dict['current_alpha'] = self.current_alpha             # 19
        self.dict['window_fading_in'] = self.window_fading_in       # 20
        self.dict['window_fading_out'] = self.window_fading_out     # 21
        self.dict['tool_type'] = self.tool_type                     # 22
        self.dict['name'] = self.name                               # 23
        self.dict['fg'] = self.fg                                   # 24
        self.dict['bg'] = self.bg                                   # 25
        self.dict['normal_text_color'] = self.normal_text_color     # 26
        self.dict['normal_button_color'] = self.normal_button_color  # 27


    def log_event(self, action, widget, x, y):
        """ action is 'enter', 'leave', 'press' or 'release'.
            If release coordinates outside of bounding box, it doesn't count.
            Just log events to array. Do not process them at this point.
            Called from bind

            Events are logged instantly, however processed every 33 ms
            There is no perceptible lag as 30 fps is faster than human eye.
        """
        Event = namedtuple('Event', 'time, action, widget, x, y')
        # noinspection PyArgumentList
        self.log_nt = Event(time.time(), action, widget, x, y)
        self.log_list.append(self.log_nt)
        # print('EVENT:', self.log_nt)

    def process_log_list(self):
        """ Process log list backwards deleting earlier matching widget events """
        # https://stackoverflow.com/a/529427/6929343

        for i, self.log_nt in reversed(list(enumerate(self.log_list))):
            # print('log_dict in log_list', self.log_nt)
            if self.log_nt.widget == self.deleted_str:
                continue                        # We deleted this one, grab next
            # Delete matching widget events prior to this event (i) which is kept
            # self.delete_older_for_widget(i)
            self.set_tip_plan()

        self.log_list = []      # Flush out log list for new events

    def delete_older_for_widget(self, stop_index):
        """ Process log list forwards from 0 deleting matching widget
            Requires specialized testing using manual calls to 
            log_event(action, widget, x, y) followed by process_log_list()

            Intention is to delete <enter> event if there is a <leave> event
            in the queue. Problem is the <leave> event is getting deleted
            instead. Disable for now...

        """
        # Find event log's widget in list of tooltips
        search_widget = self.widget_map(self.log_nt.widget)

        for i, nt in enumerate(self.log_list):
            if i >= stop_index:
                return  # Don't want to delete the last one
            if nt.widget == search_widget:
                # Widget matches so flag as deleted
                print('deleting:', self.log_nt)
                # TODO: What if entering canvas is deleted and colors not changed?
                Event = namedtuple('Event', 'time, action, widget, x, y')
                # noinspection PyArgumentList
                self.log_list[i] = Event(self.log_nt.time, self.log_nt.action,
                                         self.deleted_str,
                                         self.log_nt.x, self.log_nt.y)

    def set_tip_plan(self):
        """ Called to process  event from self.log_nt """
        # Find event log's widget in list of tooltips
        search_widget = self.widget_map(self.log_nt.widget)
        # print('self.log_nt:', self.log_nt)
        for self.tips_index, self.dict in enumerate(self.tips_list):
            if self.dict['widget'] == search_widget:
                break

        if len(self.dict) <= 1:
            print('self.log_nt widget NOT FOUND!:', search_widget)
            for self.dict in self.tips_list:
                for key in self.dict:
                    print("key: %s , value: %s" % (key, self.dict[key]))
                return

        if self.dict['widget'] != search_widget:
            # TODO: This will spam at 30 fps
            print('self.log_nt NOT FOUND!:', self.log_nt)
            return
        
        self.dict_to_fields()               # Dictionary to easy names
        self.current_mouse_xy = (self.log_nt.x, self.log_nt.y)

        ''' OVERVIEW:
            Enter, wait, create, fade in, wait, fade out, destroy.  
            self.window_fading_in and self.window_fading_out already 
            setup so just need self.wait_time.
        '''
        if self.log_nt.action == 'leave':
            # Leaving widget
            self.leave_time = self.log_nt.time
            prt_time = datetime.utcnow().strftime("%M:%S.%f")[:-2]
            d_print(prt_time, 'leaving widget: ', str(self.widget)[-4:])

            if self.window_fading_out:
                # If already fading out, continue the process
                pass  # Can't return now, need to drop down for save

            elif self.window_fading_in:
                # We were in the middle of fading in, so force fade out from
                # same alpha level
                # WIP: Currently fades from 1.0 to 0.1
                self.force_fade_out()

            elif self.window_visible:
                # Return widget colors to 'normal' state if needed.
                self.reset_widget_colors()
                # Begin fade process now
                self.force_fade_out()

            else:
                # Window isn't visible now, so force it to never mount
                self.enter_time = 0.0

        elif self.log_nt.action == 'enter':
            # Entering widget
            prt_time = datetime.utcnow().strftime("%M:%S.%f")[:-2]
            d_print(prt_time, 'entering widget:', str(self.widget)[-4:])
            self.enter_time = self.log_nt.time
            if self.window_visible is True:
                # At this point window visible, so start fade out early.
                print('ERROR: Should not be visible already. If persistent, then')
                print("activate 'tt_DEBUG = True' and check for two 'ENTER:' in a row.")

            if self.tool_type is 'canvas_button' and self.widget.state is 'normal':
                self.set_widget_colors()

        elif self.log_nt.action == 'motion':
            # Mouse motion in widget
            self.motion_time = self.log_nt.time
            if self.window_visible:
                self.move_window()

        elif self.log_nt.action == 'press':
            # Button press in widget
            self.press_time = self.log_nt.time

        elif self.log_nt.action == 'release':
            # Button release after press in widget
            self.release_time = self.log_nt.time

        else:
            print('ERROR: process_tip: Invalid action:', self.log_nt.action)

        self.fields_to_dict()
        self.tips_list[self.tips_index] = self.dict

    def force_fade_out(self):
        """ Override enter time to begin fading out now
        """
        _fade_in, _fade_out = self.calc_fade_in_out()
        diff = _fade_out - self.enter_time
        self.enter_time = self.now - diff
        # print('diff:', diff)

    def move_window(self):
        """ Move window as mouse moves"""

        # s = start, g = geometry, m = mouse, x = x-axis, y = y-axis
        sgx, sgy = self.window_geom.split('+')[1:3]
        smx, smy = self.window_mouse_xy[0:2]
        cmx, cmy = self.current_mouse_xy[0:2]
        smx_diff = int(cmx) - int(smx)  # How has mouse changed since start?
        smy_diff = int(cmy) - int(smy)
        # New geometry = start geometry + mouse change since start
        x = int(sgx) + smx_diff
        y = int(sgy) + smy_diff
        self.tip_window.wm_geometry("+%d+%d" % (x, y))

    def widget_map(self, event_widget):
        """ Some widget such as menus have unusual naming. For example:

            Widget:  .140408240130024.140408237557160.140408237557952

            becomes: .140408240130024.#140408240130024#140408237557160.
                      #140408240130024#140408237557160#140408237557952
        """
        if '#' not in str(event_widget):
            return event_widget  # Normal widget formatting

        new_widget = str(event_widget).split('.')[-1]
        new_widget = new_widget.replace('#', '.')
        for self.dict in self.tips_list:
            if str(self.dict['widget']) == new_widget:
                d_print('event widget substituted. tool_type:', self.dict['tool_type'])
                return self.dict['widget']

        # Widget wasn't found
        print('widget_map(): widget not found:\n', event_widget)

    def calc_fade_in_out(self):
        fade_in_time = self.enter_time + float(self.visible_delay) / 1000
        extra_time = self.visible_span + \
            self.extra_line_span * self.text.count('\n')
        fade_out_time = fade_in_time + float(extra_time) / 1000
        return fade_in_time, fade_out_time

    def add_tip(self, widget, text='Pass text here', tool_type='button',
                visible_delay=VISIBLE_DELAY, visible_span=VISIBLE_SPAN,
                extra_line_span=EXTRA_LINE_SPAN, fade_in_span=FADE_IN_SPAN,
                fade_out_span=FADE_OUT_SPAN):

        CommonTip.__init__(self)            # Initialize all tip instances

        self.widget = widget                # "999.999.999"
        self.text = text                    # "This button \n does that."
        self.tool_type = tool_type

        self.visible_delay = visible_delay
        self.visible_span = visible_span
        self.extra_line_span = extra_line_span
        self.fade_in_span = fade_in_span
        self.fade_out_span = fade_out_span

        try:
            self.name = self.widget['text']         # For display during debugging
        except tk.TclError:
            self.name = "Unknown"

        # All widget bound to same four functions
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        self.widget.bind('<Motion>', self.motion)
        if tool_type is 'button':
            self.widget.bind("<ButtonPress-1>", self.on_press)
            self.widget.bind("<ButtonRelease-1>", self.on_release)

        # Add tip dictionary to tips list
        self.fields_to_dict()
        self.tips_list.append(self.dict)

    def reset_tip(self):
        """ After cycle is finished reset selected widget values """
        self.enter_time = self.leave_time = self.press_time = \
            self.release_time = self.current_alpha = 0.0
        self.tip_window = self.window_geom = None
        self.window_visible = self.window_fading_in = \
            self.window_fading_out = False

    def set_widget_colors(self):
        """ Set the colors for canvas object focus """

        # For canvas buttons do heavy lifting of reflecting button active state
        self.widget.state = 'active'
        self.normal_text_color = self.widget.itemcget("text_color", "fill")
        self.normal_button_color = self.widget.itemcget("button_color", "fill")

        # We know the button is always black #000000 or white #ffffff
        if self.normal_button_color == "#000000":
            # Button color is black so lighten all 25%
            new_text_color_hex = img.rgb_to_hex(img.lighten_rgb(
                img.hex_to_rgb(self.normal_text_color)))
            new_button_color_hex = img.rgb_to_hex(img.lighten_rgb(
                img.hex_to_rgb(self.normal_button_color)))
        else:
            # Button color is white so darken all 25$
            new_text_color_hex = img.rgb_to_hex(img.darken_rgb(
                img.hex_to_rgb(self.normal_text_color)))
            new_button_color_hex = img.rgb_to_hex(img.darken_rgb(
                img.hex_to_rgb(self.normal_button_color)))

        self.widget.itemconfig("button_color", fill=new_button_color_hex,
                               outline=new_button_color_hex)
        self.widget.itemconfig("text_color", fill=new_text_color_hex)

    def reset_widget_colors(self):
        """ Reset colors for canvas object losing focus """
        if self.tool_type is 'button':
            if self.widget['state'] != tk.NORMAL:
                #print('CreateToolTip.leave(): reset button state to tk.NORMAL')
                self.widget['state'] = tk.NORMAL

        if self.tool_type is 'canvas_button' and self.widget.state is 'active':
            #print('CreateToolTip.leave(): reset canvas button state to normal')
            self.widget.state = 'normal'
            self.widget.itemconfig("button_color", fill=self.normal_button_color,
                                   outline=self.normal_button_color)
            self.widget.itemconfig("text_color", fill=self.normal_text_color)

    def poll_tips(self):
        """ Check for fading in new tooltip and/or fading out current tooltip """
        self.now = time.time()          # Current time

        # Read event log list backwards to avoid unnecessary steps, eg leave after enter
        # means we don't have to do enter step. Empty log list when done.
        self.process_log_list()         # Incomplete...

        for self.tips_index, self.dict in enumerate(self.tips_list):
            self.dict_to_fields()
            self.process_tip()
            self.fields_to_dict()
            self.tips_list[self.tips_index] = self.dict

    def process_tip(self):
        """ Check if window should be created or destroyed.
            Check if we are fading in or fading out and set alpha.
        """

        # Was window destroyed? eg by toplevel closing.
        if self.tip_window:
            if not self.tip_window.winfo_exists():
                self.tip_window = None
                self.window_visible = False
                self.window_fading_in = False
                self.window_fading_out = False
                print("ERROR: process_tip(): tip.window doesn't exist")
                return

        ''' Pending event to start displaying tooltip balloon?
        '''
        if self.enter_time == 0.0:
            if self.tip_window:
                self.tip_window.destroy()
                print('TEMPORARY: forced tip window close')
                self.tip_window = None
                self.window_visible = False
                self.window_fading_in = False
                self.window_fading_out = False
            return  # Widget doesn't have focus

        fade_in_time, fade_out_time = self.calc_fade_in_out()

        # Are we fading out?
        if self.now > fade_out_time:
            if self.window_fading_out is False:
                self.window_fading_out = True
                self.window_fading_in = False

            # What time will we hit zero alpha? (fully faded out)
            zero_alpha_time = fade_out_time + float(self.fade_out_span) / 1000
            if self.now > zero_alpha_time:
                # We've finished fading out
                if self.tip_window is None:
                    print('process_tip(): self.tip_window does not exist')
                    print('self.now:', self.now, 'zero_alpha_time:', zero_alpha_time)
                    diff = self.now - zero_alpha_time
                    print('diff:', diff)
                else:
                    self.tip_window.destroy()

                self.reset_tip()
                return

            # Calculate fade out alpha 1.00 to 0.01
            delta = (zero_alpha_time - self.now) * 1000
            alpha = delta / self.fade_out_span
            self.update_alpha(alpha)
            return

        # Are we fading in?
        if self.now > fade_in_time:

            # If we've already left the button, forego the creation
            #if self.leave_time > self.enter_time:
            #    self.enter_time = 0.0  # Prevent tip window creation
            #    #print('prevent tip window creation when leave > enter')
            #    return

            # for those quirky timing situations
            diff = abs(self.leave_time - self.enter_time)
            if diff < 0.1:
                # To Correct:
                # 45:13.059 ENTER: 8216 59 6
                # 45:13.061 LEAVE: 8216 59 52
                # 45:13.1039 leaving widget:  8216
                # 45:13.1041 entering widget: 8216
                self.enter_time = 0.0  # Prevent tip window creation
                #print('prevent tip window creation when enter ~.1 of leave')
                return

            if self.window_visible is False:
                self.create_tip_window()
                self.window_visible = True
                self.window_fading_in = True

            full_alpha_time = fade_in_time + float(self.fade_in_span) / 1000
            if self.now > full_alpha_time:
                # We've finished fading in
                self.window_fading_in = False
                if self.current_alpha != 1.0:
                    self.update_alpha(1.0)
                return

            # Calculate fade in alpha 0.01 to 1.00
            delta = (full_alpha_time - self.now) * 1000
            alpha = 1.0 - (delta / self.fade_in_span)
            self.update_alpha(alpha)
            return

        # At this point we are simply waiting to fade in or fade out

    def update_alpha(self, alpha):
        if alpha != self.current_alpha:
            self.tip_window.attributes("-alpha", alpha)
            self.current_alpha = alpha

    def create_tip_window(self):

        # Screen coordinates for tooltip balloon (window)
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        if self.tool_type == 'menu':
            # For menu bars the x & y is way off to 0,0
            # https://stackoverflow.com/a/47855128/6929343
            parent = self.widget.master.master
            x = parent.winfo_rootx() + self.widget.winfo_width()
            y = parent.winfo_rooty() + self.widget.winfo_height()
            x = x + self.current_mouse_xy[0]
            y = y + self.current_mouse_xy[1] + 30

        # Track mouse movements to change window geometry
        self.window_mouse_xy = self.current_mouse_xy

        # Invert tooltip colors from current widget album art colors.
        #if self.tool_type is 'button' or self.tool_type is 'menu':
        if self.tool_type is not 'canvas_button':
            self.fg = self.widget["background"]
            self.bg = self.widget["foreground"]
        else:
            self.fg = None
            self.bg = None

        self.tip_window = tw = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(1)   # Undecorated
        self.tip_window.wm_geometry("+%d+%d" % (x, y))

        # https://www.tcl.tk/man/tcl8.6/TkCmd/wm.htm#M9
        # self.tip_window['background'] = self.bg
        self.tip_window['background'] = self.bg
        # https://stackoverflow.com/a/52123172/6929343
        self.tip_window.wm_attributes('-type', 'tooltip')  # only works X11 and not all distros

        #print('created self.tip_window:', self.tip_window)
        #print('w.wm_geometry("+%d+%d" % (x, y)):', "+%d+%d" % (x, y))

        ''' Throws py charm error: access to protected 'tw._w'
        try:
            # For Mac OS
            tw.tk.call("::tk::unsupported::MacWindowStyle",
                       "style", tw._w,
                       "help", "noActivates")
        except tk.TclError:
            pass
        '''
        #        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background=self.bg, foreground=self.fg, relief=tk.SOLID,
                         borderwidth=2, pady=10, padx=10, font=(None, g.MON_FONTSIZE))
        label.pack(ipadx=2)

        self.tip_window.attributes("-alpha", 0)  # Start at 1%
        self.tip_window.update_idletasks()
        self.window_geom = self.tip_window.wm_geometry()
        d_print('tip_window created at:', "+%d+%d" % (x, y), 'for:', self.widget)

    def set_text(self, widget, text, visible_delay=VISIBLE_DELAY,
                 visible_span=VISIBLE_SPAN, extra_line_span=EXTRA_LINE_SPAN,
                 fade_in_span=FADE_IN_SPAN, fade_out_span=FADE_OUT_SPAN):

        """ Text can be changed at any time externally """
        for self.tips_index, self.dict in enumerate(self.tips_list):
            if self.dict['widget'] == widget:
                self.dict['text'] = text
                self.dict['visible_delay'] = visible_delay
                self.dict['visible_span'] = visible_span
                self.dict['extra_line_span'] = extra_line_span
                self.dict['fade_in_span'] = fade_in_span
                self.dict['fade_out_span'] = fade_out_span
                self.tips_list[self.tips_index] = self.dict
                # TODO: When text expands/shrinks line count
                #       we need to
                return
            
        print('ERROR: set_text(): tip not found')

    def enter(self, _event):
        """
        """
        d_print('ENTER:', str(_event.widget)[-4:], _event.x, _event.y)
        self.log_event('enter', _event.widget, _event.x, _event.y)

    def leave(self, _event):
        """
        Enter has 500 ms delay so leave may come before tooltip displayed.

        TEST: When leaving early button remains "active" so force to "normal".
        """
        d_print('LEAVE:', str(_event.widget)[-4:], _event.x, _event.y)
        self.log_event('leave', _event.widget, _event.x, _event.y)

    # noinspection PyMethodMayBeStatic
    def motion(self, _event):
        """ Mouse is panning over widget.
            Consider moving tooltip window along x-axis
            This generates a lot of noise when printing debug information...
        """
        #d_print('MOVES:', str(_event.widget)[-4:], _event.x, _event.y)
        self.log_event('motion', _event.widget, _event.x, _event.y)
        return

    def on_press(self, _event):
        """ Widget type is button and it was just pressed """
        d_print('PRESS:', str(_event.widget)[-4:], _event.x, _event.y)
        self.log_event('press', _event.widget, _event.x, _event.y)

    def on_release(self, _event):
        """ Widget type is button and mouse click was just released.
            A leave event is automatically generated but we may no longer
            be in the same widget.
        """
        d_print('REL_S:', str(_event.widget)[-4:], _event.x, _event.y)
        self.log_event('release', _event.widget, _event.x, _event.y)

    def close(self, widget):
        """ When window closes all tooltips in it must be removed.
            :param widget either button or parent(s) of button.
        """
        new_list = []
        for self.dict in self.tips_list:
            if not str(self.dict['widget']).startswith(str(widget)):
                new_list.append(self.dict)
                
        diff = len(self.tips_list) - len(new_list)
        print(diff, 'Tooltips removed on close')
        self.tips_list = []
        self.tips_list = new_list


def d_print(*args):
    """ Only print debugging lines when tt_DEBUG is true """
    if tt_DEBUG is True:
        prt_time = datetime.utcnow().strftime("%M:%S.%f")[:-3]
        print(prt_time, *args)


# End of: toolkit.py
