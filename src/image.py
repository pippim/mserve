#!/usr/bin/env python
# -*- coding: utf-8 -*-
#==============================================================================
#
#       image.py - Image processing
#
#           import image as img
#
#   Jun. 19 2023 - Reduce triangle (chevrons) clicking errors with white space.
#
#==============================================================================

from __future__ import print_function       # Must be first import
from __future__ import with_statement       # Error handling for file opens

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

# import subprocess32 as sp  # Not used and causing error in ~/bserve/b
import os
#import threading
import re
import time
import datetime
import io
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageFilter, ImageOps
from collections import namedtuple

import x11                  # Home-brewed x11 wrapper functions
import external as ext
import monitor              # Screen, Monitor and Window functions


MON_FONTSIZE = 12                   # Font size for monitor name
WIN_FONTSIZE = 11                   # Font size for Window name

# Make Gradient image below from: https://stackoverflow.com/a/32532502/6929343
BLACK, DARK_GRAY, GRAY = ((0, 0, 0), (63, 63, 63), (127, 127, 127))
LIGHT_GRAY, WHITE = ((191, 191, 191), (255, 255, 255))
BLUE, GREEN, RED = ((0, 0, 255), (0, 255, 0), (255, 0, 0))


class Point(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

    @staticmethod
    def from_point(other):
        return Point(other.x, other.y)


class Rect(object):
    def __init__(self, x1, y1, x2, y2):
        minx, max_x = (x1, x2) if x1 < x2 else (x2, x1)
        miny, max_y = (y1, y2) if y1 < y2 else (y2, y1)
        self.min = Point(minx, miny)
        self.max = Point(max_x, max_y)

    @staticmethod
    def from_points(p1, p2):
        return Rect(p1.x, p1.y, p2.x, p2.y)

    def __str__(self):
        return 'Rect({:d}, {:d}, {:d}, {:d})'.format(self.min.x, self.min.y,
                                                     self.max.x, self.max.x)
    width  = property(lambda self: self.max.x - self.min.x)
    height = property(lambda self: self.max.y - self.min.y)


def gradient_color(min_val, max_val, val, color_palette):
    """ Computes intermediate RGB color of a value in the range of min_val
        to max_val (inclusive) based on a color_palette representing the range.
    """
    max_index = len(color_palette)-1
    delta = max_val - min_val
    if delta == 0:
        # delta = 1:      ### SyntaxError: invalid syntax on the ':'
        delta = 1
    v = float(val-min_val) / delta * max_index
    i1, i2 = int(v), min(int(v)+1, max_index)
    (r1, g1, b1), (r2, g2, b2) = color_palette[i1], color_palette[i2]
    f = v - i1
    return int(r1 + f*(r2-r1)), int(g1 + f*(g2-g1)), int(b1 + f*(b2-b1))


def hor_gradient(draw, rect, color_func, color_palette):
    min_val, max_val = 1, len(color_palette)
    delta = max_val - min_val
    for x in range(rect.min.x, rect.max.x+1):
        f = (x - rect.min.x) / float(rect.width)
        val = min_val + f * delta
        color = color_func(min_val, max_val, val, color_palette)
        draw.line([(x, rect.min.y), (x, rect.max.y)], fill=color)


def vert_gradient(draw, rect, color_func, color_palette):
    min_val, max_val = 1, len(color_palette)
    delta = max_val - min_val
    for y in range(rect.min.y, rect.max.y+1):
        f = (y - rect.min.y) / float(rect.height)
        val = min_val + f * delta
        color = color_func(min_val, max_val, val, color_palette)
        draw.line([(rect.min.x, y), (rect.max.x, y)], fill=color)


# Deviation from original answer, function with text drawing feature
def make_image(text, image_w=200, image_h=200):
    """ Make image of blue, green, red overlapping gradients vertically
        Draw text in middle
    """
    color_palette = [BLUE, GREEN, RED]
    region = Rect(0, 0, image_w, image_h)
    img_x, img_y = region.max.x+1, region.max.y+1
    image = Image.new("RGB", (img_x, img_y), WHITE)
    draw = ImageDraw.Draw(image)
    vert_gradient(draw, region, gradient_color, color_palette)

    # Size of font depends on width of image - '/6' to '/7' on  October 7 2020
    icon_font = ImageFont.truetype("DejaVuSans.ttf", int(float(image_w) / 7))

    text_width, text_height = icon_font.getsize(text)
    start_x = int(int(image_w - text_width) / 2)
    start_y = int(int(image_h - text_height) / 2)

    if start_x < 0:
        start_x = 0
    draw.text((start_x, start_y), text, fill=(0, 0, 0), font=icon_font)

    """
    # DEBUG image shifting 10% in all four directions
    print('DEBUG shift_image() ===============================================')
    print('Image width:', image_w, 'height:', image_h, 'percent:', .1)
    shifted_image = shift_image(image, 'left', image_w, image_h, .1)
    shifted_image.show()
    shifted_image = shift_image(image, 'right', image_w, image_h, .1)
    shifted_image.show()
    shifted_image = shift_image(image, 'up', image_w, image_h, .1)
    shifted_image.show()
    shifted_image = shift_image(image, 'down', image_w, image_h, .1)
    shifted_image.show()
    """

    return image


def ruler_image(image_w=800, image_h=10):
    """ Make image of blue, green, red overlapping gradients horizontally
    """
    color_palette = [BLUE, GREEN, RED]
    region = Rect(0, 0, image_w, image_h)
    img_x, img_y = region.max.x+1, region.max.y+1
    image = Image.new("RGB", (img_x, img_y), WHITE)
    draw = ImageDraw.Draw(image)
    hor_gradient(draw, region, gradient_color, color_palette)

    return image


def hex_to_rgb(hex_str):
    """ translate tkinter hex color code #ffffff to rgb tuple of integers
        https://stackoverflow.com/a/29643643/6929343
    """
    h = hex_str.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb):
    """ translate rgb tuple of integers to tkinter format hex color code
    """
    return "#%02x%02x%02x" % rgb


def shade_rgb(rgb):
    """ Adjust shade of rgb by 25% (value 64 out of 256). See:
            https://stackoverflow.com/a/67963422/6929343

        :param rgb: tuple of red, green, blue integers 0 to 255
        :returns:   tuple of red, green, blue integers 0 to 255
    """
    return tuple(i + 64 if i < 128 else i - 64 for i in rgb)


def darken_rgb(rgb):
    """ Adjust shade of rgb 25% darker with clamp at 0.

        :param rgb: tuple of red, green, blue integers 0 to 255
        :returns:   tuple of red, green, blue integers 0 to 255
    """
    return tuple(i - 64 if i > 64 else 0 for i in rgb)


def lighten_rgb(rgb):
    """ Adjust shade of rgb 25% darker with clamp at 0.

        :param rgb: tuple of red, green, blue integers 0 to 255
        :returns:   tuple of red, green, blue integers 0 to 255
    """
    return tuple(i + 64 if i < 191 else 255 for i in rgb)


def contrasting_hex_color(hex_str):
    """ Pass string with hash sign of RGB hex digits.
        Returns white or black hex code contrasting color passed.
    """
    (r, g, b) = (hex_str[1:3], hex_str[3:5], hex_str[5:])
    return '#000000' if 1 - (int(r, 16) * 0.299 + int(g, 16) * 0.587 +
                             int(b, 16) * 0.114) / 255 < 0.5 else '#ffffff'


def contrasting_rgb_color(dec_tuple):
    """ Pass (r,g,b) tuple of background color.
        Returns white or black (r,g,b) tuple contrasting color passed.
    """
    (r, g, b) = dec_tuple
    return (0, 0, 0) if 1 - (r * 0.299 + g * 0.587 +
                             b * 0.114) / 255 < 0.5 else (255, 255, 255)


