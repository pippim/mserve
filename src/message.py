# -*- coding: utf-8 -*-
#==============================================================================
#
#       message.py - status messages, dialogs, tooltips
#
#==============================================================================

# identical imports in mserve
from __future__ import print_function       # Must be first import
from __future__ import with_statement       # Error handling for file opens

import pprint

try:
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as font
    import tkinter.filedialog as filedialog
    # import tkinter.messagebox as messagebox
    import tkinter.simpledialog as simpledialog
    PYTHON_VER = "3"
except ImportError:
    import Tkinter as tk
    import ttk
    import tkFont as font
    import tkFileDialog as filedialog
    # import tkMessageBox as messagebox
    import tkSimpleDialog as simpledialog
    PYTHON_VER = "2"
# print ("Python version: ", PYTHON_VER)

import subprocess32 as sp
import re
import time
from datetime import datetime

# mserve modules
import image as img
import external as ext              # For timings
import timefmt as tmf               # Format hh:mm:ss.hh
import toolkit

# Values from gnome-terminal to prevent window shrinking too small
WIN_MIN_WIDTH = 142
WIN_MIN_HEIGHT = 63

MED_FONT = 10                       # Medium Font size
MON_FONTSIZE = 11                   # Medium Font size


class Open:
    """ Text Widget with status messages

    TODO: Add vertical scroll bar
          Merge common code with DelayedTextBox
    """

    def __init__(self, title, toplevel, width, height):
        """ Mount message textbox window centered in toplevel or at mouse
        
            USAGE:
            
                tb = message.Open("title", toplevel, width, height)
                while True:
                    tb.update(message_line)
                tb.close()
        """

        self.msg_top, self.textbox = \
            common_code(title, toplevel, width, height)
        self.textbox.pack()                 # pack must be outside common code
        self.line_cnt = 0                   # Message lines displayed so far

    def update(self, msg_line):
        # TODO: Why is ndx always 'None'?
        ndx = self.textbox.insert(tk.END, msg_line + '\n')
        try:
            # self.textbox.see(ndx)  # ndx is always "None"
            self.textbox.see(tk.END)
        finally:
            print('update() passed blank string?:', ndx, msg_line)
        self.msg_top.update()
        self.line_cnt += 1                  # Message lines displayed so far
        # print('MsgDisplay.Update():', msg_list)
        # time.sleep(.1)

    def close(self):
        # self.textbox.insert(tk.END, "CLOSING DOWN NOW")
        # self.msg_top.update()
        # time.sleep(.5)
        self.msg_top.destroy()
        self.msg_top = None


def common_code(title, toplevel, width, height):
    """ Mount message textbox window centered in toplevel or at mouse """
    msg_top = tk.Toplevel()
    msg_top.minsize(WIN_MIN_WIDTH, WIN_MIN_HEIGHT)
    msg_top.title(title)

    ''' If toplevel passed use it's co-ordinates, else use mouse's '''
    if toplevel:
        toplevel.update_idletasks()     # Get up-to-date window co-ords
        # Get Geometry: "%dx%d%+d%+d" % (width, height, x_offset, y_offset)
        gw, gh, gx, gy = re.findall('[0-9]+', toplevel.winfo_geometry())
        x = int(gx) + (int(gw)/2) - (width/2)       # Center for width
        y = int(gy) + (int(gh)/2) - (height/2)      # Center for height
    else:
        x, y = get_mouse_coordinates()

    if x < 0:
        x = 0                     # Can't have negative co-ordinates
    if y < 0:
        y = 0
    msg_top.geometry('%dx%d+%d+%d' % (width, height, x, y))
    text_box = tk.Text(msg_top, height=height, width=width,
                       font=(None, MED_FONT))
    # Note pack is located in caller
    return msg_top, text_box


def get_mouse_coordinates():
    """ Get mouse co-ordinates with xdotool:
            $ xdotool getmouselocation
            x:4490 y:1920 screen:0 window:65011722
    """
    command_line_list = ['xdotool', 'getmouselocation']

    pipe = sp.Popen(command_line_list, stdout=sp.PIPE, stderr=sp.PIPE)
    text, err = pipe.communicate()              # This performs .wait() too

    if pipe.returncode is not 0:
        print('get_mouse_coordinates() ERROR:')
        print(err)
        return 100, 100

    if text:
        x, y, screen, window = [tok.split(":")[1] for tok in text.split(" ")]
        # import re
        # x, y, screen, window = re.findall("[0-9]+", text)
        return int(x), int(y)

    if err:
        print('get_mouse_coordinates() ERROR:')
        print(err)
        return 100, 100


class DelayedTextBox:
    """ Delay opening text box for short running process.
        Don't display every line for long running process.
    """

    def __init__(self, title="Status", toplevel=None, width=600, height=400,
                 startup_delay=2, frame_rate=30):

        self.title = title
        self.toplevel = toplevel
        self.width = width
        self.height = height

        # Current time + startup delay is when we mount our text box
        self.mount_time = time.time() + float(startup_delay)
        self.update_interval = 1.0 / float(frame_rate)
        self.next_update = self.mount_time  # When we will mount textbox
        self.mounted = False                # Is textbox mounted yet?
        self.textbox = None                 # The Text box instance
        self.old_lines = []                 # Lines that were not displayed
        self.line_cnt = 0                   # Message lines encountered so far
        self.display_cnt = 0                # Message lines displayed so far
        self.msg_top = None

    def update(self, msg_line):
        self.line_cnt += 1                  # Message lines encountered so far
        now = time.time()                   # Current time
        if now > self.mount_time:           # Current time > mont time target?
            if not self.mounted:            # Do we need to mount?
                ''' Mount message window centered in toplevel or at mouse'''
                self.msg_top, self.textbox = common_code(
                    self.title, self.toplevel, self.width, self.height)
                self.textbox.pack()         # Make textbox visible now
                self.mounted = True         # Signal that Textbox is mounted
                
                # turn on text box for editing, user can change too for period
                self.textbox.configure(state="normal")
                for old_line in self.old_lines: 
                    # Loop through suppressed lines and display now. Note we
                    # are not honouring frame rate here and may be flooding
                    # the screen
                    self.textbox.insert(tk.END, old_line + '\n')

                # turn pff text box for editing, we and user cannot change text
                self.textbox.configure(state="disabled")
                self.old_lines = []         # Delete old list

        else:
            self.old_lines.append(msg_line)  # Lines suppressed before mount
            return False

        if now > self.next_update:
            # Displaying every line slows down program. Honor frame rate.
            self.textbox.configure(state="normal")
            self.textbox.insert(tk.END, msg_line + '\n')
            self.textbox.configure(state="disabled")
            self.textbox.see(tk.END)
            self.textbox.update()           # Is this necessary? CONFIRMED YES
            self.display_cnt += 1           # Message lines displayed so far
            self.next_update = now + self.update_interval
            return True                     # We updated text box

        # TODO: We are getting 100 messages dropped from gmail api because it is
        #       1 second between batches of 100.
        return False

    def close(self):
        # print('DelayedTextBox lines in:',self.line_cnt,'out:',self.display_cnt)
        if self.mounted:                    # Is textbox mounted yet?
            self.msg_top.destroy()
            self.mounted = False


