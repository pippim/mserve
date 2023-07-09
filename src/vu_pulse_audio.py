#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ==============================================================================
#
#       vu_pulse_audio.py - Manage audio sinks and set volume
#
#       July 07 2023 - Enhance code converted from mserve.py
#
# ==============================================================================
"""

NOTE: Use pavucontrol to create loopback from sound output to microphone:
      https://wiki.ubuntu.com/record_system_sound - Required by vu_meter.py
      Keep an eye open if vu_meter.py can be made more robust.

"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

import global_variables as g

if g.USER is None:
    print('vu_pulse_audio.py was forced to run g.init()')
    g.init()

try:  # Python 3
    import tkinter as tk
    import tkinter.ttk as ttk
    import tkinter.font as font
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
    import tkinter.simpledialog as simpledialog
    import tkinter.scrolledtext as scrolledtext
    PYTHON_VER = "3"

except ImportError:  # Python 2
    import Tkinter as tk
    import ttk
    import tkFont as font
    import tkFileDialog as filedialog
    import tkMessageBox as messagebox
    import tkSimpleDialog as simpledialog
    import ScrolledText as scrolledtext
    PYTHON_VER = "2"

import os
import time
from collections import OrderedDict, namedtuple

# Subdirectory /pulsectl under directory where mserve.py located
from pulsectl import pulsectl

# Pippim modules
import external as ext
import timefmt as tmf
import toolkit


class PulseAudio:
    """ Manage list of dictionaries created from Pulse Audio information.
        self.pav = PulseAudio()
        self.pav.find(pid) - blocking function that finds new sink 1 second limit
        self.pav.get_all_sinks() - Returns list of tuples [ (), ()... ]

        self.pav.add(sink)
        self.pav.remove(sink)
    """

    def __init__(self, Info=None):
        self.info = Info  # Can also use: self.registerInfoCentre() to set
        self.pulse_is_working = True
        try:
            ext.t_init("pulse = pulsectl.Pulse()")
            self.pulse = pulsectl.Pulse()
            # print("pulse:", dir(pulse))
            ext.t_end('no_print')  # 0.0037407875

        except Exception as p_err:  # CallError, socket.error, IOError (pidfile), OSError (os.kill)
            self.pulse_is_working = False
            raise pulsectl.PulseError('mserve.py get_pulse_control() Failed to ' +
                                      'connect to pulse {} {}'.format(type(err),
                                                                      err))

        self.sinks_now = None  # used to compare for new sinks showing up
        self.last_sink_input_list = None  # Save .002 to .009 seconds
        self.get_all_sinks()  # saves to self.sinks_now
        self.sinks_at_init = self.sinks_now
        self.spam_count = 0  # Prevent error message flooding
        self.poll_count = 0  # To print first 10 job times to fade 
        self.fade_list = []
        self.dict = {"sink": "",
                          "begin": 0.0,
                          "end": 0.0,
                          "start_time": 0.0,
                          "duration": 0.0
                          }

    def fade(self, sink_no_str, begin, end, duration, finish_cb=None, arg_cb=None):
        """ Add new fade_dict to fade_list
            'finish_cb': is an optional callback when fade cycle is completed
            'arg_cb': is an optional parameter to the optional callback
        """
        now = time.time()
        self.dict['sink_no_str'] = sink_no_str
        self.dict['begin_perc'] = begin
        self.dict['end_perc'] = end
        self.dict['curr_perc'] = begin  # Required for reverse_fade()
        self.dict['start_time'] = now
        self.dict['last_time'] = now  # Just for debugging
        self.dict['duration'] = duration
        self.dict['finish_cb'] = finish_cb  # callback when fade is ALL done
        self.dict['arg_cb'] = arg_cb  # optional argument to callback
        # If sink_no_str is already being faded, reverse it
        self.reverse_fade(sink_no_str)
        # Add new fade job into queue where it will be processed every .033 secs
        self.fade_list.append(self.dict)

    def reverse_fade(self, sink_no_str):
        """ Fade was already started now needs to reverse.
            For example, pause was clicked and fade out started. Then
            1/4 second later play was clicked but only 75% way through the
            1 second fade out. Now need to fade in for 1/4 second from 75%
            volume to 100% volume.

            Previously play_top.update() was delayed until fade finished
            and then next play/pause click was read. Now it will interrupt
            and there can be two fades for the same sink in the list.

            The first think poll() can do is check for duplicate sink_no_str.

            Also the sink objects aren't being saved to the self.sinks_now
        """
        for i, search_dict in enumerate(self.fade_list):
            if search_dict['sink_no_str'] == sink_no_str:
                # Keep everything except duplicate
                self.fade_list = \
                    [x for x in self.fade_list if x['sink_no_str'] != sink_no_str]
                # New beginning percent is where fade left off last time
                self.dict['curr_perc'] = search_dict['curr_perc']
                self.dict['begin_perc'] = search_dict['curr_perc']
                return True
        return False
    
    def poll_fades(self):
        """ Every 33ms (in theory) process next step of fade job
            When finished, set volume to final amount (end_perc)
        """
        ext.t_init('self.pav.poll()')
        now = time.time()
        start_count = len(self.fade_list)
        finished_count = 0

        ''' Process every fade_dict in the fade_list '''
        for i, self.dict in enumerate(self.fade_list):
            if now >= self.dict['start_time'] + self.dict['duration']:
                finished_count += 1
                last_volume = self.get_volume(self.dict['sink_no_str'],
                                              refresh=False)
                self.info.cast(str(last_volume) + self.dict['sink_no_str'] +
                               " finished.")
                self.set_volume(self.dict['sink_no_str'],
                                self.dict['end_perc'])
                self.poll_callback()
                continue  # added on phone

            current_duration = now - self.dict['start_time']
            distance = self.dict['end_perc'] - self.dict['begin_perc']
            adjust = distance * current_duration / self.dict['duration']
            self.dict['curr_perc'] = self.dict['begin_perc'] + adjust
            self.fade_list[i] = self.dict
            job_time, err = \
                self.set_volume(self.dict['sink_no_str'],
                                self.dict['curr_perc'])
            if job_time is None:
                # sink has disappeared
                finished_count += 1
                last_volume = self.get_volume(self.dict['sink_no_str'])
                self.info.cast(str(last_volume) + self.dict['sink_no_str'] +
                               " finished.")
                self.poll_callback()

        # Build new list without completed fades
        self.fade_list = \
            [x for x in self.fade_list if now < x['start_time'] + x['duration']]

        end_count = len(self.fade_list)
        if finished_count != start_count - end_count:
            # self.info should be declared by now but test just to be sure
            if self.info and self.spam_count < 10:
                self.spam_count += 1  # Don't flood with broadcasts
                self.info.cast("vu_pulse_audio.py PulseAudio.poll():" +
                               " finished_count: " + str(finished_count) +
                               " start_count: " + str(start_count) +
                               " end_count: " + str(end_count), 'error')

        poll_time = ext.t_end('no_print')
        if finished_count and self.poll_count < 10:
            self.poll_count += 1
            print("self.pav.poll() poll_time: ", poll_time)

    def poll_callback(self):
        """ fade has finished. Now call 'stop' or 'kill' or whatever. """
        if self.dict['finish_cb'] is not None:
            if self.dict['arg_cb'] is not None:
                # Call function name with argument (probably pid)
                self.dict['finish_cb'](self.dict['arg_cb'])
            else:
                self.dict['finish_cb']()  # Call function name without arg.

    def get_volume(self, sink_no_str, refresh=True):
        """ Uses self.sinks_now which was set the last time that
            self.get_all_sinks(get_new_sink_input_list=True) was run.
            If the last time it was run "get_new_sink_input_list=False"
            was used it should have been less than .001 second ago.
        """
        who = "vu_pulse_audio.py PulseAudio.set_volume(): "
        if refresh:
            self.get_all_sinks()  # Populates self.sinks_now[]
        for Sink in self.sinks_now:
            if Sink.sink_no_str == sink_no_str:
                return Sink.volume

        self.info.cast(who + "unable to find sink#: " + sink_no_str)
        return None

    def set_volume(self, target_sink, percent):
        """ Set volume and return time required to do it
            Note use: pulse.volume_set_all_chans()
            DO NOT use: volume_change_all_chans() which changes volume by
                        adjustment percentage.
        """
        who = "vu_pulse_audio.py PulseAudio.set_volume(): "
        # print("\n set_volume() -- looking for sink:", target_sink,
        #      "setting volume to:", percent, "%",
        #      "float(percent) / 100.0:", float(percent) / 100.0)
        # If Python pulseaudio is working, use the fast method
        if self.pulse_is_working:
            ''' Fast method using pulse audio direct interface '''
            ext.t_init(who + '-- pulse.volume_change')
            err = None  # No known pulsectl errors have appeared yet
            for sink in self.pulse.sink_input_list():
                if str(sink.index) == target_sink:
                    self.pulse.volume_set_all_chans(sink, float(percent) / 100.0)
                    for i, S in enumerate(self.sinks_now):
                        if S.sink_no_str == target_sink:
                            Replace = namedtuple(
                                'Sink', 'sink_no_str volume name pid user')
                            # tuples immutable so recreate a new one based on old
                            replace = Replace(
                                S.index, int(percent), S.name, S.pid, S.user)
                            self.sinks_now[i] = replace
                    job_time = ext.t_end('no_print')
                    return job_time, err
            ext.t_end('no_print')
            return None, None

        if self.pulse_is_working and self.spam_count < 10:
            self.spam_count += 1  # Limit to 10 errors printed
            if self.spam_count < 10:
                text = who + "pulsectl missing sink: " + target_sink
                print(text)
                if self.info:
                    self.info.cast(text)
                all_sinks = list()
                for sink in pulse.sink_list():
                    all_sinks.append(sink)
                print("all sinks:", all_sinks)
                print("resorting to CLI 'pactl' command")

        ''' Slow method using CLI (command line interface) to pulse audio '''
        # Build command line list for subprocess
        # noinspection PyListCreation
        command_line_list = []
        command_line_list.append("pactl")
        command_line_list.append("set-sink-input-volume")
        command_line_list.append(target_sink)
        command_line_list.append(str(percent) + '%')
        # command_str = " ".join(command_line_list)  # list to printable string
        # print("command_str:", command_str)

        ext.t_init(who + '-- pactl set-sink-input-volume')
        pipe = sp.Popen(command_line_list, stdout=sp.PIPE, stderr=sp.PIPE)
        text, err = pipe.communicate()  # This performs .wait() too
        job_time = ext.t_end('no_print')
        if text:
            print(who + "subprocess:")
            print(text)
        if err:
            self.spam_count += 1  # Limit to 10 errors printed
            if self.spam_count < 10:
                print(who + "standard error of subprocess:")
                print('set_volume() ERROR. sink:', target_sink,
                      'percent:', percent,
                      'job_time:', job_time)
                print('error:', err)
        # if pipe.return_code == 0:                  # Future use
        return job_time, err

    def find(self, pid, toplevel=None):
        """
        Checks every 5 ms for Pulse Audio sink to appear after "ffplay" was
        launched as background task and the PID was discovered.

        :param pid: Linux process ID of "ffplay" instance just started
        :param toplevel: When passed gets .after(sleep) time.
        :return sink: Pulse Audio sink number or None if pid not found
        """

        #print("\nPulse working\n", self.get_all_sinks())
        #self.pulse_is_working = False
        #print("\nPulse NOT working\n", self.get_all_sinks())
        #self.pulse_is_working = True
        for i in range(1000):  # Take 5 seconds maximum
            ext.t_init('PulseAudio.find()')
            self.sinks_now = self.get_all_sinks()
            ext.t_end('no_print')  # When pulse_is_working   : 0.0016
            #                        When pulse isn't working: 0.0093

            for Sink in self.sinks_now:
                if Sink.pid == pid:
                    return str(Sink.sink_no_str)
            if toplevel:
                toplevel.after(5)
            else:
                time.sleep(.005)  # Average is 20 loops = .1 second

    def registerInfoCentre(self, Info):
        self.info = Info
        
    def get_all_sinks(self, get_new_sink_input_list=True):
        """ Get PulseAudio list of all sinks
            Return list of tuples with:
                sink #
                flat volume
                application name
                pid
                user name
                
            April 29, 2023 - app_vol has glitch "0]" for speech-dispatcher
        """

        all_sinks = []  # List of tuples

        # If Python pulseaudio is working, use the fast method
        if self.pulse_is_working:
            if get_new_sink_input_list:
                # Not worth the time saved unless shelling out to CLI below
                ext.t_init('self.pulse.sink_input_list()')
                self.last_sink_input_list = self.pulse.sink_input_list()
                ext.t_end('no_print')  # 0.0001280308 to 0.0008969307
            for sink in self.last_sink_input_list:
                # July 8, 2023 - above was self.pulse.sink_input_list()
                this_volume = str(sink.volume)
                ''' TODO: Test when L-R balance isn't even '''
                # sink.volume = channels = 2, volumes = [100 % 100 %]
                this_volume = this_volume.split('[')[1]
                this_volume = this_volume.split(' ')[0]
                this_volume = this_volume.replace('%', '')
                if this_volume.endswith(']'):
                    # Bug end up with "0]" fixed Bug April 29, 2023
                    this_volume = this_volume[:-1]
                # noinspection SpellCheckingInspection
                '''
                >>> pulse.sink_input_list()[2].proplist
                u'application.name': u'ffplay', 
                u'application.process.id': u'13166', 
                u'application.process.user': u'rick'
                '''

                # create 'Sink' named tuple class
                Sink = namedtuple('Sink', 'sink_no_str volume name pid user')
                # noinspection PyArgumentList
                this_sink = Sink(str(sink.index), int(this_volume),
                                 str(sink.proplist['application.name']),
                                 int(sink.proplist['application.process.id']),
                                 str(sink.proplist['application.process.user']))
                all_sinks.append(this_sink)
            return all_sinks

        ''' If Python pulsectl.py audio isn't working, then use the slow method '''

        all_lines = os.popen('pactl list sink-inputs').read().splitlines()

        this_sink = ""
        in_sink = False
        this_volume = ""
        in_volume = False
        this_app = None
        this_pid = None
        this_user = None
        '''
        Sink Input #575
            ... (SNIP) ...
        Volume: front-left: 65536 / 100% / 0.00 dB,   front-right: 65536 / 100% ...
            ... (SNIP) ...
        Properties:
            application.name = "ffplay"
            application.process.id = "14765"
            application.process.user = "rick"
        '''
        for line in all_lines:
            if in_sink is False and "Sink Input #" in line:
                # Sink Input #725
                this_sink = line.split('#')[1]
                in_sink = True
                continue
            if in_sink is True and in_volume is False and "Volume:" in line:
                # Volume: front-left: 32768 /  50% / -18.06 dB,   front-right ...
                this_volume = line.split('/')[1]  # Grab 50% or 100%, etc
                this_volume = this_volume.replace(' ', '')
                if this_volume.endswith(']'):
                    # July 8, 2023 - Bug fix from above copied here just in case 
                    this_volume = this_volume[:-1]
                this_volume = int(this_volume.replace('%', ''))
                in_volume = True
                continue
            # noinspection SpellCheckingInspection
            if in_sink is True and in_volume is True:
                # inspection SpellCheckingInspection
                '''
                    application.name = "ffplay"
                    application.process.id = "14765"
                    application.process.user = "rick"
                '''
                # application.name = "ffplay"
                this_app = parse_line_for_assigned_value(
                    line, "application.name", this_app)
                this_pid = parse_line_for_assigned_value(
                    line, "application.process.id", this_pid)
                this_user = parse_line_for_assigned_value(
                    line, "application.process.user", this_user)
                # Add tuple to the list
                if this_app and this_pid and this_user:
                    Sink = namedtuple('Sink', 'sink_no_str, volume, name, pid, user')
                    # noinspection PyArgumentList
                    sink = Sink(this_sink, int(this_volume), this_app,
                                int(this_pid), this_user)
                    all_sinks.append(sink)
                    # Reset searching for first and second targets again
                    in_sink = False
                    in_volume = False
                    this_app = None
                    this_pid = None
                    this_user = None

                continue  # Carry on My Wayward Son

        return all_sinks


    def get_pulse_control(self):
        """ Seemed like a good idea at the time but, it crashes after being
            called a few times.
        """
        self.pulse_is_working = True
        ext.t_init("pulse = pulsectl.Pulse()")
        try:
            self.pulse = pulsectl.Pulse()
        except Exception as err:  # CallError, socket.error, IOError (pidfile), OSError (os.kill)
            self.pulse_is_working = False
            raise pulsectl.PulseError('mserve.py get_pulse_control() Failed to ' +
                                      'connect to pulse {} {}'.format(type(err), err))
        ext.t_end('no_print')  # from: 0.0017430782 to 0.0037407875
        return self.pulse


#class Sink(namedtuple('Sink', 'sink_no_str, volume, name, pid, user')):


# global functions
def parse_line_for_assigned_value(line, search, current):
    """ Check one console output line for search string

        If already found, return the original value. Sample line:
            application.process.id = "14765"

    """
    if current:
        return current  # Already found. Return previous find.

    if search + " = " not in line:
        return current  # Search string not in line.

    this_name = line.split('=')[1]
    this_name = this_name.replace(' ', '')
    this_name = this_name.replace('"', '')
    return this_name


# Sample data
# noinspection SpellCheckingInspection
''' 
WHILE Fine-Tune Index is playing:

>>> pulse.sink_input_list()
[
<PulseSinkInputInfo at 7f3c2a188410 - index=569L, mute=0, name=u'AudioStream'>, 
<PulseSinkInputInfo at 7f3c2a188910 - index=571L, mute=0, name=u'Simple DirectMedia Layer'>, 
<PulseSinkInputInfo at 7f3c2a188ed0 - index=573L, mute=0, name=u'Simple DirectMedia Layer'>
]

>>> print type(pulse.sink_input_list()[1])
<class 'pulsectl.pulsectl.PulseSinkInputInfo'>

>>> pulse.sink_input_list()[0].proplist
{
u'window.x11.display': u':0', 
u'application.process.session_id': u'c2',
u'application.process.host': u'alien', 
u'native-protocol.peer': u'UNIX socket client', 
u'application.process.binary': u'firefox', u'application.icon_name': u'firefox', 
u'native-protocol.version': u'30', 
u'application.process.machine_id': u'1ff17e6df1874fb3b2a75e669fa978f1', 
u'application.name': u'Firefox',  u'application.process.id': u'2985', 
u'media.name': u'AudioStream', 
u'module-stream-restore.id': u'sink-input-by-application-name:Firefox', 
u'application.process.user': u'rick', u'application.language': u'en_CA.UTF-8'}

>>> pulse.sink_input_list()[1].proplist
{u'window.x11.display': u':0', 
u'application.process.session_id': u'c2', 
u'application.process.host': u'alien', 
u'native-protocol.peer': u'UNIX socket client', 
u'application.process.binary': u'ffplay', u'native-protocol.version': u'30', 
u'application.process.machine_id': u'1ff17e6df1874fb3b2a75e669fa978f1', 
u'application.name': u'ffplay', u'application.process.id': u'7654', 
u'media.name': u'Simple DirectMedia Layer', 
u'module-stream-restore.id': u'sink-input-by-application-name:ffplay', 
u'application.process.user': u'rick', u'application.language': u'C'}

>>> pulse.sink_input_list()[2].proplist
{u'window.x11.display': u':0', 
u'application.process.session_id': u'c2',
u'application.process.host': u'alien', 
u'native-protocol.peer': u'UNIX socket client', 
u'application.process.binary': u'ffplay', u'native-protocol.version': u'30', 
u'application.process.machine_id': u'1ff17e6df1874fb3b2a75e669fa978f1', 
u'application.name': u'ffplay', u'application.process.id': u'13166', 
u'media.name': u'Simple DirectMedia Layer', 
u'module-stream-restore.id': u'sink-input-by-application-name:ffplay',
u'application.process.user': u'rick', u'application.language': u'C'}

$ ps -aux | grep ffplay

rick      7654  0.0  0.1 949960 46452 pts/22   Tl+  Jul07   0:00 
ffplay -autoexit /media/rick/SANDISK128/Music/Bachman-Turner Overdrive/
The Definitive Collection/13 Lookin' Out For #1.m4a 
-ss 2.46033906937 -af afade=type=in:start_time=2.46033906937:duration=1 -nodisp

rick     13166  0.0  0.1 949960 46532 pts/22   Tl+  Jul07   0:00 
ffplay -autoexit /media/rick/SANDISK128/Music/Bachman-Turner Overdrive/
The Definitive Collection/13 Lookin' Out For #1.m4a 
-ss 22.5405571461 -af afade=type=in:start_time=22.5405571461:duration=0.5 
-af afade=type=out:start_time=41.8019502163:duration=0.5 -t 19.7613930702 -nodisp

rick     14765  0.0  0.1 949960 46244 pts/22   Tl+  Jul07   0:01 
ffplay -autoexit /media/rick/SANDISK128/Music/Bachman-Turner Overdrive/
The Definitive Collection/13 Lookin' Out For #1.m4a 
-ss 37.8019502163 -af afade=type=in:start_time=37.8019502163:duration=0.5 
-af afade=type=out:start_time=89.643184185:duration=0.5 -t 52.3412339687 -nodisp


'''

# End of vu_pulse_audio.py