def shift_image(img_name, direction, width, height, percent):
    """ Shift image down, left, right or up a given percentage.

    """
    # print('shift_image(): img_name:',img_name,'direction:',direction)
    # print('width:',width,'height:',height,'percent:',percent)
    if percent <= 0.0 or percent >= 100.0:
        # Trap impossible percentage to slide
        return img_name

    # Defaults for: crop_ = img_name.crop([ left, upper, right, lower])
    #left = 0; upper = 0; right = width-1; lower = height-1
    left = upper = 0
    right = width
    lower = height
    crop1 = [left, upper, right, lower]
    crop2 = [left, upper, right, lower]
    # New image built from crop1 to (x1, y1) and crop2 to (x2, y2)
    x1_offset = y1_offset = x2_offset = y2_offset = 0

    if direction == 'left' or direction == 'right':
        pixels_shifted = int(float(width) * percent)
        if direction == 'left':
            crop1[0] = pixels_shifted
            crop2[2] = pixels_shifted
            x2_offset = right - pixels_shifted
        else:  # direction == 'right':
            crop1[2] = right - pixels_shifted
            crop2[0] = right - pixels_shifted
            x1_offset = pixels_shifted
    else:  # direction is 'up' or 'down'
        pixels_shifted = int(float(height) * percent)
        if direction == 'down':
            crop2[1] = lower - pixels_shifted
            y1_offset = pixels_shifted
        else:  # direction == 'up':
            crop1[1] = pixels_shifted
            crop2[3] = pixels_shifted
            y2_offset = lower - pixels_shifted

    # print('Shift:',pixels_shifted,direction,'crop1:',crop1,'crop2:',crop2)
    main_image = img_name.crop(crop1)
    small_image = img_name.crop(crop2)
    new_image = Image.new('RGB', (width, height))

    new_image.paste(main_image, (x1_offset, y1_offset))
    new_image.paste(small_image, (x2_offset, y2_offset))
    
    return new_image


def make_checkboxes(hgt, out_c, fill_c, chk_c):

    """ Create CheckboxTreeview(); 'unchecked', 'checked' and 'tristate'
        Parameters: height, outline color, fill color, checkmark color

        Returns list of three PhotoImages for parent. How to use 4K screen:

            MON_FONTSIZE = 12
            row_height=int(MON_FONTSIZE*2.2)
            style.configure("Treeview", font=(None, MON_FONTSIZE), \
                            rowheight=row_height)

            self.checkboxes = make_checkboxes(row_height-6, 'black', \
                                              'white', 'deepskyblue')
            self.cd_tree.tag_configure("unchecked", image=self.checkboxes[0])
            self.cd_tree.tag_configure("tristate", image=self.checkboxes[1])
            self.cd_tree.tag_configure("checked", image=self.checkboxes[2])

    """
#    from PIL import Image, ImageTk, ImageDraw       # Pillow image processing

    if hgt % 2 == 1:
        hgt = hgt + 1                               # even number box height
    if hgt < 14:
        hgt = 14                                    # minimum box height
    wid = hgt                                       # square: width = height
    wid_pad = int(wid * 10 / 20)                    # lead + trailing padding
    xo = int(wid_pad / 5)                           # x-offset after lead pad
    ret_images = []                                # list of three images

    image = Image.new("RGBA", (wid + wid_pad, hgt), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)                    # Create drawable image

    draw.rectangle([(xo, 0), (xo + wid, hgt-1)], fill=fill_c, outline=out_c)
    ret_images.append(ImageTk.PhotoImage(image))   # Unchecked
    draw.rectangle([(xo+3, 7), (xo + wid-3, hgt-8)], fill=chk_c)
    ret_images.append(ImageTk.PhotoImage(image))   # Tristate
    draw.rectangle([(xo+3, 3), (xo + hgt-3, hgt-4)], fill=chk_c)
    ret_images.append(ImageTk.PhotoImage(image))   # Checked

    return ret_images


def make_triangles(triangle_list, hgt, out_c, fill_c):

    """ Make triangles (chevrons) for open, close and empty tree parent
    """
    width = int(hgt * 1.8)  # Padding right of triangle reduces clicking errors
    im_open, im_close, im_empty = triangle_raw_images(hgt, out_c, fill_c)
    triangle_list.append(ImageTk.PhotoImage(im_open))   # assign to passed
    triangle_list.append(ImageTk.PhotoImage(im_close))  # list to stop GC -
    triangle_list.append(ImageTk.PhotoImage(im_empty))  # (Garbage collector)

    # custom indicator
    style = ttk.Style()
    # Check if triangles already created.
    element_list = style.element_names()
    if 'Treeitem.myindicator' in element_list:
        # print('Treeitem.myindicator already created in image.py make_triangles()')
        return

    try:
        style.element_create('Treeitem.myindicator', 'image', triangle_list[1],
                             ('user1', '!user2', triangle_list[0]),
                             ('user2', triangle_list[2]),
                             sticky='w', width=width)
    except tk.TclError:
        print('Treeitem.myindicator tk.TclError in image.py make_triangles()')
        return

    # replace Treeitem.indicator by custom one
    style.layout(
        'Treeview.Item',
        [('Treeitem.padding',
          {'sticky': 'nswe',
           'children': [
                ('Treeitem.myindicator', {'side': 'left', 'sticky': ''}),
                ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                ('Treeitem.focus', {'side': 'left', 'sticky': '', 'children':
                                    [('Treeitem.text', 
                                      {'side': 'left', 'sticky': ''})]
                                    })
                      ]
           })])

    ''' June 19, 2023 - Attempt 'indent' to put more space between triangles
        and checkboxes in order to prevent accidental clicking. See:
        https://stackoverflow.com/questions/61280744/
        tkinter-how-to-adjust-treeview-indentation-size-and-indicator-arrow-image
        
        Marginal success. Old format:
        1
         12
           121
           122
         13
          131
        
        New format.
        
        1
            12
                 121
                 122
            13
                 131

        However it only indents entire row and doesn't put whitespace between
        triangle (chevron) and checkbox.
    '''
    #print("style.configure('Treeview', indent=50)")
    style.configure('Treeview', indent=63)


def triangle_raw_images(hgt, out_c, fill_c):

    """ Make triangles for open, close and empty tree parent
    """
    ''' Create CheckboxTreeview(); 'im_empty', 'im_open' and 'im_close'
        Parameters: height, outline color, fill color

        Returns list of three raw images suitable for Photo conversion.
        How to use:

            MON_FONTSIZE = 12
            row_height=int(MON_FONTSIZE*2.2)
            style.configure("Treeview", font=(None, MON_FONTSIZE), \
                            rowheight=row_height)

            self.triangles = triangle_raw_images(row_height-5, 'black', 'gray')

    '''
#    from PIL import Image, ImageTk, ImageDraw       # Pillow image processing

    """
    """

    # Following comments when passed hgt = 17
    wid = hgt                                       # square image
    hgt_off = 4                                     # top & bottom whitespace
    # TODO: June 19, 2023 - calculate an even number above instead of hard code
    #print("hgt:", hgt, "hgt_off:", hgt_off)
    wxy = (0, hgt_off, )                                # x=0, y=4
    #print("wxy:", wxy)
    exy = (wid - 2, hgt_off, )                          # x=15, y=4
    #print("exy:", exy)
    sxy = (int((hgt - 1) / 2), hgt - hgt_off / 2, )     # x=8, y=15
    #print("sxy:", sxy)

    wxy2 = (hgt_off / 2, hgt_off / 2, )                 # x=2, y=2
    #print("wxy2:", wxy2)
    exy2 = (wid - 2, int((wid - 1) / 2), )              # x=15, y=8
    #print("exy2:", exy2)
    sxy2 = (hgt_off / 2, hgt - hgt_off / 2, )           # x=2, y=15
    #print("sxy2:", sxy2)

    # custom indicator images
    im_open = Image.new('RGBA', (wid + wid, hgt), (0, 0, 0, 0))
    im_empty = Image.new('RGBA', (wid + wid, hgt), (0, 0, 0, 0))
    im_close = Image.new('RGBA', (wid + wid, hgt), (0, 0, 0, 0))  # June 19, 2023
    draw = ImageDraw.Draw(im_open)
    draw.polygon([wxy, exy, sxy], outline=out_c, fill=fill_c)
    #im_close = im_open.rotate(90)  # June 19, 2023 draw separately to experiment
    draw = ImageDraw.Draw(im_close)
    draw.polygon([wxy2, exy2, sxy2], outline=out_c, fill=fill_c)

    # June 19, 2023 - Some funky tests below "What if?..."
    #im_open = im_close.rotate(90)  # Make up chevron instead of down chevron

    return im_open, im_close, im_empty