class FakeEvent:
    """ Create fake event.x_root and event.y_root for popup menu post """
    def __init__(self, parent, offset='right'):

        parent.update()
        gw = parent.winfo_width()
        gh = parent.winfo_height()
        gx = parent.winfo_rootx()
        gy = parent.winfo_rooty()
        if offset is 'right':
            self.x_root = int(gx) + int(gw) - 150   # Awkward
            self.y_root = int(gy) + int(gh) + 15    # Awkward


    # ==============================================================================
    #
    #   message.py - ShowInfo, AskQuestion, AskString
    #
    # ==============================================================================


class CommonSelf:
    """ Variables common to ShowInfo, AskQuestion and AskString
        Must appear before first reference (ShowInfo)
    """
#    def __init__(self, parent, title=None, text=None, confirm='yes',
    def __init__(self, parent, text=None, confirm='yes',
                 align='center', thread=None, icon='warning'):

        self.top_level = parent     # Allows .after() calls
        self.confirm = confirm      # Append "Are you sure?" line?
        self.align = align          # data (text lines) alignment
        if thread is None:
            self.thread = None
        elif callable(thread):
            self.thread = thread    # The thread runs whilst waiting for button click
        else:
            print("message.py, CommonSelf, invalid thread= passed")
            toolkit.print_trace()
            self.thread = None
        self.loop_no = 1            # Loop counter (not used yet)
        self.text = text            # data (text lines) for text box
        self.textbox = None         # Textbox widget
        self.icon = icon            # Warning, Error, Info, Question icons
        self.entry = None           # Tkinter Entry widget
        self.string = ""            # What the user has entered (AskString)
        self.result = None          # Defined in simpledialog already
        # MON_FONTSIZE may not be defined globally
        try:
            self.font = (None, MON_FONTSIZE)
        except NameError:
            self.font = (None, 10)

        # Shared functions
        self.wait_window = wait_window_func


class ShowInfo(simpledialog.Dialog, CommonSelf):
    """ Show information message with "OK" button at end
        Prepends and appends "\n" to text passed.
    """
    def __init__(self, parent=None, title=None, text=None, align='center',
                 thread=None, confirm='no', icon='information'):

        #        CommonSelf.__init__(self, parent, title=title, text=text, confirm=confirm,
        CommonSelf.__init__(self, parent, text=text, confirm=confirm,
                            align=align, thread=thread, icon=icon)
        simpledialog.Dialog.__init__(self, parent, title=title)

    def body(self, parent):
        return body_func(self)

    def buttonbox(self):
        """add standard button box for ShowInformation.

        override with sole "OK" button bound to both Enter and Escape
        """

        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, 
                      default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)

        box.pack()


# data_w_l(), set_icon_image(), wait_window_func(), # body_func()
# shared by classes: ShowInfo, AskQuestion, AskString

def data_w_l(text):
    """ Get widest line and number of lines of text in message box """

    lines = text.split('\n')
    longest = max(lines, key=len)
    width = len(longest)

    return width, len(lines)


def set_icon_image(icon):
    """ Set Icon image or set None """
    # Icon message files: https://stackoverflow.com/questions/37783878/
    # is-it-possible-to-get-tkinter-messagebox-icon-image-files
    # ::tk::icons::warning
    # ::tk::icons::error
    # ::tk::icons::information
    # ::tk::icons::question
    if icon is "warning":
        icon_image = "::tk::icons::warning"
    elif icon is "error":
        icon_image = "::tk::icons::error"
    elif icon is "information":
        icon_image = "::tk::icons::information"
    elif icon is "question":
        icon_image = "::tk::icons::question"
    else:
        icon_image = None
    return icon_image


def textbox(box, text, align, lines):
    """ Populate textbox with message lines """

    box.configure(state="normal")
    box.insert("1.0", text)          # Allows text to be copied to clipboard

    if align is 'center':
        box.tag_configure("center", justify='center')
        box.tag_add("center", "1.0", "end")

    box.configure(height=lines)
    box.configure(state="disabled")


#def wait_window_func(self, *args):
def wait_window_func(self):
    """ Even with no thread passed, this allows other windows to remain
        updating graphic animations at 30 fps
    """
    #print('wait_window() has started. self.thread is:', self.thread)
    #print('Sleeping a second.  self.top_level is:', self.top_level)
    if not self.thread:
        return

    while self.winfo_exists():  # Loop while our window exists
        now = time.time()
        if self.thread:
            self.thread()
        sleep = 33 - (time.time() - now) * 1000
        if sleep < 1:
            sleep = 1
        self.top_level.after(int(sleep))

    #print('wait_window() has ended')


if 'BIG_SPACE' not in locals() and 'BIG_SPACE' not in globals():
    BIG_SPACE = " "  # UTF-8 (2003) aka Em Space


