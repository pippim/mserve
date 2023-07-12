#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Pulse Audio controls
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

# ==============================================================================
#
#       vu_pulse_audio.py - Manage audio sinks and set volume
#
#       July 07 2023 - Enhanced code converted from mserve.py
#
# ==============================================================================
"""

NOTE: Use pavucontrol to create loopback from sound output to microphone:
      https://wiki.ubuntu.com/record_system_sound - Required by vu_meter.py
      Keep an eye open if vu_meter.py can be made more robust.

"""


import mserve_config as cfg
caller = "vu_pulse_audio.py"
if not cfg.main(caller):
    print("mserve not fully installed. Aborting...")
    exit()
else:
    print(caller, "finished call to mserve_config.py with SUCCESS!")

import global_variables as g

if g.USER is None:
    print('vu_pulse_audio.py was forced to run g.init()')
    g.init()

import os
import time
from collections import OrderedDict, namedtuple

# Subdirectory /pulsectl under directory where mserve.py located
from pulsectl import pulsectl
#print(pulsectl.__file__)  # Using - mserve/src/pulsectl?

# Pippim modules
import external as ext
import timefmt as tmf
import toolkit

who_am_i = "vu_pulse_audio.py PulseAudio."


class PulseAudio:
    """ Manage list of sinks created from Pulse Audio information.
        Fade in/out sound volumes when polled every 33ms.
    """

    def __init__(self, Info=None):
        self.info = Info  # Can also use: self.registerInfoCentre() to set
        self.pulse_is_working = True
        try:
            ext.t_init("pulse = pulsectl.Pulse()")
            self.pulse = pulsectl.Pulse()
            # print("pulse:", dir(pulse))
            ext.t_end('no_print')  # 0.0037407875

        except Exception as err:  # CallError, socket.error, IOError (pidfile), OSError (os.kill)
            self.pulse_is_working = False
            raise pulsectl.PulseError('mserve.py get_pulse_control() Failed to ' +
                                      'connect to pulse {} {}'.format(type(err),
                                                                      err))

        self.last_pid_sink = None  # Used for stability to ensure same sink
        self.curr_pid_sink = None  # number isn't classified as a new sink.
        self.aliens = None  # To turn down all apps except 'ffplay'

        self.last_sink_input_list = None  # = self.pulse.sink_input_list()
        self.sinks_now = None  # mserve formatted list of tuple sinks
        self.get_all_sinks()  # auto saves to self.sinks_now
        self.sinks_at_init = self.sinks_now
        self.spam_count = 0  # Prevent error message flooding
        self.poll_count = 0  # To print first 10 job times to fade 
        self.fade_list = []
        self.dict = {}

    def fade(self, sink_no_str, begin, end, duration, finish_cb=None, arg_cb=None):
        """ Add new self.dict to fade_list
            'finish_cb': is an optional callback when fade cycle is completed
            'arg_cb': is an optional parameter to the optional callback
        """
        if sink_no_str is None:
            return  # Could use error message and trace...

        now = time.time()
        self.dict['sink_no_str'] = str(sink_no_str)  # Sink#, E.G. "849L"
        self.dict['begin_perc'] = float(begin)  # Starting volume percent
        self.dict['end_perc'] = float(end)  # Ending volume percent
        self.dict['start_time'] = now  # Time entered queue + duration = leave
        self.dict['duration'] = float(duration)  # Seconds fade will last.
        self.dict['finish_cb'] = finish_cb  # callback when fade is ALL done
        self.dict['arg_cb'] = arg_cb  # optional argument to callback
        self.dict['curr_perc'] = begin  # Required for reverse_fade()
        self.dict['history'] = []  # Used for debugging
        self.dict['last_time'] = now  # Just for debugging
        # If sink_no_str is already being faded, reverse it
        if not self.reverse_fade(now):  # When True, an existing fade
            # Add new fade job into queue where it will be processed every .033 secs
            self.fade_list.append(self.dict)

    def reverse_fade(self, now):
        """ Fade was already started now needs to reverse.

            Currently reversing fade needs same duration as original fade.

            poll_fades() calls reverse_fade() before adding new fade to list.
        """
        who = who_am_i + "reverse_fade(): "
        for i, scan_dict in enumerate(self.fade_list):
            if scan_dict['sink_no_str'] == self.dict['sink_no_str']:
                old_dict = dict(scan_dict)  # Shallow copy of old fade
                # Replace original fade with new fade in opposite direction
                elapsed = now - old_dict['start_time']
                new_duration = old_dict['duration'] - elapsed
                if self.dict['duration'] != old_dict['duration']:
                    # What to do when new duration is different?
                    print(who, "self.dict['duration']:", self.dict['duration'],
                          "old_dict['duration']:", old_dict['duration'])
                self.dict['duration'] = new_duration
                # New beginning volume percent is where fade left off last cycle
                self.dict['begin_perc'] = old_dict['curr_perc']
                # Debugging fields not normally accessed
                self.dict['curr_perc'] = old_dict['curr_perc'] 
                print(who + "started for sink:", self.dict['sink_no_str'],
                      "from:", self.dict['begin_perc'],
                      "to:", self.dict['end_perc'])
                self.fade_list[i] = self.dict
                return True  # Did reverse previous fade
        return False  # Did not reverse previous fade
    
    def poll_fades(self):
        """ Every 33ms (in theory) process next step of every fade job in queue
            When finished, set volume to final amount in self.dict['end_perc']
        """

        ''' Process every self.dict in the fade_list '''
        now = time.time()
        for i, self.dict in enumerate(self.fade_list):

            ''' If all done set final volume and grab next fade in queue '''
            if now >= self.dict['start_time'] + self.dict['duration']:
                self.set_volume(self.dict['sink_no_str'], self.dict['end_perc'])
                self.poll_callback()
                continue

            ''' Still fading. Calculate volume and set '''
            current_duration = now - self.dict['start_time']
            distance = self.dict['end_perc'] - self.dict['begin_perc']
            adjust = distance * current_duration / self.dict['duration']
            self.dict['curr_perc'] = self.dict['begin_perc'] + adjust
            self.set_volume(
                self.dict['sink_no_str'], self.dict['begin_perc'] + adjust)

        ''' Build new self.fade_list without the fades that just finished '''
        self.fade_list = \
            [x for x in self.fade_list if now < x['start_time'] + x['duration']]

    def poll_fades_debug(self):
        """ Every 33ms (in theory) process next step of fade job
            When finished, set volume to final amount (end_perc)
            Same as poll_fades() except loaded with debug information.
        """
        who = who_am_i + "poll_fades_debug(): "
        ext.t_init('self.pav.poll()')
        now = time.time()
        start_count = len(self.fade_list)
        finished_count = 0
        set_vol_time = 0.9999999  # Make obvious not done number

        # Note info.cast is blocking so use info.fact instead?
        ''' Process every fade_dict in the fade_list '''
        for i, self.dict in enumerate(self.fade_list):
            if now >= self.dict['start_time'] + self.dict['duration']:
                finished_count += 1
                last_volume = self.get_volume(self.dict['sink_no_str'],
                                              refresh=False)
                text = who + "fade completed normally.\n" + \
                    "\t" + "last volume before finalization: " + \
                    str(last_volume) + "\tsink#: " + self.dict['sink_no_str']
                str_history = ' '.join(str(e) for e in self.dict['history'])
                self.info.fact(text + "\n" + str_history)
                ext.t_init(who + ' - set_volume()')
                self.set_volume(self.dict['sink_no_str'],
                                self.dict['end_perc'])
                set_vol_time = ext.t_end('no_print')
                self.poll_callback()
                continue  # added on phone

            current_duration = now - self.dict['start_time']
            distance = self.dict['end_perc'] - self.dict['begin_perc']
            adjust = distance * current_duration / self.dict['duration']
            self.dict['curr_perc'] = self.dict['begin_perc'] + adjust
            self.dict['history'].append((str(self.dict['curr_perc']),
                                         str(current_duration)))
            self.fade_list[i] = self.dict
            job_time, err = \
                self.set_volume(self.dict['sink_no_str'],
                                self.dict['curr_perc'])
            if job_time is None:
                # sink has disappeared
                finished_count += 1
                last_volume = self.get_volume(self.dict['sink_no_str'])
                str_history = ' '.join(str(e) for e in self.dict['history'])
                self.info.fact(str(last_volume) + self.dict['sink_no_str'] +
                               " finished.\n" + str_history)
                self.poll_callback()

        # Build new list without completed fades
        self.fade_list = \
            [x for x in self.fade_list if now < x['start_time'] + x['duration']]

        end_count = len(self.fade_list)
        try:
            sink_no_str = self.dict['sink_no_str']
        except KeyError:
            sink_no_str = "??? MISSING ???"
        text = who + "sink finished fading.\n" + \
            "sink_no_str: " + sink_no_str + \
            " finished_count: " + str(finished_count) + \
            " start_count: " + str(start_count) + \
            " end_count: " + str(end_count)

        poll_time = ext.t_end('no_print')
        if finished_count and self.poll_count < 10:
            self.poll_count += 1
            print("\n" + text, "poll_time:", poll_time)  # poll time: 0.1248590
            print("set_vol_time:", set_vol_time, "\n")
            str_history = ' '.join(str(e) for e in self.dict['history'])
            print("\nself.dict['history']:", str_history)
            # poll time: 0.1248590 is way too long.
            # Caused by info.cast. Change to info.fact now is: 0.0696840286255

        if finished_count != start_count - end_count:
            # self.info should be declared by now but test just to be sure
            if self.info and self.spam_count < 10:
                self.spam_count += 1  # Don't flood with broadcasts
                self.info.cast(text, 'error')

    def poll_callback(self):
        """ fade has finished. Now call 'stop' or 'kill' or whatever. """

        if self.dict['finish_cb'] is not None:  # Was callback passed?
            if self.dict['arg_cb'] is not None:  # Does callback have arg?
                # Call function name with argument (probably pid)
                self.dict['finish_cb'](self.dict['arg_cb'])
            else:
                self.dict['finish_cb']()  # Call function name without arg.

    def get_volume(self, sink_no_str, refresh=True):
        """ Get current volume of sink.
        :param sink_no_str: Pulse Audio sink number converted to string
        :param refresh: When False, reuse self.sinks_now from last time
        """
        who = who_am_i + "get_volume(): "
        if refresh:
            self.get_all_sinks()  # Populates self.sinks_now[]
        for Sink in self.sinks_now:
            if Sink.sink_no_str == sink_no_str:
                return Sink.volume

        self.info.cast(who + "unable to find sink#: " + sink_no_str)
        return None

    def set_volume(self, target_sink, percent):
        """ Set volume and return time required to do it
            Note it uses: volume_set_all_chans()
            DOES NOT use: volume_change_all_chans() which changes volume by
                          adjustment percentage.
        """
        who = who_am_i + "set_volume(): "
        if self.pulse_is_working:
            ''' Fast method using pulse audio direct interface '''
            ext.t_init(who + '-- pulse.volume_change')
            err = None  # Default to no error
            try:
                self.last_sink_input_list = self.pulse.sink_input_list()
            except pulsectl.pulsectl.PulseOperationFailed as err:  # 56
                # noinspection SpellCheckingInspection
                '''
SECOND Exception HAPPENED AFTER `pulseaudio -k` to fix FIRST EXCEPTION
  File "/home/rick/python/pulsectl/pulsectl.py", line 523, in _pulse_op_cb
    if not self._actions[act_id]: raise PulseOperationFailed(act_id)
pulsectl.pulsectl.PulseOperationFailed: 56
                '''
                print(who + "pulsectl.pulsectl.PulseOperationFailed:", err)
                return None, str(err)

            for sink in self.last_sink_input_list:
                if str(sink.index) == target_sink:
                    try:
                        self.pulse.volume_set_all_chans(sink, float(percent) / 100.0)
                    except pulsectl.pulsectl.PulseOperationFailed as err:  # 144
                        # noinspection SpellCheckingInspection
                        '''
FIRST Exception HAPPENED AFTER CHANGING SOUND OUTPUT DEVICES

  File "/home/rick/python/pulsectl/pulsectl.py", line 800, in volume_set_all_chans
    self.volume_set(obj, obj.volume)
  File "/home/rick/python/pulsectl/pulsectl.py", line 794, in volume_set
    method(obj.index, vol)
  File "/home/rick/python/pulsectl/pulsectl.py", line 634, in _wrapper
    except c.pa.CallError as err: raise PulseOperationInvalid(err.args[-1])
  File "/usr/lib/python2.7/contextlib.py", line 24, in __exit__
    self.gen.next()
  File "/home/rick/python/pulsectl/pulsectl.py", line 523, in _pulse_op_cb
    if not self._actions[act_id]: raise PulseOperationFailed(act_id)
pulsectl.pulsectl.PulseOperationFailed: 144
                        '''
                        print(who + "pulsectl.pulsectl.PulseOperationFailed:", err)
                        return None, str(err)

                    for i, S in enumerate(self.sinks_now):
                        if S.sink_no_str == target_sink:
                            Replace = namedtuple('Sink',
                                                 'sink_no_str volume name pid user')
                            # tuples immutable so recreate a new one based on old
                            # noinspection PyArgumentList
                            replace = Replace(str(S.sink_no_str), int(percent),
                                              S.name, S.pid, S.user)
                            self.sinks_now[i] = replace
                            # Was 100% added duplicate at 70%
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
                err_sinks = list()  # err_sinks is just for error message
                for sink in self.pulse.sink_input_list():
                    err_sinks.append(sink)
                print("Current sinks:", err_sinks)
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

    def find(self, pid):
        """
        Checks every 5 ms for Pulse Audio sink to appear after "ffplay" was
        launched as background task and the PID was discovered.

        :param pid: Linux process ID of "ffplay" instance just started
        :return sink: Pulse Audio sink number or None if pid not found
        """
        who = who_am_i + "find(): "
        ''' Originally sleeping for 5 ms, but it's blocking function
            and last song fading out for 1 second doesn't progress
        '''
        self.last_pid_sink = self.curr_pid_sink
        print_once = True
        for i in range(1000):  # Take 5 seconds maximum
            ext.t_init('PulseAudio.find()')
            self.sinks_now = self.get_all_sinks()
            ext.t_end('no_print')  # When pulse_is_working   : 0.0016
            #                        When pulse isn't working: 0.0093

            for Sink in self.sinks_now:
                if Sink.pid == pid:
                    self.curr_pid_sink = str(Sink.sink_no_str)
                    if str(self.last_pid_sink) == self.curr_pid_sink:
                        self.info_cast("Same sink used twice in row: " +
                                       self.curr_pid_sink)
                    ''' If too quick the volume is 'None' so drop down to wait.
                        Also the sink# is 1 less than the real sink# later after
                        the Volume is no longer 'None'.
                    '''
                    if Sink.volume is not None:
                        # Zero volume is ok so don't test "if Sink.Volume"
                        return str(Sink.sink_no_str)
                    else:
                        ''' Volume is 'None' so wait 5 ms. '''
                        if print_once:
                            print(who + "sink:", Sink.sink_no_str,
                                  "has volume of:", Sink.volume)
                        print_once = False
                        break  # Wait another 5ms and to get good volume

            ext.t_init('pav.find')
            self.poll_fades()
            job_time = ext.t_end('no_print')
            sleep = .005 - job_time
            sleep = .001 if sleep < .001 else sleep
            time.sleep(sleep)

    def registerInfoCentre(self, Info):
        """ Module imported in main() before InfoCentre() class defined. """
        self.info = Info

    def fade_out_aliens(self, fade_time):
        """ Turn down volume for all applications except 'ffplay'.
            E.G. Firefox would be an alien """
        self.get_all_sinks()
        self.aliens = list(self.sinks_now)  # Shallow copy for fade_in() later
        for Sink in self.aliens:
            if not Sink.name.startswith("ffplay"):
                self.fade(Sink.sink_no_str, Sink.volume, 1.0, fade_time)

    def fade_in_aliens(self, fade_time):
        """ Turn up volume for all applications except 'ffplay'.
            E.G. Firefox would be an alien """
        self.get_all_sinks()
        for Now in self.sinks_now:
            if not Now.name.startswith("ffplay"):
                if Now.volume != 1.0:  # fade_out went down to 1%
                    continue  # User manually reset volume
                for Sink in self.aliens:  # Use shallow copy from fade_out()
                    if Sink.sink_no_str == Now.sink_no_str:
                        self.fade(Sink.sink_no_str, Now.volume, Sink.volume,
                                  fade_time)
                        break

    def get_all_sinks(self):
        """ Get PulseAudio list of all sinks
            Return list of tuples with:
                sink #
                flat volume
                application name
                pid
                user name

                TODO: Add temp_filename to tuple
        """

        self.sinks_now = []  # List of tuples returned and saved locally

        # If Python pulseaudio is working, use the fast method
        if self.pulse_is_working:
            # .sink_input_list() only takes 0.0001280308 to 0.0008969307
            for sink in self.pulse.sink_input_list():
                this_volume = str(sink.volume)
                # <PulseVolumeInfo... - channels=1, volumes=[0%]>
                # <PulseVolumeInfo... - channels=2, volumes=[25% 25%]>
                this_volume = this_volume.split('[')[1]
                this_volume = this_volume.split('%')[0]
                # create 'Sink' named tuple class
                Sink = namedtuple('Sink', 'sink_no_str volume name pid user')
                # noinspection PyArgumentList
                this_sink = Sink(str(sink.index), int(this_volume),
                                 str(sink.proplist['application.name']),
                                 int(sink.proplist['application.process.id']),
                                 str(sink.proplist['application.process.user']))
                self.sinks_now.append(this_sink)
            return self.sinks_now

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
            Volume: front-left: 65536 / 100% / 0.00 dB,   front-right: ...
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
                this_volume = int(this_volume.replace('%', ''))
                in_volume = True
                continue

            if in_sink is True and in_volume is True:

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
                    sink = Sink(str(this_sink), int(this_volume), this_app,
                                int(this_pid), this_user)
                    self.sinks_now.append(sink)
                    # Reset searching for first and second targets again
                    in_sink = False
                    in_volume = False
                    this_app = None
                    this_pid = None
                    this_user = None

                continue  # Carry on My Wayward Son

        return self.sinks_now


    def get_pulse_control(self):
        """ Seemed like a good idea at the time but, it crashes after being
            called a few times.
            
            Morale of the story: ONLY CALL pulsectl ONCE !

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
        # noinspection SpellCheckingInspection
        ''' Random tinkering - Preliminary research to set sound output to recording

            1. Output to SONY BRAVIA TV - nvidia card:
                >>> pulse.sink_list()
                [<PulseSinkInfo at 7f3c2a188850 - 
                description=u'GM204 High Definition Audio Controller Digital Stereo (HDMI)', 
                index=0L, mute=0, name=u'alsa_output.pci-0000_01_00.1.hdmi-stereo', 
                channels=2, volumes=[100% 100%]>, 

                <PulseSinkInfo at 7f3c2a188250 - 
                description=u'Built-in Audio Analog Stereo', 
                index=2L, mute=0, name=u'alsa_output.pci-0000_00_1f.3.analog-stereo', 
                channels=2, volumes=[52% 52%]>]

                    NOTE: last index=2L

            2. Output to TCL/GOOGLE TV - intel chipset:
                >>> pulse.sink_list()
                [<PulseSinkInfo at 7f3c2a188f50 - 
                description=u'GM204 High Definition Audio Controller Digital Stereo (HDMI)', 
                index=0L, mute=0, name=u'alsa_output.pci-0000_01_00.1.hdmi-stereo', 
                channels=2, volumes=[100% 100%]>, 

                <PulseSinkInfo at 7f3c2a1a8110 - 
                description=u'Built-in Audio Digital Stereo (HDMI)', 
                index=3L, mute=0, name=u'alsa_output.pci-0000_00_1f.3.hdmi-stereo', 
                channels=2, volumes=[100% 100%]>]

                    NOTE: last index=3L
                          'Built-in Audio Digital Stereo (HDMI)'
                          'alsa_output.pci-0000_00_1f.3.hdmi-stereo'
                          pavucontrol does NOT update VU meter DB level bar

            3. Output to LAPTOP speakers - intel chipset:
                >>> pulse.sink_list()
                [<PulseSinkInfo at 7f3c2a188850 -
                 description=u'GM204 High Definition Audio Controller Digital Stereo (HDMI)', 
                 index=0L, mute=0, name=u'alsa_output.pci-0000_01_00.1.hdmi-stereo', 
                 channels=2, volumes=[100% 100%]>, 

                 <PulseSinkInfo at 7f3c2a1a8610 - 
                 description=u'Built-in Audio Analog Stereo', 
                 index=4L, mute=0, name=u'alsa_output.pci-0000_00_1f.3.analog-stereo', 
                 channels=2, volumes=[52% 52%]>]

                    NOTE: last index=4L
                          'Built-in Audio Analog Stereo'
                          'alsa_output.pci-0000_00_1f.3.analog-stereo'

            4. Output to TCL/GOOGLE TV - intel chipset:
                ... Same as before ...

                    NOTE: last index=5L
                          pavucontrol does NOT update VU meter DB level bar

        '''
        return self.pulse


#class Sink(namedtuple('Sink', 'sink_no_str, volume, name, pid, user')):
# Future class


# global functions
def parse_line_for_assigned_value(line, search, current):
    """ Check one console output line for search string

        If already found, return the original value. Sample line:
            application.process.id = "14765"

        Make this a global function in case another module needs same
        function someday...

    """
    if current:
        return current  # Already found. Return previous find.

    if search + " = " not in line:
        return current  # Search string not in line.

    this_name = line.split('=')[1]
    this_name = this_name.replace(' ', '')
    this_name = this_name.replace('"', '')
    return this_name

# End of vu_pulse_audio.py