def set_font_style():

    # Used by get_dir, save_items and load_items
    # Nov 15, 2020 copy from mserve to encoding,py to try in tkSimpleDialog
    #style = ttk.Style(root)
    style = ttk.Style()
    style.configure('.', font=(None, WIN_FONTSIZE))
    text = font.nametofont("TkTextFont")  # TkDefaultFont changes buttons
    text.configure(size=MON_FONTSIZE)

    # from example # 7 in program creek:
    # https://www.programcreek.com/python/example/104617/tkinter.font.nametofont
    font_types = ["TkDefaultFont", "TkTextFont", "TkFixedFont",
                  "TkMenuFont", "TkHeadingFont", "TkCaptionFont",
                  "TkSmallCaptionFont", "TkIconFont", "TkTooltipFont"]
    #ww = ['normal', 'bold']
    #if self.font_size < max(sizes):
    #    self.font_size = min([i for i in sizes if i > self.font_size])
    #else:
    #    self.font_size = sizes[0]
    #    self.font_weight = 0

    #ff = 'Helvetica' if self.font_size != min(sizes) else 'Courier'
    #self.font_weight = 0 if self.font_size == min(sizes) else 1
    for typ in font_types:
        default_font = font.nametofont(typ)
        #default_font.configure(size=self.font_size,
        #                       weight=ww[self.font_weight], family=ff)
        default_font.configure(size=WIN_FONTSIZE) 

    ''' old code in mserve '''
    icon = font.nametofont("TkIconFont")  # TkDefaultFont changes buttons
    icon.configure(size=MON_FONTSIZE)
    dialog = font.nametofont("TkCaptionFont")  # Dialog Box text
    dialog.configure(size=WIN_FONTSIZE)


def m_splash_image(hgt, out_c, fill_c, text_c, char="M"):
    """
            +-------+
            | _. ._ |
            |{  M  }|
            | -. .- |
            +-------+

        Build m splash graphics

    """

    # passed hgt = 32
    wid = hgt                                       # square image
    hgt_off = 4                                     # top & bottom whitespace
    end_off = wid - 4

    # Create new image with circle
    im_open = Image.new('RGBA', (wid, hgt), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im_open)
    draw.ellipse((hgt_off, hgt_off, end_off, end_off), outline=out_c, fill=fill_c)
    splash_font = ImageFont.truetype("DejaVuSans.ttf", int(float(wid) / 1.8))

    # Put letter M centered in circle
    text = char
    text_width, text_height = splash_font.getsize(text)
    start_x = int(int(wid - text_width) / 2)
    start_y = int(int(hgt - text_height) / 2)
    if start_x < 0:
        start_x = 0
    if start_y < 0:
        start_y = 0

    draw.text((start_x, start_y), text, fill=text_c, font=splash_font)

    im_open.save("m.png", "PNG")
    png_img = tk.Image("photo", file="m.png")
    return png_img


def m_circle_splash_image(hgt, out_c, fill_c, text_c, char='M'):
    """
              _. ._
             {  M  }
              -. .-

        Build m splash graphics as a circle with transparent background

    """

    # passed hgt = 32
    wid = hgt                                       # square image
    hgt_off = 4                                     # top & bottom whitespace
    end_off = wid - 4

    # Create new image with circle
    im_open = Image.new('RGBA', (wid, hgt), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im_open)
    draw.ellipse((hgt_off, hgt_off, end_off, end_off), outline=out_c, fill=fill_c)
    splash_font = ImageFont.truetype("DejaVuSans.ttf", int(float(wid) / 1.8))

    # Put letter M centered in circle
    text = char
    text_width, text_height = splash_font.getsize(text)
    start_x = int(int(wid - text_width) / 2)
    start_y = int(int(hgt - text_height) / 2)
    if start_x < 0:
        start_x = 0
    if start_y < 0:
        start_y = 0
    # See darken_rgb for working version of below
    # start_x = 0 if start_x < 0
    # start_y = 0 if start_y < 0

    draw.text((start_x, start_y), text, fill=text_c, font=splash_font)

    # Create duplicate image for alpha channel
    # https://note.nkmk.me/en/python-pillow-putalpha/
    im_a = Image.new('L', im_open.size, 0)
    draw_a = ImageDraw.Draw(im_a)
    draw_a.ellipse((hgt_off, hgt_off, end_off, end_off), fill=255)
    im_a_blur = im_a.filter(ImageFilter.GaussianBlur(4))

    im_rgba = im_open.copy()
    #im_rgba.putalpha(im_a)                 # Non-blurred circle edge
    im_rgba.putalpha(im_a_blur)
    im_rgba_crop = im_rgba.crop((hgt_off, hgt_off, end_off, end_off))
    im_rgba_crop.save("m.png")

    #im_open.save("m.png", "PNG")
    png_img = tk.Image("photo", file="m.png")
    return png_img


def taskbar_icon(toplevel, hgt, out_c, fill_c, text_c, char='M'):
    """
            +-------+
            | _. ._ |
            |{  M  }|
            | -. .- |
            +-------+

        Build taskbar icon into memory 
        save as png
        open png as photoicon

    """

    # passed hgt = 32
    wid = hgt                                       # square image
    hgt_off = 4                                     # top & bottom whitespace
    end_off = wid - 4

    # Create new image with circle
    im_open = Image.new('RGBA', (wid, hgt), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im_open)
    draw.ellipse((hgt_off, hgt_off, end_off, end_off), outline=out_c, fill=fill_c)
    icon_font = ImageFont.truetype("DejaVuSans.ttf", int(float(wid) / 1.8))

    # Put letter M centered in circle
    text = char
    text_width, text_height = icon_font.getsize(text)
    start_x = int(int(wid - text_width) / 2)
    start_y = int(int(hgt - text_height) / 2)
    if start_x < 0:
        start_x = 0
    if start_y < 0:
        start_y = 0
    draw.text((start_x, start_y), text, fill=text_c, font=icon_font)

    im_open.save("mserve.png", "PNG")
    # Above can be skipped when mserve.png already exists
    png_img = tk.Image("photo", file="mserve.png")
    toplevel.tk.call('wm', 'iconphoto', toplevel._w, png_img)
#    toplevel.iconphoto(True, png_img)
    # im_open.save("mserve.gif","GIF")
    # gif_img = tk.PhotoImage(file="mserve.gif")
    # toplevel.tk.call('wm', 'iconphoto', toplevel._w, gif_img)
    # Must wrap bytes in file io
    # https://pillow.readthedocs.io/en/5.1.x/reference/Image.html
    # t_file = io.BytesIO(im_open)
    # original_art = Image.open(t_file)
    # del t_file              # Delete object to save memory
    # toplevel.tk.call('wm', 'iconphoto', root._w, im_open)


def mmm_taskbar_icon(toplevel, hgt, out_c, fill_c, m1c, m2c, m3c):
    """
        Build taskbar icon into memory:
            +-------+
            |   M   |
            |  M M  |
            +-------+
        M's overlap in 3 colors
        save as png
        open png as photoicon
    """

    # passed hgt = 32
    wid = hgt                                       # square image
    hgt_off = 4                                     # top & bottom whitespace
    end_off = wid - 4

    # Create new image with circle
    im_open = Image.new('RGBA', (wid, hgt), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im_open)
    draw.rectangle((hgt_off, hgt_off, end_off, end_off), outline=out_c, fill=fill_c)
    sample_font = ImageFont.truetype("DejaVuSans.ttf", int(float(wid) / 2))

    # Put letter M centered in circle
    text = "M"
    text_width, text_height = sample_font.getsize(text)
    start_x = int(int(wid - text_width) / 1.9)  # 2 then 1.8 then 1.9
    start_y = int(float(hgt - text_height) / 5)  # 4 then 3
    if start_x < 0:
        start_x = 0
    if start_y < 0:
        start_y = 0

    draw.text((start_x, start_y), text, fill=m1c, font=sample_font)

    # second m lower to left
    start_x2 = (start_x - text_width) + int(float(text_width) / 1.9) 
    start_y2 = (start_y + text_height) - int(float(text_height) / 2.5)
    draw.text((start_x2, start_y2), text, fill=m2c, font=sample_font)

    # third m lower to right
    start_x3 = (start_x + text_width) - int(text_width / 1.85) 
    start_y3 = start_y2
    draw.text((start_x3, start_y3), text, fill=m3c, font=sample_font)

    im_open.save("mserve.png", "PNG")
    png_img = tk.Image("photo", file="mserve.png")
    toplevel.tk.call('wm', 'iconphoto', toplevel._w, png_img)
    # im_open.save("mserve.gif","GIF")
    # gif_img = tk.PhotoImage(file="mserve.gif")
    # toplevel.tk.call('wm', 'iconphoto', toplevel._w, gif_img)
    # Must wrap bytes in file io
    # https://pillow.readthedocs.io/en/5.1.x/reference/Image.html
    # t_file = io.BytesIO(im_open)
    # original_art = Image.open(t_file)
    # del t_file              # Delete object to save memory
    # toplevel.tk.call('wm', 'iconphoto', root._w, im_open)


