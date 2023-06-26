# -*- coding: utf-8 -*-
#==============================================================================
#
#       external.py - Used by mserve, encoding.py and dell_start
#
#==============================================================================

from __future__ import print_function   # Must be first import

import signal                           # Trap shutdown to close files
import os
try:
    import subprocess32 as sp
    SUBPROCESS_VER = '32'
except ImportError:  # No module named subprocess32
    import subprocess as sp
    SUBPROCESS_VER = 'native'

import errno
import time
import datetime

# Common routines used by many programs put here
import toolkit

# Program timings for OS calls and functions or loops
TIME_LIST = []  # list of tuples name, start time
TIME_NDX = 0  # index pushed or popped to support nested items


def t_init(name):
    global TIME_LIST, TIME_NDX
    TIME_LIST.append(tuple([name, time.time()]))
    # print('Adding TIME_NDX:',TIME_NDX,'name:',name)
    TIME_NDX += 1


def t_end(option):
    global TIME_LIST, TIME_NDX
    TIME_NDX -= 1
    name, start_time = TIME_LIST[TIME_NDX]
    elapsed = time.time() - start_time
    # print('Ending TIME_NDX:',TIME_NDX,'name:',name,'elapsed:',elapsed)
    if option is "print":
        leader = ' ' * (TIME_NDX * 2) + name + ":"
        #        print(' ' * (TIME_NDX * 2), name+": ", elapsed)
        print(leader, format(elapsed, '.10f'))
    del TIME_LIST[-1]
    return elapsed


def t(float_time):
    """ Print date and time with AM/PM """
    f_time = datetime.datetime.fromtimestamp(float_time)
    return f_time.strftime("%b %d %Y %I:%M:%S %p")


def h(float_time):
    """ Print 24 hour clock with milliseconds """
    f_time = datetime.datetime.fromtimestamp(float_time)
    return f_time.strftime("%H:%M:%S.%f")


def tail(f, n, offset=0):
    """
    https://stackoverflow.com/a/136280/6929343 Python 2 version give deprecation warning
    so use Python 3 version instead.

    sp is alias for subprocess32 or subprocess

    :param f: Filename to tail
    :param n: Number of lines at end of file
    :param offset: Generates error so comment out
    :return lines: list of last n lines in the filename
    """
    proc = sp.Popen(['tail', '-n', str(n + offset), f], stdout=sp.PIPE)
    lines = proc.stdout.readlines()
    #return lines[:, -offset]
    # TypeError: list indices must be integers, not tuple
    return lines


def which(cmd, path=None):
    """ test if path contains an executable file with name
        https://stackoverflow.com/a/28909933/6929343
    """
    if path is None:
        path = os.environ["PATH"].split(os.pathsep)

    for prefix in path:
        filename = os.path.join(prefix, cmd)
        executable = os.access(filename, os.X_OK)
        is_not_directory = os.path.isfile(filename)
        if executable and is_not_directory:
            # TODO for Windows add current directory
            return prefix + os.sep + cmd  # Path in which command exists
    return None


def launch_command(ext_name, toplevel=None):
    """ Launch external command in background and return PID to parent.
        Use for programs requiring more than .2 seconds to run. Otherwise,
        program could run and finish before PID can be obtained.

        UPGRADE: https://stackoverflow.com/a/19152273/6929343
        # Can't use shell=True if you want the pid of `du`, not the
        # shell, so we have to do the redirection to file ourselves
        proc = sp.Popen("/usr/bin/du folder", stdout=file("1.txt", "ab"))
        print "PID:", proc.pid
        print "Return code:", proc.wait()
    """

    all_pid = pid_list(ext_name)
    new_pid = all_pid

    os.popen(ext_name + ' &')           # Run command in background
    sleep_count = 0
    while new_pid == all_pid:
        new_pid = pid_list(ext_name)
        if sleep_count > 0:             # Don't sleep first time through loop
            if toplevel is None:
                time.sleep(.01)         # sleep 10 milliseconds
            else:
                toplevel.after(10)      # Fine tune for sleep count of 2
        sleep_count += 1
        if sleep_count == 1000:         # 10 second time-out
            print('launch_ext_command() ERROR: max sleep count reached')
            print('External command name:', ext_name)
            return 0

    #print('launch_ext_command() sleep_count:', sleep_count, all_pid)
    diff_list = list(set(new_pid) - set(all_pid))

    if len(diff_list) == 1:
        return int(diff_list[0])

    print('launch_ext_command() ERROR: A new PID could not be found')
    return 0