def body_func(self):
    """
    Force our window to stay on top.

    Reformat text defined in self.text (textbox message):
        If confirm = 'yes' add "Are you sure?" line at bottom
        If align = 'left' prepend 'Em' space on lines not beginning with '\t'

    :param self: ShowInf0(), AskQuestion() or AskString() class parent
    :return: Formatted text box as newly created widget called self.textbox
    """

    # Force our window to stay on top
    self.wm_attributes("-topmost", 1)

    # Massage text with extra lines, extra message and left padding
    f_text = "\n" + self.text + "\n"        # Reformatted text
    if self.confirm is 'yes':
        f_text = f_text + "\nAre you sure?\n"

    if self.align == 'left':
        p_text = ""                         # Padded text
        for line in f_text.split('\n'):
            if line.startswith('\t'):
                p_text = p_text + line + '\n'
            else:
                p_text = p_text + BIG_SPACE + line + '\n'
        f_text = p_text

    # Find longest line and use it as text width
    width, lines = data_w_l(f_text)

    # Get message box icon image from Tkinter
    icon_image = set_icon_image(self.icon)
    if icon_image:
        self.icon = tk.Label(self, image=icon_image)
        self.icon.pack(fill="both", padx=5, pady=15)

    self.textbox = tk.Text(self, width=width, font=self.font)
    self.textbox.pack(fill="both", expand=True)
    # self.textbox.pack(side=tk.LEFT, fill="both", expand=True)

    # Populate the textbox with justification and height
    textbox(self.textbox, f_text, self.align, lines)
    return self.textbox