class RoundedButton(tk.Canvas):
    """
        Create rounded button.

        # From: https://stackoverflow.com/a/60558959/6929343
    """

    def __init__(self, parent, width, height, corner_radius, padding,
                 color, bg, command=None, tags=None):

        tk.Canvas.__init__(self, parent, borderwidth=0,
                           relief="flat", highlightthickness=0, bg=bg)
        self.command = command
        self.pool = None

        if corner_radius > 0.5 * width:
            print("Error: corner_radius is greater than width.")
            return

        if corner_radius > 0.5 * height:
            print("Error: corner_radius is greater than height.")
            return

        rad = 2 * corner_radius

        def shape():
            self.create_polygon(
                (padding, height - corner_radius - padding, padding,
                 corner_radius + padding, padding + corner_radius, padding,
                 width - padding - corner_radius, padding, width - padding,
                 corner_radius + padding, width - padding, height -
                 corner_radius - padding, width - padding - corner_radius,
                 height - padding, padding + corner_radius, height -
                 padding), fill=color, outline=color, tags=tags)
            self.create_arc(
                (padding, padding + rad, padding + rad, padding), start=90,
                extent=90, fill=color, outline=color, tags=tags)
            self.create_arc(
                (width - padding - rad, padding, width - padding, padding +
                 rad), start=0, extent=90, fill=color, outline=color, tags=tags)
            self.create_arc(
                (width - padding, height - rad - padding, width - padding -
                 rad, height - padding), start=270, extent=90, fill=color,
                outline=color, tags=tags)
            self.create_arc(
                (padding, height - padding - rad, padding + rad, height -
                 padding), start=180, extent=90, fill=color, outline=color,
                tags=tags)

        #id = shape()
        shape()
        (x0, y0, x1, y1) = self.bbox("all")
        width = (x1 - x0)
        height = (y1 - y0)
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.state = 'normal'
        self.bind('<Enter>', self.enter)
        self.bind('<Leave>', self.leave)

    def _on_press(self, _event):
        self.configure(relief="sunken")
        if self.pool:
            # Tell tool tips not to display
            self.pool.button_press()

    def _on_release(self, _event):
        self.configure(relief="raised")
        # TODO: get event.x and event.y to ensure within BBOX
        if self.command:
            self.command()

    def enter(self, _event):
        """
            When entering button, tooltips have delayed fade in
            TODO: Set color for active button state
        """
        self.state = 'active'

    def leave(self, _event):
        """
            When leaving button, tooltips fade out (if visible after delay)
            TODO: Set color for normal button state
        """

        # print('\n', h(time.time()), ' CreateToolTip LEAVE button:', self.name)
        self.state = 'normal'
        '''
        if self.tool_type is 'button':
            if self.pool:
                self.pool.set_button(self.widget, tk.NORMAL)
            if self.widget['state'] != tk.NORMAL:
                # print('CreateToolTip.hidetip(): reset button state to tk.NORMAL')
                self.widget['state'] = tk.NORMAL

        self.tool.hidetip()
        '''

    def register_pool(self):
        """ June 15 2023 - Appears to be unused """
        self.pool = pool


class RoundedRectangle(RoundedButton):
    """
    Create rounded rectangles for mserve. A canvas object is
    returned with image drawn rectangle with text draw within.
    Rectangle height is determined by reference object. The
    text size is set with 10x padding around y-top and y-bottom.
    The rectangle width is determined by Text length + 10x pad.

    NOTE: mserve has four rounded rectangles occupying same space
          so it is important to set width of all rectangles the
          same to prevent underlying rectangles creating shadow.

    #:param: Object: Pointer to reference widget (usually label)
    """
    '''

           BUTTON IMAGE          TOOLTIP TEXT

         /--------------\
        | Manual Scroll  |  - Click for Auto Scroll
         \\-------------/

         /--------------\
        | Manual Scroll  |  - Click for Time Scroll
         \\-------------/

         /--------------\
        |  Auto Scroll   |  - Click for Manual Scroll
         \\-------------/

         /--------------\
        |  Time Scroll   |  - Click for Manual Scroll
        \\--------------/

    '''

    def __init__(self, parent, text, color, bg, ms_font=(None, WIN_FONTSIZE),
                 command=None, stretch=True):

        # As of June 10/2021 mserve 'ms_font' is '(None, SIZE)' tuple.
        # ms_font is a label on same line to give height for rounded rectangle
        # The font size for text inside rounded rectangle is 2 points less
        width, height = canvas_text_bbox_size(text, ms_font)
        height_extra = ms_font[1] / 2       # Tweaking factor
        if height < width:
            corner_radius = height / 2
        else:
            corner_radius = width / 2
        width_extra = corner_radius * 2     # Tweaking factor
        padding = 0
        if stretch is True:
            # By default text strings require a little bigger rectangle
            self.width = width + width_extra
            self.height = height + height_extra
        else:
            # Single character text don't require extra space. eg Hamburger
            self.width = width + 5      # Awkward
            self.height = height + 2

        self.button = RoundedButton.__init__(
            self, parent, self.width, self.height, corner_radius,
            padding, color, bg, command=command, tags="button_color")

        # Subtract 2 points from Font size so text fits in rounded button
        family, size = ms_font
        text_size = size - 2
        font_width, font_height = canvas_text_bbox_size(text, (family, text_size))
        #text_x = width - corner_radius * 1.8 - font_width / 2
        text_x = width - font_width / 2
        text_y = height - font_height / 2
        #print('font_width, font_height, text_x, text_y:',
        #      font_width, font_height, text_x, text_y)
        self.text = text
        """ June 15 2023 - self.create_text() s/b global create_text() instead  """
        self.create_text((text_x, text_y), text=self.text, tags="text_color",
                         # font=(family, text_size, "italic", "bold"), fill='white')
                         font=(family, text_size), fill='white')

        ''' Now that button is fully created tooltip can be registered.
            We want the tooltip to not appear if button already clicked. Clicking the
            button can cause a new button to appear under the cursor. For example
            mserve has four buttons for scrolling status.
            
            Manual to Auto tooltip is blue background of album.
            Auto to Manual tooltip is white background from when mserve started.

            When clicking on button we want tooltip display to be cancelled. Most
            notable when hamburger button invokes dropdown menu and tooltip displays
            a second later.
            
            The leave event is being recorded and tooltip still pops up for 10 seconds
            in rare circumstances. Can poll_tips() be modified to search all? 

        '''
        self.tooltip = None
        self.pool = None

    def register_tooltip(self, tooltip, pool=None):
        """ June 15 2023 - Appears to be unused """
        self.tooltip = tooltip
        self.pool = pool

    def update_colors(self, button_color, text_color):
        """ Called from play_ffmpeg_artwork() when new song starts """
        self.itemconfig("button_color", fill=button_color, outline=button_color)
        self.itemconfig("text_color", fill=text_color)

    def lift(self, aboveThis=None):
        """ Deal with bug in tkinter raising canvas window:
            https://stackoverflow.com/a/55559387/6929343
        """
        self.tk.call('raise', self._w, aboveThis)


def canvas_text_bbox_size(text, ms_font):
    """ Calculate width and height of canvas text)
        From: 3https://stackoverflow.com/a/19971213/692934
    """
    scratch = tk.Canvas()
    sample = scratch.create_text((0, 0), text=text, font=ms_font)
    x0, y0, x1, y1 = scratch.bbox(sample)
    #print('_x0, _y0, x1, y1:', x0, y0, x1, y1)
    #width = x1 - x0
    #height = y1 - y0
    #print('width, height:', width, height)
    return x1 - x0, y1 - y0   # x1 = width, y1 = height