def pid_list(ext_name):
    """ Return list of PIDs for program name and arguments
        Whitespace output is compressed to single space
    """
    # Just grep up to first space in command line. It was failing on !
    prg_name = ext_name.split(' ', 1)[0]
    all_lines = os.popen("ps aux | grep -v grep | grep " +
                         "'" + prg_name + "'").read().strip().splitlines
    PID = []
    #for l in all_lines():              # Aug 13/2021 - Change for pycharm
    #    l = ' '.join(l.split())         # Compress whitespace to single space
    #    PID.append(int(l.split(' ', 2)[1]))
    for line in all_lines():
        line = ' '.join(line.split())       # Compress whitespace to single space
        PID.append(int(line.split(' ', 2)[1]))

    #print('pid_list:',PID)
    return PID


def check_pid_running(active_pid):
    """ Some parents call 10 times a second until process is finished.
    """
    if active_pid == 0:
        return 0                    # Could be running in loop until PID ends

    try:
        os.kill(active_pid, 0)      # 0 is status check, 9 kills
        return active_pid           # pid is still running
    except OSError:
        return 0                    # pid has finished


def shell_quote(s):
    """ Escape quotes in shell variable names """
    ''' E.G.
            def play_lyrics_from_web(self):
            """ turn on auto scrolling, it can be overridden from saved steps or
                if left-clicking on lyrics to set lyrics line to time index.
            """
            webscrape.delete_files()  # Cleanup last run
            self.lyrics_line_count = 1  # Average about 45 lines
    
            artist = ext.shell_quote(self.Artist)  # backslash in front of '
            song = ext.shell_quote(self.Title)     # and " in variables
    '''
    s = s.replace("'", "'\\''")
    return s.replace('"', '"\\""')


def kill_pid_running(active_pid):
    """ Kill running process we launched earlier. """
    if active_pid < 2:
        print("kill_pid_running() ERROR: argument 'active_pid' is:", active_pid)
        return 0                    # Programmer error

    try:
        os.kill(active_pid, 9)      # 0 is status check, 9 kills
        return True                 # pid killed
    except OSError:
        toolkit.print_trace()
        print("kill_pid_running() ERROR: os.kill failed for PID:", active_pid)
        return 0                    # pid has finished


def stop_pid_running(active_pid):
    """ Stop (pause) running process we launched earlier. """
    if active_pid == 0:
        print("stop_pid_running() ERROR: argument is '0'")
        return 0                    # Programmer error

    try:
        os.popen("kill -s STOP " + str(active_pid))         # Pause pid
        # Note SIGSTOP is shell supported, not linux supported use STOP
        # Get error: os.p open("kill -s SIGSTOP " + self.play_top_pid)
        return True                 # pid stopped
    except OSError:
        toolkit.print_trace()
        print("stop_pid_running() ERROR: os.kill failed to STOP job")
        return 0                    # pid has finished


def continue_pid_running(active_pid):
    """ Continue (resume) running process we launched earlier. """
    if active_pid == 0:
        print("continue_pid_running() ERROR: argument is '0'")
        return 0                    # Programmer error

    try:
        os.popen("kill -s CONT " + str(active_pid))         # Resume pid
        # Note SIGSTOP is shell supported, not linux supported use STOP
        # Get error: os.p open("kill -s SIGSTOP " + self.play_top_pid)
        return True                 # pid continued
    except OSError:
        toolkit.print_trace()
        print("continue_pid_running() ERROR: os.kill failed to CONT job")
        return 0                    # pid has finished