class AskQuestion(simpledialog.Dialog, CommonSelf):
    """ Prepends "\n" to text passed.
        Appends "\n\nAre you sure?\n" to text passed.
        Allows text to be highlighted and copied to clipboard with CTRL+C.
        Blocks other windows from getting focus
        MON_FONTSIZE is temporary font size until configuration file set up.

        BUGS:
        April 24, 2023 - When 'no' click was returning: 139944643864048.139944641065544

    """

    def __init__(self, parent, title=None, text=None, confirm='yes',
                 align='center', thread=None, icon='warning'):

        #        CommonSelf.__init__(self, parent, title=title, text=text, confirm=confirm,
        CommonSelf.__init__(self, parent, text=text, confirm=confirm,
                            align=align, thread=thread, icon=icon)
        simpledialog.Dialog.__init__(self, parent, title=title)
        '''
        When encoding.py was popping up question to manually enter disc id
        cursor was being forced into web browser to copy the new disc id at
        from musicbrainz website at same time causing this error:

Exception in Tkinter callback
Traceback (most recent call last):
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1540, in __call__
    return self.func(*args)
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 590, in callit
    func(*args)
  File "/home/rick/python/encoding.py", line 637, in cd_run_to_close
    if self.error_3():
  File "/home/rick/python/encoding.py", line 732, in error_3
    "Disc ID not found in Musicbrainz", text=text, icon="question")
  File "/home/rick/python/message.py", line 394, in __init__
    simpledialog.Dialog.__init__(self, parent, title=title)
  File "/usr/lib/python2.7/lib-tk/tkSimpleDialog.py", line 85, in __init__
    self.grab_set()
  File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 679, in grab_set
    self.tk.call('grab', 'set', self._w)
TclError: grab failed: another application has grab        
        '''

    def body(self, parent):
        """
        """
        self.textbox = body_func(self)
        return self.textbox

    def buttonbox(self):
        """ add standard button box for AskQuestion
            override to "Yes" and "No" for sense to "Are you sure?" question
        """

        box = tk.Frame(self)

        w = tk.Button(box, text="Yes", width=10, command=self.ok, 
                      default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        w = tk.Button(box, text="No", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics
    def ok(self, event=None):

        # From: /usr/lib/python2.7/lib-tk/tkSimpleDialog.py (returns 1)
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()
        self.result = "yes"

    def cancel(self, event=None):

        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.result = "no"
        self.destroy()


class AskString(simpledialog.Dialog, CommonSelf):
    """ Prepends "\nInput:" to text passed.
        Appends Entry field after "Input:"
        Allows text to be highlighted and copied to clipboard with CTRL+C.
        Blocks other windows from stealing focus
        MON_FONTSIZE is temporary font size until configuration file set up.
    """

    def __init__(self, parent, title=None, text=None, confirm='no',
                 align='center', thread=None, icon='question'):

        #        CommonSelf.__init__(self, parent, title=title, text=text, confirm=confirm,
        CommonSelf.__init__(self, parent, text=text, confirm=confirm,
                            align=align, thread=thread, icon=icon)

        simpledialog.Dialog.__init__(self, parent, title=title)

    def new_body(self):
        """ Remove parent from parameter list Aug 12/2021.
        """
        self.textbox = body_func(self)
        return self.textbox

    def body(self, parent):
        """
        """
        self.text = "\n" + self.text + "\n"
        if self.confirm is 'yes':
            self.text = self.text + "\nAre you sure?\n"

        # Force our window to stay on top
        self.wm_attributes("-topmost", 1)

        # Find longest line and use it as text width
        width, lines = data_w_l(self.text)

        icon_image = set_icon_image(self.icon)
        if icon_image:
            self.icon = tk.Label(self, image=icon_image)
            self.icon.pack(fill="both", padx=5, pady=15)

        self.textbox = tk.Text(self, width=width, font=self.font)
        self.textbox.pack(fill="both", padx=5, expand=True)
        #self.textbox.pack(side=tk.LEFT, fill="both", expand=True)

        # Populate the textbox with justification and height
        textbox(self.textbox, self.text,  self.align, lines)

        # Append our label and entry field.
        tk.Label(self, text="Input or Paste below:",
                 font=self.font).pack(fill="none", padx=5)
        self.entry = tk.Entry(self, font=self.font,
                              bg="#282B2B", fg="white", width=28)
        self.entry.pack(fill="none", padx=5, expand=True)
        self.entry.focus_set()

        return self.textbox

    def buttonbox(self):
        """ add standard button box for AskString

        override to "Apply" and "Cancel"
        """

        box = tk.Frame(self)

        w = tk.Button(box, text="Apply", width=10, command=self.ok,
                      default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()

    #
    # standard button semantics
    def ok(self, event=None):

        # From: /usr/lib/python2.7/lib-tk/tkSimpleDialog.py (returns 1)
        if not self.validate():
            self.initial_focus.focus_set()  # put focus back
            return

        self.withdraw()
        self.update_idletasks()

        try:
            self.apply()
        finally:
            self.cancel()
        self.result = "yes"

    def apply(self, event=None):
        self.string = self.entry.get()
        #print('self.string:', self.string)
        return True

    def cancel(self, event=None):

        # put focus back to the parent window
        if self.parent is not None:
            self.parent.focus_set()
        self.result = "no"
        self.destroy()


# ==============================================================================
#
#   message.py - InputWindow() class
#
# ==============================================================================


class CommonIW:
    """ Variables common to InputWindow__init__() and add_field()
    """

    def __init__(self):
        self.dict = {}  # add_tip() dictionary

        self.widget = None  # "999.999.999" = top.frame.button  1
        self.current_state = None  # enter, press, release or leave    2
        self.current_mouse_xy = 0  # Mouse position within widget      3
        self.window_mouse_xy = 0  # Position when tip window created  4
        self.enter_time = 0.0  # time button was entered           5
        self.leave_time = 0.0  # time button was left              6
        self.motion_time = 0.0  # time button was released          7
        self.press_time = 0.0  # time button was pressed           8
        self.release_time = 0.0  # time button was released          9
        self.visible_delay = 0  # milliseconds before visible       10
        self.visible_span = 0  # milliseconds to keep visible      11
        self.extra_word_span = 0  # milliseconds for extra lines      12
        self.fade_in_span = 0  # milliseconds for fading in        13
        self.fade_out_span = 0  # milliseconds for fading out       14

        # Too much window_ ??
        #  'tip_window' used to be 'window_object'
        #  'text' used to be 'window_text'
        #  'window_fading_in' could be 'fading_in'
        #  'window_fading_out' could be 'fading_out'
        self.tip_window = None  # The tooltip window we created     15
        self.text = None  # Text can be changed by caller     16
        Geometry = namedtuple('Geometry', 'x, y, width, height')
        # noinspection PyArgumentList
        self.window_geom = Geometry(0, 0, 0, 0)  # 17
        self.window_visible = False  # False when alpha = 0.0          # 18
        # Window is never alpha 0 anymore...
        self.current_alpha = 0.0  # current window alpha            # 19
        self.window_fading_in = False  # 20
        self.window_fading_out = False  # 21

        self.tool_type = None  # "button", "label", etc.         # 22
        self.name = None  # Widget name for debugging       # 23
        self.fg = None  # Foreground color (buttons)      # 24
        self.bg = None  # Background color (buttons)      # 25
        self.normal_text_color = None  # self.widget.itemcget(...)       # 26
        self.normal_button_color = None  # .itemcget("button_color"...)   # 27
        self.anchor = None  # tooltip anchor point on widget  # 28


class InputWindow(CommonIW):
    """
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

        When screen is closed:

            self.tt.close(widget_toplevel)

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

              If window doesn't have focus, don't display tips.
              If window loses focus, close balloons.
    """

    def __init__(self):

        """ Duplicate entry_init() """
        CommonIW.__init__(self)  # Recycled class to set self. instances

        self.log_nt = None  # namedtuple time, action, widget, x, y
        self.log_list = []  # list of log dictionaries
        self.deleted_str = "0.0.0"  # flag log entry as deleted (zero time)
        self.now = time.time()  # Current time

        self.dict = {}  # Tip dictionary
        self.tips_list = []  # List of Tip dictionaries
        self.tips_index = 0  # Current working Tip dictionary in list

    def dict_to_fields(self):
        """ Cryptic dictionary fields to easy names """
        self.widget = self.dict['widget']  # 01
        self.current_state = self.dict['current_state']  # 02
        self.current_mouse_xy = self.dict[' current_mouse_xy']  # 03
        self.window_mouse_xy = self.dict[' window_mouse_xy']  # 04
        self.enter_time = self.dict['enter_time']  # 05
        self.leave_time = self.dict['leave_time']  # 06
        self.motion_time = self.dict['motion_time']  # 07
        self.press_time = self.dict['press_time']  # 08
        self.release_time = self.dict['release_time']  # 09
        self.visible_delay = self.dict['visible_delay']  # 10
        self.visible_span = self.dict['visible_span']  # 11
        self.extra_word_span = self.dict['extra_word_span']  # 12
        self.fade_in_span = self.dict['fade_in_span']  # 13
        self.fade_out_span = self.dict['fade_out_span']  # 14
        self.tip_window = self.dict['tip_window']  # 15
        self.text = self.dict['text']  # 16
        self.window_geom = self.dict['window_geom']  # 17
        self.window_visible = self.dict['window_visible']  # 18
        self.current_alpha = self.dict['current_alpha']  # 19
        self.window_fading_in = self.dict['window_fading_in']  # 20
        self.window_fading_out = self.dict['window_fading_out']  # 21
        self.tool_type = self.dict['tool_type']  # 22
        self.name = self.dict['name']  # 23
        self.fg = self.dict['fg']  # 24
        self.bg = self.dict['bg']  # 25
        self.normal_text_color = self.dict['normal_text_color']  # 26
        self.normal_button_color = self.dict['normal_button_color']  # 27
        self.anchor = self.dict['anchor']  # 28

    def fields_to_dict(self):
        """ Easy names to cryptic dictionary fields """
        self.dict['widget'] = self.widget  # 01
        self.dict['current_state'] = self.current_state  # 02
        self.dict[' current_mouse_xy'] = self.current_mouse_xy  # 03
        self.dict[' window_mouse_xy'] = self.window_mouse_xy  # 04
        self.dict['enter_time'] = self.enter_time  # 05
        self.dict['leave_time'] = self.leave_time  # 06
        self.dict['motion_time'] = self.motion_time  # 07
        self.dict['press_time'] = self.press_time  # 08
        self.dict['release_time'] = self.release_time  # 09
        self.dict['visible_delay'] = self.visible_delay  # 10
        self.dict['visible_span'] = self.visible_span  # 11
        self.dict['extra_word_span'] = self.extra_word_span  # 12
        self.dict['fade_in_span'] = self.fade_in_span  # 13
        self.dict['fade_out_span'] = self.fade_out_span  # 14
        self.dict['tip_window'] = self.tip_window  # 15
        self.dict['text'] = self.text  # 16
        self.dict['window_geom'] = self.window_geom  # 17
        self.dict['window_visible'] = self.window_visible  # 18
        self.dict['current_alpha'] = self.current_alpha  # 19
        self.dict['window_fading_in'] = self.window_fading_in  # 20
        self.dict['window_fading_out'] = self.window_fading_out  # 21
        self.dict['tool_type'] = self.tool_type  # 22
        self.dict['name'] = self.name  # 23
        self.dict['fg'] = self.fg  # 24
        self.dict['bg'] = self.bg  # 25
        self.dict['normal_text_color'] = self.normal_text_color  # 26
        self.dict['normal_button_color'] = self.normal_button_color  # 27
        self.dict['anchor'] = self.anchor  # 28

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
                continue  # We deleted this one, grab next
            # Delete matching widget events prior to this event (i) which is kept
            # self.delete_older_for_widget(i)
            self.set_tip_plan()

        self.log_list = []  # Flush out log list for new events

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
                print('toolkit.py delete_older_for_widget():', self.log_nt)
                # TODO: What if entering canvas is deleted and colors not changed?
                Event = namedtuple('Event', 'time, action, widget, x, y')
                # noinspection PyArgumentList
                self.log_list[i] = Event(self.log_nt.time, self.log_nt.action,
                                         self.deleted_str,
                                         self.log_nt.x, self.log_nt.y)

    def set_tip_plan(self):
        """ Called to process event from self.log_nt """
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

        self.dict_to_fields()  # Dictionary to easy names
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
                pass  # Can't return now, need to go down for save

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
                # Same widget was entered again before fade out completed.
                pass
                # print('ERROR: Should not be visible already. If persistent, then')
                # print("activate 'tt_DEBUG = True' and check for two 'ENTER:' in a row.")

            if self.tool_type is 'canvas_button' and self.widget.state is 'normal':
                self.set_widget_colors()

        elif self.log_nt.action == 'motion':
            # Mouse motion in widget
            self.motion_time = self.log_nt.time
            if self.window_visible:
                self.move_window()

        elif self.log_nt.action == 'press':
            # Button pressed in widget
            self.press_time = self.log_nt.time

        elif self.log_nt.action == 'release':
            # Button released after press in widget
            self.release_time = self.log_nt.time

        else:
            print('ERROR: process_tip: Invalid action:', self.log_nt.action)

        self.fields_to_dict()
        self.tips_list[self.tips_index] = self.dict


# ==============================================================================
#
#   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED
#
#   message.py - ToolTipsPool, ToolTip, createToolTip - INSTANT DISPLAY tool tips
#
#   NOTE: Use toolkit.py - ToolTips() for fading tool tips
#
# ==============================================================================

VISIBLE_DELAY = 500             # ms pause until balloon tip appears (1/2 sec)
VISIBLE_DURATION = 5000         # ms balloon tip remains on screen (3 sec/line)
FADE_TIME = 250                 # 1/4 second to fade in or fade out
FADE_STEPS = 20                 # number of steps to complete fading in or out

if VISIBLE_DELAY < FADE_TIME:
    print('VISIBLE_DELAY < FADE_TIME')
    exit()
''' NOTE: Because a new tip fades in after 1/2 second we have time to
          make old tool tip fade out assuming VISIBLE_DELAY > FADE_TIME
'''


def safe_destroy(window):
    """ Indirect removal via 'tw' var is necessary to prevent artifacts

        June 12/2021: There is Tkinter flaw where enter event isn't logged
            until code is completed. The leave event has no code so quick
            move through button caused leave to be logged before enter and
            the old "active" button state was still in play. Code has been
            added to retroactively remove "active" state. Therefore this
            function may not be be necessary anymore.
    """
    tw = window
    if tw:
        tw.destroy()


class ToolTipsPool:
    """ 
        NOTE: Remove all pool references. Tips now instantly displayed!
        
        USE: New toolkit.ToolTips() class for one-step fading tips.
    
        Tooltip is defined with:

            message.CreateToolTip(widget_name,
                                  text="blah blah\n Blah blah")

    """

    def __init__(self):
        """ Background defaults to yellow """
        self.pool_number = 0        # last pool number assigned

        self.visible_pending = None  # balloon object scheduled to appear?
        self.visible_time = None    # The time balloon object will appear
        self.visible_object = None  # The balloon object (window)
        self.visible_alpha = None   # The alpha step (0.0 to 1.0)
        self.visible_next_step_time = None
        # Currently step_duration is same for visible and fade
        self.visible_step_duration = float(FADE_TIME) / 1000.0 / float(FADE_STEPS)

        ''' A new button can be logged for showing tip while previous button
            is still fading. Variables below COULD BE pointing at last tip.
        '''
        self.fade_pending = None    # Is fade out pending for balloon window?
        self.fade_time = None       # The time a balloon will begin fading
        self.fade_object = None     # The object (window) that will fade
        self.fade_alpha = None      # The alpha step (1.0 to 0.0)
        self.fade_next_step_time = None
        # Currently step_duration is same for visible and fade
        self.fade_step_duration = float(FADE_TIME) / 1000.0 / float(FADE_STEPS)

        self.last_10_times = [0.0] * 10
        self.last_10_times_count = 0

        # We can leave before we enter due to lag creating window
        self.ignore_showtip_count = 0

        # Tkinter bug can cause enter event twice in a row and
        # leave event twice in a row.
        self.last_tool_hide = None
        self.last_tool_show = None
        self.tool_text = None

        # Reset button to normal under fast mouse moving situations
        # TODO: Is this only for last visible widget which can be different
        #       than last fade widget?
        self.reset_widget = None
        self.reset_state = None

    def register(self):
        """ Called by ToolTip() to register a new tooltip """
        self.pool_number += 1
        return self.pool_number

    @staticmethod
    def expel():
        """ Called by ToolTip() to expel an existing tooltip """
        #self.pool_number -= 1 # We can't decrement pool number because
        #                        objects have reference to their own number
        #print('tool:', tool, 'widget:', widget)
        #print('EXPEL tool.text:\n', tool.text, '\n widget:', widget)
        #    print('tool.text:', tool.text, 'widget:', widget)
        #AttributeError: ToolTipsPool instance has no attribute 'text'
        pass


    def poll_tips(self):
        """ Check for fading in new tooltip and/or fading out current tooltip """
        now = time.time()
        #if self.reset_widget:
            #print(h(time.time()),
            #      'ToolTipsPool.poll_tips() 1: reset button to:', self.reset_state)
            #self.reset_widget['state'] = self.reset_state

        self.last_10_times.insert(0, now)
        self.last_10_times.pop()

        ''' Check if window has been destroyed. eg by toplevel closing. '''
        if self.visible_object:
            if not self.visible_object.winfo_exists():
                self.visible_object = None
                self.visible_pending = None
                return
        if self.fade_object:
            if not self.fade_object.winfo_exists():
                self.fade_object = None
                self.fade_pending = None
                return

        ''' Pending event to start displaying tooltip balloon?
        '''
        if self.visible_pending:
            # Balloon not started yet?
            if self.visible_alpha == 0.0:
                # Should we start displaying Balloon now?
                if now > self.visible_time:
                    # Begin displaying balloon
                    self.visible_object.deiconify()  # Reverse window.withdraw()
                    self.visible_next_step_time = now
                    self.fade_in()
            elif self.visible_alpha >= 1.0:
                # If previous window is still fading destroy it early
                if self.fade_pending:
                    safe_destroy(self.fade_object)

                # We are fully visible, setup to activate fade out
                self.fade_pending = True  # balloon object scheduled to fade out

                # If number of lines > 2 then VISIBLE_DURATION = 3 seconds per line
                count = self.tool_text.count('\n')
                if count > 2:
                    self.fade_time = now + count * 3.0
                else:
                    self.fade_time = now + (float(VISIBLE_DURATION) / 1000)

                self.fade_object = self.visible_object
                self.fade_alpha = 1.0
                self.visible_pending = None  # don't use False - IT BREAKS
                self.visible_object = None
                self.visible_alpha = 0.0     # Temporary should be in showtip init section
                #print('fade pending seconds:', self.fade_time - time.time())
            else:
                # Fading in has begun, is it time for next step?
                if now > self.visible_next_step_time:
                    self.fade_in()

        # Pending event to start fading balloon?
        if self.fade_pending:
            # Fading started yet?
            if self.fade_alpha == 1.0:
                # Should we start fading Balloon now?
                if now > self.fade_time:
                    # Begin displaying balloon
                    self.fade_next_step_time = now
                    self.fade_out()
            elif self.fade_alpha <= 0.0:
                # We are fully faded, destroy window and clear variables
                self.fade_pending = None  # don't use False - IT BREAKS
                safe_destroy(self.fade_object)
                self.fade_object = None
            else:
                # We are already displaying Balloon is it time for next step?
                if now > self.fade_next_step_time:
                    self.fade_out()

        # Do twice in case first doesn't stick because when Tkinter sets
        # active state when button enter is finished which can be after leave
        if self.reset_widget:
            #print(h(time.time()),
            #      'ToolTipsPool.poll_tips() 2: reset button to:', self.reset_state)
            self.reset_widget['state'] = self.reset_state
        self.reset_widget = None
        self.reset_state = None

    def fade_in(self):
        """ Advance to next step in fading in process """

        # Take into account lagging caused by other functions
        self.visible_next_step_time = \
            self.visible_next_step_time + self.visible_step_duration
        # Set alpha channel to make more visible
        self.visible_alpha += 1.0 / float(FADE_STEPS)
        self.visible_object.attributes("-alpha", self.visible_alpha)
        self.visible_object.update_idletasks()

    def fade_out(self):
        """ Advance to next step in fade out process """
        # Take into account lagging caused by other functions
        self.fade_next_step_time = \
            self.fade_next_step_time + self.fade_step_duration
        # Set alpha channel to make more invisible
        self.fade_alpha -= 1.0 / float(FADE_STEPS)
        self.fade_object.attributes("-alpha", self.fade_alpha)
        self.fade_object.update_idletasks()

    def set_button(self, widget, state):
        self.reset_widget = widget
        self.reset_state = state

    def showtip(self, tool, window):
        """ Begin countdown to show tooltip window """
        # Previous tip should have been erased by hidetip()
        #print('', h(time.time()), ' ToolTipsPool ENTER button')
        '''
        if self.ignore_showtip_count > 0:
            print('', h(time.time()),
                  ' ToolTipsPool ENTER. count:', self.ignore_showtip_count)
            self.ignore_showtip_count -= 1
            return

        if tool == self.last_tool_show:
            # Tkinter bug can cause two leaves in a row
            print('ToolTipsPool showtip same tool twice in a row:', tool)
            return
        '''
        self.last_tool_show = tool
        self.tool_text = tool.text

        if self.visible_pending:
            # This happens when tooltip is fading and multiple enter and leaves are done
            print('ToolTipsPool.showtip(): Previous tooltip should not be waiting to be visible:\n',
                  self.visible_object)
            ''' ILLUSTRATED BY:
ENTER: 3048 60 41
LEAVE: 3048 157 28
ENTER: 3696 0 28
LEAVE: 3696 159 9
ENTER: 4200 2 8
ToolTipsPool.showtip(): Previous tooltip should not be waiting to be visible:
 .140121171504736.140121162102832.140121162103696.140121162289448
LEAVE: 4200 56 -1
ENTER: 4200 106 0
LEAVE: 4200 172 14

                There should only be three segments to identify widget but there are
                now four segments.
                
                When widget created extract third of three segments and search for it
                when there are four segments.
            '''

            safe_destroy(self.visible_object)
            safe_destroy(self.fade_object)          # still have window after visible destroy?

        self.visible_pending = True     # balloon object scheduled to appear
        self.visible_time = time.time() + (float(VISIBLE_DELAY) / 1000)
        self.visible_object = window    # The balloon object that will appear
        self.visible_alpha = 0.0         # The alpha steps from 0.0 to 1.0

    def hidetip(self, tool, _window):
        """ Force countdown to start fading tooltip window """
        #print('', h(time.time()), ' ToolTipsPool LEAVE button')
        '''
        if _window != self.visible_object:
            # We are leaving button before tooltip balloon (window) created
            self.ignore_showtip_count += 1
            print('', h(time.time()),
                  ' ToolTipsPool LEAVE. count:', self.ignore_showtip_count)
            return

        if tool == self.last_tool_hide:
            # Tkinter bug can cause two leaves in a row
            print('', h(time.time()),
                  ' ToolTipsPool LEAVE button twice in a row. tool:', tool)
            return
        '''
        self.last_tool_hide = tool

        if self.fade_pending:
            # Already scheduled to fade so accelerate process
            self.fade_time = 1.1    # Fading scheduled long long time ago
            self.fade_next_step_time = 1.1
        elif self.visible_pending:
            # Destroy previous tooltip's invisible window
            safe_destroy(self.visible_object)
            self.visible_pending = None
            self.visible_object = None
        else:
            #print('ToolTipsPool: Neither self.fade_pending or self.visible_pending')
            pass  # This simply means window was already displayed and removed

    def button_press(self):
        """ Button was pressed so we want to override tooltip """
        if self.visible_pending:
            # print ('poll_tips(): button press: visible_pending')
            safe_destroy(self.visible_object)
            safe_destroy(self.fade_object)          # still have window after visible destroy?
            self.visible_pending = None

        if self.fade_pending:
            # print ('poll_tips(): button press: visible_pending')
            safe_destroy(self.visible_object)
            safe_destroy(self.fade_object)          # still have window after visible destroy?
            self.fade_pending = None

    def button_release(self):
        """ Button was released """
        pass


    def print_poll_times(self):
        """ Print out pool timing information (run times) """
        print('self.last_10_times', self.last_10_times)
        last_value = 0.0
        values = []
        for value in self.last_10_times:
            if last_value == 0.0:
                last_value = value
                continue
            values.append(last_value - value)
            last_value = value
        print('durations:', values)

# ==============================================================================
#
#   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED
#
# ==============================================================================


class ToolTip(object):

    def __init__(self, widget, text, pool=None, tool_type='button'):
        """ Background defaults to yellow """
        self.widget = widget
        # Invert tooltip colors from widget colors
        if tool_type is 'button':
            self.fg = self.widget["background"]
            self.bg = self.widget["foreground"]
        else:
            self.fg = None
            self.bg = None

        self.tip_window = None
        self.text = text                    # Breaks if text dynamically changed
        self.pool = pool
        self.tool_type = tool_type
        self.alpha = 0.0
        self.enter_time = time.time()
        self.leave_time = time.time()
        self.window_ready = False           # Window is not ready for displaying


    def showtip(self, new_text):
        """ Display text in tooltip window

            TODO: When the widget is at bottom of monitor mount the tooltip
                  above the widget.
        """

        self.enter_time = time.time()
        self.text = new_text            # Longer text will fade later

        ext.t_init('ToolTip showtip()')
        self.window_ready = False
        #print('', h(time.time()), ' ToolTip ENTER button')
        # Screen coordinates for tooltip balloon (window)
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10

        # Invert tooltip colors from current widget album art colors.
        if self.tool_type is 'button':
            self.fg = self.widget["background"]
            self.bg = self.widget["foreground"]
        else:
            self.fg = None
            self.bg = None

        self.tip_window = tw = tk.Toplevel(self.widget)
        # TODO: Failed attempts to prevent brief window generation before fade in
        #       Redesign to create windows when tooltip created instead.
        #       Before fade in current parent geometry (button) must be reread and
        #           background / foreground colors must be reset to parent (button).
        if self.pool:
            tw.wm_overrideredirect(1)  # June 13/20201 debug long press, move this to top.
            # https://www.tcl.tk/man/tcl8.6/TkCmd/wm.htm#M9
            #self.tip_window['background'] = self.bg
            tw['background'] = self.bg
            # https://stackoverflow.com/a/52123172/6929343
            tw.wm_attributes('-type', 'tooltip')      # only works X11 and not all distros
            tw.wm_geometry("+%d+%d" % (x, y))
            tw.wait_visibility()
            tw.withdraw()  # Reverse with deiconify
            #self.tip_window.attributes("-alpha", 0)  # Make invisible alpha
        else:
            # We won't be fading in/out
            self.tip_window.withdraw()  # Remain invisible while we figure out the geometry
            # Default background color must be same as widget foreground
            self.tip_window['background'] = self.bg
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))

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
        label = tk.Label(tw, text=new_text, justify=tk.LEFT,
                         background=self.bg, foreground=self.fg, relief=tk.SOLID,
                         borderwidth=2, pady=10, padx=10, font=(None, MED_FONT))
        label.pack(ipadx=2)

        #root.update()
        if self.leave_time > self.enter_time:
            # Mouse may have left button before tooltip was generated
            self.destroy_window()
            #print('ToolTip ENTER button ABORT')
            if self.tool_type is 'button':
                if self.pool:
                    # Reset button state for poll_tips()
                    self.pool.set_button(self.widget, tk.NORMAL)
                if self.widget['state'] != tk.NORMAL:
                    #print('ToolTip.showtip(): reset button state to tk.NORMAL')
                    self.widget['state'] = tk.NORMAL
            # TODO: Button processing for 'canvas_button' self.tool_type
            return

        ext.t_end('no_print')

        if self.pool:
            ''' When tooltips pool exists, it will delay hoover mount 500 ms 
                and fade out balloon after 5 seconds.
            '''
            self.tip_window.attributes("-alpha", 0)     # Make invisible alpha
            self.window_ready = True
            self.pool.showtip(self, self.tip_window)          # Set timer to display
        else:
            self.window_ready = True
            self.tip_window.deiconify()  # Become visible at the desired location


    def hidetip(self):
        """ Hide tooltip when cursor leaves bbox
        """
        #last_time = self.leave_time        # For debugging print line below
        self.leave_time = time.time()
        #print('', h(time.time()), ' ToolTip LEAVE button')
        if self.tool_type is 'button':
            if self.pool:
                self.pool.set_button(self.widget, tk.NORMAL)
            if self.widget['state'] != tk.NORMAL:
                #print('ToolTip.hidetip(): reset button state to tk.NORMAL')
                self.widget['state'] = tk.NORMAL
        '''
        if self.leave_time > self.enter_time:
            # Nothing to do, window destroyed as we leave before mounting
            print('ToolTip LEAVE button ABORT')
            self.leave_time = time.time() + 1000.0  # Add 1,000 bogus seconds
            return
        '''

        if not self.window_ready:
            # Window hasn't been ready for displaying yet
            #print('ToolTip LEAVE: Window not ready last leave time difference:',
            #      self.leave_time - last_time)
            return

        # Helps trap Tkinter calling us twice in a row.
        self.window_ready = False

        if self.pool:
            ''' When tooltips pool exists, it will delay hoover mount 500 ms 
                and fade out balloon after 5 seconds.
            '''
            self.pool.hidetip(self, self.tip_window)
        else:
            self.destroy_window()

    def destroy_window(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

    def button_press(self):
        """ Button was pressed so we want to override tooltip """
        if self.pool:
            self.pool.button_press()

    def button_release(self):
        """ Button was released """
        if self.pool:
            self.pool.button_release()

# ==============================================================================
#
#   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED   NOT USED
#
# ==============================================================================


class CreateToolTip(object):

    def __init__(self, widget, text='Pass text here', pool=None,
                 tool_type='button'):
        """
        Create tooltip for labels, buttons, etc. Initially sharp yellow rectangles
        Concept from: https://stackoverflow.com/a/56749167/6929343 - AND -
        http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml#e387

        Enhanced to make text and instance and return tooltip object in order to
        dynamically change text depending on processing step.
        """

        self.widget = widget
        self.text = text
        self.pool = pool
        self.tool_type = tool_type
        try:
            self.name = self.widget['text']         # For display during debugging
        except tk.TclError:
            self.name = self.tool_type              # 'canvas_button' or 'menu' type
        # For canvas rounded rectangle buttons we need extra variables
        self.button_press_time = None
        self.button_release_time = None
        self.normal_text_color = None
        self.normal_button_color = None
        self.tool = ToolTip(self.widget, self.text, pool=self.pool, tool_type=self.tool_type)

        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)
        if tool_type is 'button':
            self.widget.bind("<ButtonPress-1>", self.on_press)
            self.widget.bind("<ButtonRelease-1>", self.on_release)

        self.pool_number = None
        if self.pool:
            ''' When tooltips pool exists, it will delay hoover mount 500 ms 
                and fade out balloon after 10 seconds.
                TODO: Pass the widget (button) and tooltip widget
            '''
            self.pool_number = self.pool.register()
            #print('self.pool_number:', self.pool_number)


    def enter(self, _event):
        """
        """
        prt_time = datetime.utcnow().strftime("%M:%S.%f")[:-3]
        print('ENTER:', prt_time, str(_event.widget)[-4:], _event.x, _event.y)
        if self.tool_type is 'canvas_button' and self.widget.state is 'normal':
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

        self.tool.showtip(self.text)            # Override with changed text

    def leave(self, _event):
        """
        Enter has 500 ms delay so leave may come before tooltip displayed.

        TEST: When leaving early button remains "active" so force to "normal".
        """
        prt_time = datetime.utcnow().strftime("%M:%S.%f")[:-3]
        print('LEAVE:', prt_time, str(_event.widget)[-4:], _event.x, _event.y)
        #print('\n', h(time.time()), ' CreateToolTip LEAVE button:', self.name)
        if self.tool_type is 'button':
            if self.pool:
                self.pool.set_button(self.widget, tk.NORMAL)
            if self.widget['state'] != tk.NORMAL:
                #print('CreateToolTip.leave(): reset button state to tk.NORMAL')
                self.widget['state'] = tk.NORMAL

        if self.tool_type is 'canvas_button' and self.widget.state is 'active':
            #print('CreateToolTip.leave(): reset canvas button state to normal')
            self.widget.state = 'normal'
            self.widget.itemconfig("button_color", fill=self.normal_button_color,
                                   outline=self.normal_button_color)
            self.widget.itemconfig("text_color", fill=self.normal_text_color)

        self.tool.hidetip()


    def on_press(self, _event):
        """ Widget type is button and it was just pressed """
        prt_time = datetime.utcnow().strftime("%M:%S.%f")[:-3]
        print('PRESS:', prt_time, str(_event.widget)[-4:], _event.x, _event.y)
        self.button_press_time = time.time()
        # print('Button pressed: ', h(self.button_press_time))
        self.tool.button_press()


    def on_release(self, _event):
        """ Widget type is button and it was just pressed """
        prt_time = datetime.utcnow().strftime("%M:%S.%f")[:-3]
        print('REL_S:', prt_time, str(_event.widget)[-4:], _event.x, _event.y)
        self.button_release_time = time.time()
        # print('Button released:', h(self.button_release_time))
        self.tool.button_release()


# End of message.py