class GoneFishing:
    """ Transform music player into shark silhouette that goes fishing for man

        The man is on target window which music player gobbles up when TV Break
        is clicked.

        When music count down timer is done the windows are restored.

        Optionally no sound from target window can invoke GoneFishing and sound
        presence can restore windows.

        NOTE: Beginning of __init__ code copied from mmm mainline. mmm needs
              upgrading to take advantage of classes.

        TODO: 

    wmctrl -lG
        
    0x00a00007  0 2621 491  643  175  alien Ubuntu
    0x02c00002 -1 5355 24   410  1392 alien conky (alien)
    0x03800002  0 -5890 -3340 5790 3240 alien XdndCollectionWindowImp
    0x03800009  0 -165 -1156 65   1056 alien unity-launcher
    0x0380001e  0 0    0    1920 24   alien unity-panel
    0x03800025  0 1920 0    3840 24   alien unity-panel
    0x03800033  0 -420 -300 320  200  alien unity-dash
    0x03800034  0 -420 -300 320  200  alien Hud
F   0x03400003  0 5966 6660 1742 884  alien ffprobe preserve last access time - Google Search — Mozilla Firefox
    0x03400021  0 24   296  1890 774  alien Subscriptions - YouTube — Mozilla Firefox
    0x03a0000a  0 0    0    5790 3240 alien Desktop
    0x04e0000a  0 2330 3345 1300 874  alien Python 3
    0x04e00115  0 3500 128  1300 874  alien mserve
F   0x0480004d  0 6327 3424 1377 855  alien website – mserve.md
    0x04800054  0 2719 620  1657 1495 alien mserve – ~/python/mserve.py
T   0x04e0158e  0 5827 6664 1300 874  alien rick@alien: ~
P   0x03a01399  0 5895 6553 1268 672  alien programs
    0x05600036  0 1969 324  1447 810    N/A Multiple Monitors Manager - mmm
    0x038002e8  0 3870 2160 1920 24   alien unity-panel

F = Firefox
T = Gnome Terminal
P = PyCharm

    """

    def __init__(self, parent, ms_font=(None, WIN_FONTSIZE * 4)):

        self.src_toplevel = parent          # mserve play_top
        self.shark_pid = None
        self.man_pid = None
        self.src_cover_top = None
        self.src_window_moved = None
        self.trg_was_above = None
        self.src_was_below = None
        self.place_in_plugins = False

        # geometry of target window - Do this first to ensure window exists!
        self.trg_window_id_hex, trg_geom = self.trg_get_window_id()
        if self.trg_window_id_hex is None:
            # No target window, tell functions there is no shark window
            self.shark_window_id_dec = None     # plot_move() and shark_move()
            print("No target window to go fishing on. Needed at x,y coordinates 0,0")
            return

        self.src_cover_top = None           # Gone Fishing placeholder window
        self.shark_gtk_win = None           # Gtk Window object
        self.trg_toplevel = None            # Falling man silhouette window
        self.trg_was_maximized = None       # Check these states and restore
        self.trg_was_above = None           # when GoneFishing closes
        self.toggle_str = ""                # Full screen indicator
        self.src_was_below = None           # when GoneFishing closes

        self.move_steps = None              # How many steps (x+y) to move
        self.step_value = None              # How much x & y is stepped by
        self.curr_x = None                  # Current x position
        self.curr_y = None                  # Current y position
        self.on_x_axis = None               # Are we traversing x-axis?
        self.on_y_axis = None               # Are we traversing y-axis?
        self.direction_x = None             # 'left' or 'right' movement
        self.direction_y = None             # 'up' or 'down' movement (first)
        self.src_window_moved = None        # Is source window overtop target?
        self.old_compiz_plugins = self.get_gsettings()
        self.place_in_plugins = False       # Compiz doesn't contain: 'place',

        self.src_wm_window = self.src_x11_window = x11.get_active_window()
        self.src_window_id_dec = self.src_x11_window.id
        self.src_window_id_hex = hex(self.src_window_id_dec)
        # self.src_geom way different than used in bserve.py - confirm
        self.src_geom = namedtuple('src_geom', 'x y w h')
        self.src_geom = x11.get_absolute_geometry(self.src_wm_window)
        # self.all_x11_windows = x11.build_windows_list()

        # Use monitor function that compensates for window decoration
        self.src_x, self.src_y, self.src_w, self.src_h = \
            monitor.get_window_geom_raw(self.src_toplevel)
        src_geom = (self.src_x, self.src_y, self.src_w, self.src_h)
        # Using X lib to get geom....
        self.src_wm_window_geom = self.src_wm_window.get_geometry()

        ''' Take screenshot of Source Window (play_top)
        '''
        self.src_img = x11.screenshot(self.src_geom.x, self.src_geom.y,
                                      self.src_geom.width, self.src_geom.height)

        # Place holder for old play top window with "Gone Fishing" text splash
        self.src_cover_top = tk.Tk()  # July 23, 2201 - Should test tk.Toplevel()
        self.src_cover_top.title("TV Break - mserve")
        self.src_cover_top.grid_columnconfigure(0, weight=1)
        self.src_cover_top.grid_rowconfigure(0, weight=1)

        ''' TODO: Put screenshot image into source cover '''
        #self.src_window_id_hex = monitor.wm_get_active_window()
        #print(self.src_cover_top.put_pil_image())

        # create and pack the canvas. Then load image file
        #canvas = tk.Canvas(self.src_cover_top, width=self.src_w,
        #                   height=self.src_h, bg='black')
        #canvas.pack(expand=tk.YES, fill=tk.BOTH)
        #canvas.create_image(0, 0, image=?, anchor=tk.NW)

        src_frame = tk.Frame(self.src_cover_top, bg="black",
                             width=self.src_w, height=self.src_h)
        src_frame.grid(column=0, row=0, sticky=tk.NSEW)
        src_frame.grid_columnconfigure(0, weight=1)
        src_frame.grid_rowconfigure(0, weight=1)

        src_label = tk.Label(src_frame, text="Gone Fishing", fg="red",
                             bg="black", font=ms_font)
        src_label.grid(column=0, row=0, sticky=tk.NSEW)
        src_label.grid_columnconfigure(0, weight=1)
        src_label.grid_rowconfigure(0, weight=1)

        self.src_cover_top.wait_visibility()
        self.src_cover_top.attributes("-alpha", .75)
        self.src_cover_top.withdraw()
        self.src_cover_top.update_idletasks()
        self.src_cover_top.geometry('{}x{}+{}+{}'.format(
            self.src_w, self.src_h, self.src_x, self.src_y))
        self.src_cover_top.deiconify()  # Forces window to appear
        self.src_cover_top.update()  # This is required for visibility

        # Apply shark silhouette - based on: m_circle_splash_image
        # TODO: Shark is facing left. If Man to right, flip horizontally.
        #shark_img = Image.open('shark.png').convert('L').resize(self.src_img.size)
        shark_img = Image.open('shark.png').convert('L').resize(
            (self.src_geom.width, self.src_geom.height))

        # Invert black & transparent:
        # https://note.nkmk.me/en/python-pillow-invert/
        shark_img_invert = ImageOps.invert(shark_img)

        # https://note.nkmk.me/en/python-pillow-putalpha/
        #shark_blur = shark_img_invert.filter(ImageFilter.GaussianBlur(4))
        shark_blur = shark_img_invert      # Alternate with clean edges

        # Blend raw image and silhouette
        self.src_img.putalpha(shark_blur)
        self.src_img.save("shark_alpha.png")

        # At this point make window undecorated, don't do it sooner!
        # From: https://stackoverflow.com/a/37199655/6929343
        #self.src_cover_top.overrideredirect(True)  # Remove self.src_cover_top window close button

        # Mount the shark with transparent layer
        fudge_x = str(src_geom[0] + 14)
        fudge_y = str(src_geom[1] + 24)
        # fudge_x = str(src_geom[0])
        # fudge_y = str(src_geom[1])
        shark_alpha_name = " shark_alpha.png"
        ext_name = 'pqiv -c -i -P ' + fudge_x + ',' + fudge_y +\
                   " " + shark_alpha_name

        # Place the shark over source window and get it's PID
        ''' Need option to wait for GUI window to open! '''
        self.shark_pid = ext.launch_command(ext_name, self.src_toplevel)

        #ext.t_init('x11.build_windows_list')
        #win_list = x11.build_windows_list()     # 10 times faster than "wmctrl -l"
        #print('win_list:', win_list)
        #ext.t_end('print')

        self.shark_window_id_dec = \
            x11.wait_visible_name('pqiv:' + shark_alpha_name, self.src_toplevel, 33, 100)

        if self.shark_window_id_dec is None:
            print('Waited ' + str(33 * 100 / 1000) + ' seconds but no shark appeared')
            return

        # geometry of target window - Already obtained at top of init using:
        self.trg_window_id_hex, trg_geom = self.trg_get_window_id()
        # print('trg_window_id_hex:', self.trg_window_id_hex, 'trg_geom:', trg_geom)
        self.trg_x = trg_geom[0]  # x
        self.trg_y = trg_geom[1]  # y
        self.trg_w = trg_geom[2]  # width
        self.trg_h = trg_geom[3]  # height

        self.man_window_id = None           # xdotool decimal format

        # self.win_remove_above()  # Changed April 30, 2023

        self.trg_was_above = None
        self.trg_check_full_screen()
        """  The target window can stay maximized for undecorated windows only. We need to get
             "always on top" (above) state, Maximized Vertically and Maximized Horizontally
              states.

              Sets         self.trg_was_above = True
        """

        self.src_window_id_hex = hex(self.src_window_id_dec)
        self.src_was_below = self.win_remove_below(self.src_window_id_hex)

        ''' Next code Was BELOW about 20 lines '''
        # Mount the shark with transparent layer
        ''' TODO: Center man on screen '''
        fudge_x = str(trg_geom[0] + 450)
        fudge_y = str(trg_geom[1] + 200)
        ext_name = 'pqiv -c -c -i -P ' + fudge_x + ',' + fudge_y +\
                   ' "man falling.png"'
        #print('ext_name:', ext_name)

        # Place the "man falling" over target window and get it's PID
        self.man_pid = ext.launch_command(ext_name, self.trg_toplevel)


    @staticmethod
    def get_gsettings():
        """ Find out if 'place', is in Compiz plug ins list """
        settings = os.popen(
            'gsettings get org.compiz.core:/org/compiz/profiles/unity/plugins/core/' +
            ' active-plugins').read().strip()
        # print('self.old_compiz_plugins:', settings)
        return settings

    @staticmethod
    def set_gsettings(settings):
        """ set Compiz plug ins list. Don't use read() function which waits until
            job finishes.
        """
        os.popen(
            'gsettings set org.compiz.core:/org/compiz/profiles/unity/plugins/core/' +
            ' active-plugins ' + '"' + settings + '"')


    def plot_move(self, iterations):
        """ How much to move window each step depends on:
            distance / duration / interval

            Float up or sink down along x-axis until on same y-axis as target.
            Then move along y-axis to gobble up target

            Move center of shark to center of man.
        """
        if self.shark_window_id_dec is None:
            return  # Failsafe

        if self.src_x > self.trg_x:
            step_x = self.src_x - self.trg_x
            self.direction_x = 'left'
        else:
            step_x = self.trg_x - self.src_x
            self.direction_x = 'right'

        if self.src_y > self.trg_y:
            step_y = self.src_y - self.trg_y
            self.direction_y = 'up'
        else:
            step_y = self.trg_y - self.src_y
            self.direction_x = 'down'

        # TODO: What if x or y are on same axis? Then step_x or step_y would be 0.
        self.move_steps = step_x + step_y
        self.step_value = self.move_steps / iterations
        self.curr_x = self.src_x
        self.curr_y = self.src_y
        self.on_x_axis = False
        self.on_y_axis = True
        # print('steps:', self.move_steps, 'step_value:', self.step_value,
        #      'x:', self.curr_x, self.direction_x, step_x, 'to:', self.trg_x,
        #      'y:', self.curr_y, self.direction_y, step_y, 'to:', self.trg_y)

        # Removing "place" from gsettings allows smooth shark movement over
        # monitors. However there are screen resets with disappearing windows
        # for a couple seconds from time to time. Keeping "place" has shark
        # stop at monitor border then "jump" into the next monitor.
        '''
        if "'place', " in self.old_compiz_plugins:
            self.place_in_plugins = True
            override = self.old_compiz_plugins.replace("'place', ", '')
            #print('override:', override)
            self.set_gsettings(override)
        '''

    def shark_move(self):
        """ How much to move window each step depends on:
            distance / duration / interval

            Float up or sink down along x-axis until on same y-axis as target.
            Then move along y-axis to gobble up target

            Move center of shark to center of man.
        """
        if self.shark_window_id_dec is None:
            print("image.py GoneFishing.shark_move() shark_window_id_dec is None")
            # June 10, 2023 - Gazillion error messages for above
            return  # Failsafe

        if not self.on_y_axis and not self.on_x_axis:
            if self.shark_pid is not None:
                # Remove shark and falling man windows. Move play_top
                self.move_src_toplevel()
            return              # Plot moving is finished

        if self.on_y_axis is True:
            if self.direction_y is 'up':
                # We are going 'up' so subtract from y-axis
                self.curr_y -= self.step_value
                if self.curr_y <= self.trg_y:
                    self.curr_y = self.trg_y
            else:
                # We are going 'down' so add to y-axis
                self.curr_y += self.step_value
                if self.curr_y >= self.trg_y:
                    self.curr_y = self.trg_y

        if self.on_x_axis is True:
            if self.direction_x is 'left':
                # We are going 'left' so subtract from x-axis
                self.curr_x -= self.step_value
                if self.curr_x <= self.trg_x:
                    self.curr_x = self.trg_x
            else:
                # We are going 'right' so add to x-axis
                self.curr_x += self.step_value
                if self.curr_x >= self.trg_x:
                    self.curr_x = self.trg_x


        # Final attempt using X11 to move window
        ''' Switch to X11 because xdotool jumps across monitors after lag
            But wmctrl same but worse by lagging on a the same monitor even.
            
            FINAL SOLUTION: Install CompizConfig Settings Manager and remove the
                            "Place Windows" checkbox.  

            FINAL FINAL SOLUTION (4 second lag though). Notice 'place' follows 'move' below:

            $ gsettings get org.compiz.core:/org/compiz/profiles/unity/plugins/core/ active-plugins
            ['core', 'composite', 'opengl', 'regex', 'mousepoll', 'animation',
             'wall', 'vpswitch', 'session', 'snap', 'workarounds',
             'compiztoolbox', 'imgpng', 'resize', 'move', 'expo', 'fade',
             'ezoom', 'scale', 'switcher', 'unityshell']

            $ gsettings set org.compiz.core:/org/compiz/profiles/unity/plugins/core/ active-plugins 
            "['core', 'composite', 'opengl', 'regex', 'mousepoll', 'animation',
              'wall', 'vpswitch', 'session', 'snap', 'workarounds',
              'compiztoolbox', 'imgpng', 'resize', 'move', 'place', 'expo', 'fade',
              'ezoom', 'scale', 'switcher', 'unityshell']"

            $ gsettings get org.compiz.core:/org/compiz/profiles/unity/plugins/core/ active-plugins
            ['core', 'composite', 'opengl', 'regex', 'mousepoll', 'animation',
             'wall', 'vpswitch', 'snap', 'workarounds', 
             'compiztoolbox', 'imgpng', 'resize', 'move', 'place', 'expo', 'fade',
             'session', 'ezoom', 'scale', 'switcher', 'unityshell']
             
No PLACE one-liner:
gsettings set org.compiz.core:/org/compiz/profiles/unity/plugins/core/ 
active-plugins "['core', 'composite', 'opengl', 'regex', 'mousepoll', 
'animation', 'wall', 'vpswitch', 'session', 'snap', 'workarounds', 
'compiztoolbox', 'imgpng', 'resize', 'move', 'expo', 'fade', 
'ezoom', 'scale', 'switcher', 'unityshell']"

Restore PLACE one-liner:
gsettings set org.compiz.core:/org/compiz/profiles/unity/plugins/core/ 
active-plugins "['core', 'composite', 'opengl', 'regex', 'mousepoll', 
'animation', 'wall', 'vpswitch', 'session', 'snap', 'workarounds', 
'compiztoolbox', 'imgpng', 'resize', 'move', 'place', 'expo', 'fade', 
'ezoom', 'scale', 'switcher', 'unityshell']"

        '''

        self.x11_move_window(self.shark_window_id_dec, self.curr_x, self.curr_y,
                             self.src_w, self.src_h)

        # Set for next iteration
        if self.on_x_axis:
            if self.curr_x == self.trg_x:
                self.on_x_axis = False

        if self.on_y_axis:
            if self.curr_y == self.trg_y:
                self.on_y_axis = False
                self.on_x_axis = True

        return self.on_y_axis, self.on_x_axis


    def move_src_toplevel(self):
        """ Move source toplevel (self.play_top) over target window.
            At this time shark has finished eating man.
        """
        self.close(full_close=False)    # Close the shark & man only

        self.src_toplevel.geometry('+{}+{}'.
                                   format(self.trg_x, self.trg_y))
        #self.src_toplevel.overrideredirect(1)    # Turn off decorations
        _mon_dict = monitor.center(self.src_toplevel)
        self.src_toplevel.deiconify()  # Forces window to appear
        self.src_toplevel.update_idletasks()
        self.src_window_moved = True

        # TODO: raise self.src_toplevel above full screen somehow
        if self.place_in_plugins:
            self.set_gsettings(self.old_compiz_plugins)  # Old is restored twice
            self.place_in_plugins = False


    @staticmethod
    def x11_move_window(window_id_dec, x, y, width, height):
        """ Use x11 library to move window From:
            https://gist.github.com/chipolux/13963019c6ca4a2fed348a36c17e1277
        """

        import Xlib.display

        d = Xlib.display.Display()
        window = d.create_resource_object('window', window_id_dec)
        window.configure(x=x, y=y, width=width, height=height, border_width=0,
                         stack_mode=Xlib.X.Above)
        d.sync()

    @staticmethod
    def trg_get_window_id():
        """  TEMPORARY: Largest window on monitor at 0,0 is the target window.

            TODO: Get desktop size EG 5760x3240 and skip this as a window
                  Get all monitors and their mapping x,y,w,h
                  Let user specify monitor as big screen TV. Currently 0,0

            OUTPUT NON-FULL SCREEN AND ON TOP:
                $ wmctrl -lG
                0x03200002 -1 5355 24   410  1392 alien conky (alien)
                0x0180000a -1 0    0    5790 3240 alien Desktop
                0x03a00003  0 3940 2269 1742 941  alien Mozilla Firefox
                0x03a00021  0 78   110  1773 970  alien Subscriptions - YouTube — Mozilla Firefox

            OUTPUT FULL SCREEN NOT ON TOP:
                0x03a00021  0 0    24   1920 1056 alien Subscriptions - YouTube — Mozilla Firefox

            OUTPUT FULL SCREEN ON TOP:
                0x03a00021  0 0    24   1920 1056 alien Subscriptions - YouTube — Mozilla Firefox

            ENTIRE DESKTOP:
                $ wmctrl -lGd
                0  * DG: 5790x3240  VP: 0,0  WA: 0,24 5790x3216  N/A

        """

        all_windows = os.popen('wmctrl -lG').read().strip().splitlines()
        # print('all_windows:', len(all_windows), all_windows)
        last_window = None
        last_geom = None
        for window in all_windows:
            try:
                wid = window.split()[0]
                geom = list(map(int, window.split()[2:6]))
                # print('wid:', wid, 'geom:', geom)
            except IndexError:
                print('Need .strip() after read(). window.split() failed on:', window)
                continue  # Loop to next window

            # Compare x (0) and y (1) to boundaries
            if geom[0] > 1920 or geom[1] > 1080:
                continue    # x, y - Not on screen

            if geom[0] < 0 or geom[1] < 0:
                continue    # x, y - Hidden panel or HUD

            # Compare width (2) and height (3) to boundaries
            if geom[2] > 1920 or geom[3] > 1080:
                continue  # Too large for screen, it's entire desktop

            if geom[2] < 200 or geom[3] < 200:
                continue  # Too small for window, it's the panel

            if last_geom:
                # Compare width (2) and height (3) to last saved window
                if geom[2] < last_geom[2] or geom[3] < last_geom[3]:
                    continue  # smaller width or smaller height so skip it.

            last_geom = geom
            last_window = wid

        return last_window, last_geom

    def win_remove_above(self):
        """  If window 'above' (Always on Top in Ubuntu-speak) toggle it off.
             Note: _NET_WM_STATE_FULLSCREEN could be checked but is not yet...
             
             No Longer used but keep just in case...
        """
        self.trg_was_above = None
        all_lines = os.popen('xprop -id ' + self.trg_window_id_hex).\
            read().strip().splitlines()
        print("\nimage.py GoneFishing.win_remove_above() all_lines:")
        for line in all_lines:
            print(line)
            if "_NET_WM_STATE(ATOM)" in line:
                # print('line:', line)
                if "ABOVE" in line:
                    self.trg_was_above = True
                    #print('if "ABOVE" in line:', self.trg_was_above)
                    os.popen('wmctrl -ir ' + self.trg_window_id_hex +
                             ' -b toggle,above')
                break

    def trg_restore_above(self):
        """  Revert the "always on top" (above) state.

             No longer used. Keep just in case...
        """
        if self.trg_was_above is True:
            os.popen('wmctrl -ir ' + self.trg_window_id_hex +
                     ' -b toggle,above')

        self.trg_was_above = None

    @staticmethod
    def win_remove_below(win_hex):
        """  If the source window was below (probably always) make it above the
             TV broadcast
        """
        was_below = None
        all_lines = os.popen('xprop -id ' + win_hex).read().strip().splitlines()
        for line in all_lines:
            if "_NET_WM_STATE(ATOM)" in line:
                # print('line:', line)
                if "ABOVE" not in line:
                    was_below = True
                    os.popen('wmctrl -ir ' + win_hex + ' -b toggle,above')
                break

        return was_below

    def src_restore_below(self):
        """  Revert the below state.
        """
        if self.src_was_below is True:
            os.popen('wmctrl -ir ' + self.src_window_id_hex +
                     ' -b toggle,above')

        self.src_was_below = None

    def trg_check_full_screen(self):
        """  The target window can stay maximized for undecorated windows only. We need to get
             "always on top" (above) state, Maximized Vertically and Maximized Horizontally
              states.

        NOT USED - Because taking out of full screen brings up chat window for hockey game.

        Change mind - CBC doesn't have chat window and stays in full screen on top.
                      YouTube doesn't work coming out of full screen either.
        SAMPLE:
        _NET_WM_USER_TIME(CARDINAL) = 293540101
        GDK_TIMESTAMP_PROP(GDK_TIMESTAMP_PROP) = 0x61
        _NET_WM_ICON_GEOMETRY(CARDINAL) = 3875, 2543, 54, 54
        _NET_FRAME_EXTENTS(CARDINAL) = 0, 0, 0, 0
        WM_STATE(WM_STATE):
                window state: Normal
                icon window: 0x0
        _NET_WM_DESKTOP(CARDINAL) = 0
        _NET_WM_STATE(ATOM) = _NET_WM_STATE_FULLSCREEN
        WM_HINTS(WM_HINTS):
                Client accepts input or input focus: True
                Initial state is Normal State.
                bitmap id # to use for icon: 0x3201c91
                bitmap id # of mask for icon: 0x3201c97
                window id # of group leader: 0x3200001
        _NET_WM_ALLOWED_ACTIONS(ATOM) = _NET_WM_ACTION_MOVE, _NET_WM_ACTION_RESIZE, _NET_WM_ACTION_STICK, _NET_WM_ACTION_MINIMIZE, _NET_WM_ACTION_MAXIMIZE_HORZ, _NET_WM_ACTION_MAXIMIZE_VERT, _NET_WM_ACTION_FULLSCREEN, _NET_WM_ACTION_CLOSE, _NET_WM_ACTION_CHANGE_DESKTOP, _NET_WM_ACTION_ABOVE, _NET_WM_ACTION_BELOW
        WM_WINDOW_ROLE(STRING) = "browser"
        _NET_WM_BYPASS_COMPOSITOR(CARDINAL) = 2
        XdndAware(ATOM) = BITMAP
        _GTK_MENUBAR_OBJECT_PATH(UTF8_STRING) = "/com/canonical/unity/gtk/window/2"
        _UNITY_OBJECT_PATH(UTF8_STRING) = "/com/canonical/unity/gtk/window/2"
        _GTK_UNIQUE_BUS_NAME(UTF8_STRING) = ":1.67"
        _NET_WM_ICON(CARDINAL) = 	Icon (64 x 64):

            ( LOTS OF HUGE ICONS SHOW UP IN TERMINAL )

        _NET_WM_OPAQUE_REGION(CARDINAL) = 0, 0, 1920, 1080
        _NET_WM_WINDOW_TYPE(ATOM) = _NET_WM_WINDOW_TYPE_NORMAL
        _NET_WM_SYNC_REQUEST_COUNTER(CARDINAL) = 52428837, 52428838
        _NET_WM_USER_TIME_WINDOW(WINDOW): window id # 0x3200024
        WM_CLIENT_LEADER(WINDOW): window id # 0x3200001
        _NET_WM_PID(CARDINAL) = 2925
        WM_LOCALE_NAME(STRING) = "en_CA.UTF-8"
        WM_CLIENT_MACHINE(STRING) = "alien"
        WM_NORMAL_HINTS(WM_SIZE_HINTS):
                program specified location: 0, 0
                program specified minimum size: 675 by 143
                program specified maximum size: 16384 by 16384
                program specified base size: 675 by 143
                window gravity: NorthWest
        WM_PROTOCOLS(ATOM): protocols  WM_DELETE_WINDOW, WM_TAKE_FOCUS, _NET_WM_PING, _NET_WM_SYNC_REQUEST
        WM_CLASS(STRING) = "Navigator", "Firefox"
        WM_ICON_NAME(COMPOUND_TEXT) = "After Bakhmut, Is Russia Still Advancing? Col Daniel Davis - YouTube — Mozilla Firefox"
        _NET_WM_ICON_NAME(UTF8_STRING) = "After Bakhmut, Is Russia Still Advancing? Col Daniel Davis - YouTube — Mozilla Firefox"
        WM_NAME(COMPOUND_TEXT) = "After Bakhmut, Is Russia Still Advancing? Col Daniel Davis - YouTube — Mozilla Firefox"
        _NET_WM_NAME(UTF8_STRING) = "After Bakhmut, Is Russia Still Advancing? Col Daniel Davis - YouTube — Mozilla Firefox"

        """

        self.trg_was_above = None
        self.toggle_str = ""
        all_lines = os.popen('xprop -id ' + self.trg_window_id_hex).read().strip().splitlines()
        #print("image.py GoneFishing.trg_check_full_screen() line with FULL SCREEN:")
        for line in all_lines:
            if "_NET_WM_STATE(ATOM)" in line:
                if "ABOVE" in line:
                    self.toggle_str += ",above"
                #if "_NET_WM_STATE_FOCUSED" in line:
                #    self.toggle_str += ",focused"  # Added May 24, 2023
                if '_NET_WM_STATE_MAXIMIZED_VERT' in line:
                    self.toggle_str += ",maximized_vert"
                if '_NET_WM_STATE_MAXIMIZED_HORZ' in line:
                    self.toggle_str += ",maximized_horz"
                if '_NET_WM_STATE_FULLSCREEN' in line:
                    self.toggle_str += ",fullscreen"
                    #print('line:', line)

                if self.toggle_str != "":
                    res = os.popen('wmctrl -ir ' + self.trg_window_id_hex +
                                   ' -b toggle' + self.toggle_str).read()
                    self.trg_was_above = True
                    if res is not None and res != "":
                        print("os.popen('wmctrl -ir " + self.trg_window_id_hex +
                              " -b toggle" + self.toggle_str + ")  res:", res,
                              "len(res):", len(res), "type:", type(res))
                break

    def trg_restore_full_screen(self):
        """  Revert the "always on top" (above) state.
        """
        if self.trg_was_above is True:
            res = os.popen('wmctrl -ir ' + self.trg_window_id_hex +
                           ' -b toggle' + self.toggle_str).read()
            if res is not None and res != "":
                print("os.popen('wmctrl -ir " + self.trg_window_id_hex +
                      " -b toggle" + self.toggle_str + ")  res:", res)

        self.trg_was_above = None

    def close(self, full_close=True):
        """ Put music player back where it was.
            Restore above state for big screen

            TODO: We need two close options, one for most excluding source
                  over target, the other for closing all
        """
        #print('gone_fishing.curr_x:', gone_fishing.curr_x,
        #      '.curr_y:', gone_fishing.curr_y)
        # Kill the shark image transparent window
        if self.shark_pid is not None:
            ext.kill_pid_running(self.shark_pid)
            self.shark_pid = None

        # Kill the man falling image transparent window
        if self.man_pid is not None:
            ext.kill_pid_running(self.man_pid)
            self.man_pid = None

        if full_close is False:
            ''' Called from move_src_toplevel() close man & shark only. '''
            return

        ''' We were NOT called from move_src_toplevel() so FULL close '''
        # Destroy top level window covering up old music player position
        if self.src_cover_top is not None:
            self.src_cover_top.destroy()
            self.src_cover_top = None

        if self.src_window_moved is not None:
            try:
                #self.src_toplevel.overrideredirect(0)  # Turn on decorations
                # Messing up restore?
                self.src_toplevel.geometry(
                    '{}x{}+{}+{}'.format(self.src_w, self.src_h, self.src_x, self.src_y))
            finally:
                self.src_window_moved = None

        # Restore original target's above (always on top) state
        if self.trg_was_above is not None:
            self.trg_restore_full_screen()

        # Restore original source's below (normal) state
        if self.src_was_below is not None:
            self.src_restore_below()

        # Restore g settings
        if self.place_in_plugins:
            self.set_gsettings(self.old_compiz_plugins)  # Old is restored twice
            self.place_in_plugins = False

    @staticmethod
    def refresh_gtk():
        # Doesn't seem to work as static:
        #   global name 'refresh_gtk' is not defined
        while Gtk.events_pending():
            Gtk.main_iteration()


