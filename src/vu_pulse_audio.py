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
#       July 12 2023 - Interface to/from mserve_config.py
#
# ==============================================================================
"""

NOTE: Use pavucontrol to create loopback from sound output to microphone:
      https://wiki.ubuntu.com/record_system_sound - Required by vu_meter.py
      Keep an eye open if vu_meter.py can be made more robust.

NOTE: Unstable if 'pulseaudio -k' run from command line.
      Lose vu_meter.py updates
      'Next' song stays at 25% volume until another 'Next' click
"""

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
FADE_NO = 0  # Aids in debugging


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
            'arg_cb': is an optional parameter to the optional callback function
        """
        if sink_no_str is None:
            toolkit.print_trace()
            print('pav.fade() passed empty sink_no_str')
            return  # Could use error message and trace...

        global FADE_NO
        FADE_NO += 1
        now = time.time()
        new_dict = dict()
        new_dict['FADE_NO'] = FADE_NO  # Aids in debugging
        new_dict['sink_no_str'] = str(sink_no_str)  # Sink#, E.G. "849L"
        new_dict['begin_perc'] = float(begin)  # Starting volume percent
        new_dict['end_perc'] = float(end)  # Ending volume percent
        new_dict['start_time'] = now  # Time entered queue + duration = leave
        new_dict['duration'] = float(duration)  # Seconds fade will last.
        new_dict['finish_cb'] = finish_cb  # callback when fade is ALL done
        new_dict['arg_cb'] = arg_cb  # optional argument to callback
        new_dict['curr_perc'] = float(begin)  # Required for reverse_fade()
        new_dict['history'] = []  # Used for debugging
        new_dict['last_time'] = now  # Just for debugging
        # If sink_no_str is already being faded, reverse it
        if not self.reverse_fade(new_dict, now):  # When True, an existing fade
            # Add new fade job into queue where it will be processed every .033 secs
            self.fade_list.append(new_dict)

    def reverse_fade(self, new_dict, now):
        """ Fade was already started now needs to reverse.

            Currently reversing fade needs same duration as original fade.

            poll_fades() calls reverse_fade() before adding new fade to list.

            self.dict contains current new fade fields.

        """
        who = who_am_i + "reverse_fade(): "
        for i, scan_dict in enumerate(self.fade_list):
            if scan_dict['sink_no_str'] == new_dict['sink_no_str']:
                old_dict = dict(scan_dict)  # Shallow copy of old fade
                elapsed = now - old_dict['start_time']  # Calculate new
                new_duration = old_dict['duration'] - elapsed  # duration
                if new_dict['duration'] != old_dict['duration']:
                    print(who, "new_dict['duration']:", new_dict['duration'],
                          "old_dict['duration']:", old_dict['duration'])
                new_dict['duration'] = new_duration
                new_dict['begin_perc'] = old_dict['curr_perc']  # Reverse volume
                new_dict['end_perc'] = old_dict['begin_perc']  # to old beginning
                new_dict['curr_perc'] = old_dict['curr_perc']
                new_dict['history'].extend(old_dict['history'])
                self.fade_list[i] = new_dict
                #print("\n" + who + "started for sink:", new_dict['sink_no_str'],
                #      "from:", new_dict['begin_perc'],
                #      "to:", new_dict['end_perc'],
                #      "elapsed:", elapsed,
                #      "new_duration:", new_duration)
                #print("\nold_dict:", old_dict)
                #print("\nnew_dict:", new_dict)
                return True  # Did reverse previous fade
        return False  # Did not reverse previous fade
    
    def poll_fades(self):
        """ Every 33ms (in theory) process next step of every fade job in queue
            When finished, set volume to final amount in self.dict['end_perc']
        """

        ''' Process every self.dict in the fade_list '''
        now = time.time()
        for i, fade_dict in enumerate(self.fade_list):

            ''' If all done set final volume and grab next fade in queue '''
            if now >= fade_dict['start_time'] + fade_dict['duration']:
                self.set_volume(fade_dict['sink_no_str'], fade_dict['end_perc'])
                fade_dict['curr_perc'] = fade_dict['end_perc']
                self.fade_list[i] = fade_dict  # Update 'curr_perc' for reverse_fade()
                self.poll_callback(fade_dict)  # Uses current fade_dict
                continue

            ''' Still fading. Calculate volume and set '''
            current_duration = now - fade_dict['start_time']
            distance = fade_dict['end_perc'] - fade_dict['begin_perc']
            adjust = distance * current_duration / fade_dict['duration']
            fade_dict['curr_perc'] = fade_dict['begin_perc'] + adjust
            fade_dict['last_time'] = now
            fade_dict['history'].append((str(fade_dict['curr_perc']),
                                         str(current_duration)))
            self.fade_list[i] = fade_dict  # Update 'curr_perc' for reverse_fade()
            self.set_volume(
                fade_dict['sink_no_str'], fade_dict['begin_perc'] + adjust)

        ''' Build new self.fade_list without the fades that just finished '''
        self.fade_list = \
            [x for x in self.fade_list if now < x['start_time'] + x['duration']]

    def poll_fades_debug(self):
        """ Every 33ms (in theory) process next step of fade job
            When finished, set volume to final amount (end_perc)
            Same as poll_fades() except loaded with debug information.

            Run 'pulseaudio -k' to reset static:

Traceback (most recent call last):
  File "./m", line 81, in <module>
    main()
  File "./m", line 75, in main
    mserve.main(toplevel=splash, cwd=cwd, parameters=sys.argv)
  File "/home/rick/python/mserve.py", line 16727, in main
    MusicTree(toplevel, SORTED_LIST)  # Build treeview of songs
  File "/home/rick/python/mserve.py", line 1422, in __init__
    self.load_last_selections()  # Play songs in favorites or playlists
  File "/home/rick/python/mserve.py", line 6675, in load_last_selections
    self.play_selected_list()
  File "/home/rick/python/mserve.py", line 7150, in play_selected_list
    if not self.play_one_song(resume=resume, chron_state=chron_state):
  File "/home/rick/python/mserve.py", line 8194, in play_one_song
    self.play_to_end()  # Play entire song unless next/prev, etc.
  File "/home/rick/python/mserve.py", line 8304, in play_to_end
    self.refresh_play_top()  # Rotate art, refresh vu meter
  File "/home/rick/python/mserve.py", line 8340, in refresh_play_top
    pav.poll_fades()
  File "/home/rick/python/vu_pulse_audio.py", line 176, in poll_fades
    fade_dict['sink_no_str'], fade_dict['begin_perc'] + adjust)
  File "/home/rick/python/vu_pulse_audio.py", line 301, in set_volume
    except pulsectl.pulsectl.PulseOperationFailed as err:  # 56
AttributeError: 'module' object has no attribute 'pulsectl'

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

    def poll_callback(self, scan_dict):
        """ fade has finished. Now call 'stop' or 'kill' or whatever. """

        if scan_dict['finish_cb'] is not None:  # Was callback passed?
            if scan_dict['arg_cb'] is not None:  # Does callback have arg?
                # Call function name with argument (probably pid)
                scan_dict['finish_cb'](scan_dict['arg_cb'])
            else:
                scan_dict['finish_cb']()  # Call function name without arg.

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
            except pulsectl.PulseOperationFailed as err:  # 56
                # noinspection SpellCheckingInspection
                '''
SECOND Exception HAPPENED AFTER `pulseaudio -k` to fix FIRST EXCEPTION
  File "/home/rick/python/pulsectl/pulsectl.py", line 523, in _pulse_op_cb
    if not self._actions[act_id]: raise PulseOperationFailed(act_id)
pulsectl.pulsectl.PulseOperationFailed: 56

THIRD Exception after fixing pulsectl.pulsectl. reference to pulsectl.

  File "/home/rick/python/vu_pulse_audio.py", line 176, in poll_fades
    fade_dict['sink_no_str'], fade_dict['begin_perc'] + adjust)
  File "/home/rick/python/vu_pulse_audio.py", line 328, in set_volume
    self.last_sink_input_list = self.pulse.sink_input_list()
  File "/home/rick/python/pulsectl/pulsectl.py", line 563, in _wrapper_method
    *([index, cb, None] if index is not None else [cb, None]) )
  File "/home/rick/python/pulsectl/_pulsectl.py", line 673, in _wrapper
    raise self.CallError(*err)
pulsectl._pulsectl.CallError: ('pa_context_get_sink_input_info_list', (<pulsectl._pulsectl.LP_PA_CONTEXT object at 0x7f91c772c560>, <CFunctionType object at 0x7f91bd039a10>, None), <pulsectl._pulsectl.LP_PA_OPERATION object at 0x7f91c772cd40>, 'Bad state [pulse errno 15]')


                '''
                try:
                    self.pulse = pulsectl.Pulse()
                    self.info.cast("PulseAudio reloaded. Restart mserve",
                                   "error")
                    return  # User can try again or poll_fades will do next step
                except:
                    print(who + "pulsectl.PulseOperationFailed:", err)
                    return None, str(err)

            for sink in self.last_sink_input_list:
                if str(sink.index) == target_sink:
                    try:
                        self.pulse.volume_set_all_chans(sink, float(percent) / 100.0)
                    except pulsectl.PulseOperationFailed as err:  # 144
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

SECOND Exception HAPPENED DURING SQL MUSIC TABLE SEARCH MISSING ARTWORK

  File "/home/rick/python/mserve.py", line 16687, in main
    ext.t_init('sql.create_tables()')
  File "/home/rick/python/mserve.py", line 1421, in __init__
    self.load_last_selections()  # Play songs in favorites or playlists
  File "/home/rick/python/mserve.py", line 6642, in load_last_selections
    """ Selected songs can be filtered by having time index or by Artist """
  File "/home/rick/python/mserve.py", line 7114, in play_selected_list
    #    self.splash_toplevel.withdraw()  # Remove splash screen
  File "/home/rick/python/mserve.py", line 8140, in play_one_song
    elif self.play_ctl.sink is not None:
  File "/home/rick/python/vu_pulse_audio.py", line 316, in set_volume
    except pulsectl.pulsectl.PulseOperationFailed as err:  # 144
AttributeError: 'module' object has no attribute 'pulsectl'


                        '''
                        try:
                            self.pulse = pulsectl.Pulse()
                            self.info.cast("PulseAudio reloaded. Restart mserve",
                                           "error")
                            return  # User can try again or poll_fades will do next step
                        except pulsectl.PulseOperationFailed as err:  # ???
                            print(who + "pulsectl.PulseOperationFailed:", err)
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
                        self.info.cast("Same sink used twice in row: " +
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