def stat_existing(filename):
    """ stat file and return attributes
    """
    try:
        stat = os.stat(filename)
        return stat
    except OSError as e:   # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:   # err no.ENO ENT = no such file or directory
            raise   # re-raise exception if a different error occurred

    return None    # File doesn't exist


def remove_existing(filename):
    """ Remove file if it exists
        from: https://stackoverflow.com/a/10840586/6929343
    """
    try:
        os.remove(filename)
        return True
    except OSError as e:   # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:   # err no.ENO ENT = no such file or directory
            raise   # re-raise exception if a different error occurred

    return False    # File doesn't exist


def legalize_dir_name(name):
    """ '/', ':', and '?' are some of the invalid characters for file and
        directory names that are replaced with "_".
        See: https://stackoverflow.com/a/31976060/6929343
    """
    name = legalize_most(name)
    name = name.replace('.', '_')
    return name


def legalize_most(name):
    """ Everything except '.' is fixed (legalized)
    """
    name = name.replace('/', '_')  # Only character that Linux forbids
    name = name.replace('?', '_')
    name = name.replace(':', '_')
    name = name.replace('<', '_')
    name = name.replace('>', '_')
    name = name.replace('"', '_')
    name = name.replace('\\', '_')
    name = name.replace('|', '_')
    name = name.replace('*', '_')
    return name


def legalize_song_name(name):
    """ Only one '.' can appear in pathname. Replace first ones with "_"
    """
    name = legalize_most(name)
    if name.endswith("."):  # In Windows files can end in `.`
        name = name[:-1]
    ext = name.count('.')  # How many extension characters?
    if ext > 1:
        name = name.replace('.', '_', ext - 1)  # Keep last extension
    return name


class GracefulKiller:
    """ From: https://stackoverflow.com/a/31464349/6929343
    """
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    # noinspection PyUnusedLocal
    def exit_gracefully(self, *args):
        self.kill_now = True


class SoundControl:
    """ "FF" for "fast forward", so ffmpeg stands for
        "Fast Forward Moving Picture Experts Group".

        Controller for ffmpeg, ffprobe and ffplay

        USAGE:
            sc_main = SoundControl()  # main playlist object
            sc_sync = SoundControl()  # synchronize (fine-tune time index)
            sc_sample = SoundControl()  # sample song object
    """

    # Initialization parameters
    pid = 0
    sink = ""
    start_sec = 0
    duration_secs = 0
    fade_in_secs = 0
    duet_sinks = []  # list of opposing sinks to turn up/down

    steps = 10  # How many steps between volume start and end?
    step_time = .05  # Time between steps

    # Metadata fields
    artist = None
    album = None
    title = None
    release_date = None
    original_date = None
    play_count = None
    genre = None
    rating = None

    # OS song information
    path = None
    access_time = None
    modification_time = None
    creation_time = None
    state = "Playing"  # Other option is "Paused" (STOP)
    current_secs = None


    def __init__(self, path):
        self.path = path

    # noinspection PyUnusedLocal
    def launch(self, *args):
        pass


"""
https://trac.ffmpeg.org/wiki/AudioVolume

Peak and RMS Normalization

To normalize the volume to a given peak or RMS level, the file first has to be
analyzed using the volumedetect filter:

ffmpeg -i input.wav -filter:a volumedetect -f null /dev/null

Read the output values from the command line log:

[Parsed_volumedetect_0 @ 0x7f8ba1c121a0] mean_volume: -16.0 dB
[Parsed_volumedetect_0 @ 0x7f8ba1c121a0] max_volume: -5.0 dB
...

... then calculate the required offset, and use the volume filter as shown above.
Loudness Normalization

If you want to normalize the (perceived) loudness of the file, use the ​
loudnorm filter, which implements the EBU R128 algorithm:

ffmpeg -i input.wav -filter:a loudnorm output.wav

This is recommended for most applications, as it will lead to a more uniform
 loudness level compared to simple peak-based normalization. However, it is
  recommended to run the normalization with two passes, extracting the measured
   values from the first run, then using the values in a second run with linear
    normalization enabled. See the loudnorm filter documentation for more. 
"""

# End of external.py