def gtk_screenshot(x, y, width, height):
    """ Take screenshot of Screen region x, y, w, h
        returns photo image
    """
    import gi
    gi.require_version('Gdk', '3.0')
    gi.require_version('Gtk', '3.0')
    gi.require_version('Wnck', '3.0')

    # gi.require_versions({"Gtk": "3.0", "Gdk": "3.0", "Wnck": "3.0"}) # Python 3

    from gi.repository import Gdk, GdkPixbuf, Gtk, Wnck

    Gdk.threads_init()  # From: https://stackoverflow.com/questions/15728170/

    def refresh_gtk():
        while Gtk.events_pending():
            Gtk.main_iteration()

    refresh_gtk()
    wnck_screen = Wnck.Screen.get_default()
    wnck_screen.force_update()

    root_window = Gdk.get_default_root_window()

    # pb = Gdk.pixbuf_get_from_window(root_window, *src_geom)
    pb = Gdk.pixbuf_get_from_window(root_window, x,
        y, width, height)
    win_pixels = pb.read_pixel_bytes().get_data()  # Screenshot source
    #src_img = Image.frombytes('RGB', (src_geom[2], src_geom[3]), win_pixels,
    src_img = Image.frombytes('RGB', (width, height), win_pixels,
                              'raw', 'RGB', pb.get_rowstride(), 1)

    return src_img


def create_text(x1, y1, **kwargs):
    """ From mmm:

    for i in range (monitors_cnt):
        monitor = monitors[i * MON_CNT : i * MON_CNT + MON_CNT ]
        # Calculate positions for this monitor
        x1, y1, x2, y2 = scale_dtop (monitor[MON_X], monitor[MON_Y], \
                                     monitor[MON_W], monitor[MON_H])[0:4]
        # Rectangle left, top, right, bottom
        create_rectangle(x1, y1, x2, y2, wallpaper=i)
        # Shadow text colors
        InvertColor="white"
        ShadowColor="black"
        create_text(x1, y1 + PANEL_HGT/SCALE, text"stuff", fill=InvertColor, \
                     shadow_fill=ShadowColor, thick=2, \
                     anchor="nw", font=(None, MON_FONTSIZE))


    """
    if 'thick' in kwargs:
        thick = kwargs.pop('thick')
        if thick > 5 : thick = 0
    else :
        thick = 0

    if 'shadow_fill' in kwargs:
        shadow_fill = kwargs.pop('shadow_fill')
    else:
        mycanvas.create_text(x1, y1, **kwargs)
        return

    if 'fill' in kwargs:
        fill = kwargs.pop('fill')
    else:
        fill = "black"

    x = x1 + 1 + thick
    y = y1 + 1 + thick
    if thick > 1:
        thick_less = thick - 1
    else:
        thick_less = 1

    while thick_less > 0:
        mycanvas.create_text(x-thick_less, y+thick, fill=shadow_fill, **kwargs)
        mycanvas.create_text(x+thick_less, y+thick, fill=shadow_fill, **kwargs)
        mycanvas.create_text(x-thick, y-thick_less, fill=shadow_fill, **kwargs)
        mycanvas.create_text(x+thick, y+thick_less, fill=shadow_fill, **kwargs)
        thick_less -= 1
        thick -= 1

    mycanvas.create_text(x, y, fill=fill, **kwargs)

# End of image.py
