#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Author: Pippim
License: GNU GPLv3
Source: This repository
Description: mserve - Music Server - Calls to External Programs
"""

from __future__ import print_function  # Must be first import
from __future__ import with_statement  # Error handling for file opens

#==============================================================================
#
#       external.py - Used by mserve, encoding.py and dell_start
#
#       July 12 2023 - Hooks to mserve_config.py
#       Aug. 18 2023 - Fix newish function - get_running_apps()
#       Aug. 22 2023 - remove_group() - remove file groups ending in * (splat)
#       Sep. 29 2023 - t(short=False) - Set to True for MM:SS printed only
#       June 02 2024 - Reactivate '?' as illegal filename character
#       Dec. 04 2024 - if t_init() ends in ":" don't add another when printing
#       June 01 2025 - Strip `env` from `#!/usr/bin/env python` for script name
#
#==============================================================================

import signal  # Trap shutdown to close files
import os
try:
    import subprocess32 as sp
    SUBPROCESS_VER = '32'
except ImportError:  # No module named subprocess32
    import subprocess as sp
    SUBPROCESS_VER = 'native'

import errno
import json  # For reading/writing files in json format, no image support
import glob  # For globbing files in /tmp/mserve_ffprobe*
import time
import datetime
import pickle  # For reading/writing files in pickle format, supports images
import toolkit  # Common Tkinter routines

# Program timings for OS calls and functions or loops
TIME_LIST = []  # list of tuples name, start time
TIME_NDX = 0  # index pushed or popped to support nested items


def t_init(name):
    """ Declare timer """
    global TIME_LIST, TIME_NDX
    TIME_LIST.append(tuple([name, time.time()]))
    # print('Adding TIME_NDX:',TIME_NDX,'name:',name)
    TIME_NDX += 1


def t_end(option):
    """ End timer """
    global TIME_LIST, TIME_NDX
    TIME_NDX -= 1
    name, start_time = TIME_LIST[TIME_NDX]
    elapsed = time.time() - start_time
    # print('Ending TIME_NDX:',TIME_NDX,'name:',name,'elapsed:',elapsed)
    append = "" if name.endswith(":") else ":"
    if option is "print":
        leader = ' ' * (TIME_NDX * 2) + name + append
        #        print(' ' * (TIME_NDX * 2), name+": ", elapsed)
        print(leader, format(elapsed, '.10f'))
    del TIME_LIST[-1]
    return elapsed


def t(float_time=None, short=False, hun=False):
    """ Print date and time with AM/PM """
    if not float_time:
        float_time = time.time()
    f_time = datetime.datetime.fromtimestamp(float_time)
    if short:
        if hun:
            return f_time.strftime("%H:%M:%S.%f")[:-5]  # chop off 5 of 6 decs
        else:
            return f_time.strftime("%H:%M:%S")
    else:
        return f_time.strftime("%b %d %Y %I:%M:%S %p")


def h(float_time=None):
    """ Print 24 hour clock with milliseconds """
    if not float_time:
        float_time = time.time()
    f_time = datetime.datetime.fromtimestamp(float_time)
    return f_time.strftime("%H:%M:%S.%f")


def ch():
    """ Print current 24 hour time with milliseconds """
    return h(time.time())


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


def read_into_list(fname):
    """ Read text file into list """
    if os.path.isfile(fname):
        with open(fname) as f:
            return f.read().splitlines()
    return None


def read_into_string(fname):
    """ Read text file into string with "\n" separating lines """
    if os.path.isfile(fname):
        with open(fname, "r") as f:
            return f.read()
    return None


def write_from_list(fname, f_list):
    """ Read list of lines and write to text file """

    if os.path.isfile(fname):
        #print("Overwriting existing file:", fname)
        pass
    else:
        #print("Creating new file:", fname)
        pass

    try:
        with open(fname, "w") as f:
            for f_line in f_list:
                f.write("%s\n" % f_line)
                #print("ext.write_from_list() wrote f_line:", f_line)
    except Exception as err:
        print("Exception:", err)
        return False

    return True


def write_from_string(fname, f_str):
    """ Read list of lines and write to text file """

    if os.path.isfile(fname):
        #print("Overwriting existing file:", fname)
        pass
    else:
        #print("Creating new file:", fname)
        pass

    try:
        with open(fname, "w") as f:
            f.write(f_str)
            #print("ext.write_from_list() wrote f_line:", f_line)
    except Exception as err:
        print("Exception:", err)
        return False

    return True


def read_from_json(fname):
    """ Read json file and return serialized object """
    if os.path.isfile(fname):
        with open(fname) as f:
            return json.loads(f.read())
    return None


def write_to_json(fname, s_obj):
    """ Write serialized object to storage """

    if os.path.isfile(fname):
        #print("Overwriting existing file:", fname)
        pass
    else:
        #print("Creating new file:", fname)
        pass

    try:
        with open(fname, "w") as f:
            s_obj = json.dumps(s_obj)
            f.write(s_obj)
    except Exception as err:
        print("Exception:", err)
        return False

    return True


def read_from_pickle(fname):
    """ Read pickle file and return serialized object with image(s) """
    if os.path.isfile(fname):
        with open(fname, 'rb') as f:
            try:
                return pickle.load(f)
            except EOFError:
                print("Pickle EOFError:", fname)
    return None


def write_to_pickle(fname, s_obj):
    """ Write serialized object with image to storage """

    if os.path.isfile(fname):
        #print("Overwriting existing file:", fname)
        pass
    else:
        #print("Creating new file:", fname)
        pass

    try:
        with open(fname, "wb") as f:
            pickle.dump(s_obj, f)
    except Exception as err:
        print("Exception:", err)
        return False

    return True


def check_command(name):
    """ Check if command installed in linux """
    return os.system("command -v " + name + " >/dev/null 2>&1") == 0


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


def launch_command(ext_name, toplevel=None, ms_wait=3000):
    """ Launch external command in background and return PID to parent.
        Use for programs requiring more than .2 seconds to run. Otherwise,
        program could run and finish before PID can be obtained.

        UPGRADE: https://stackoverflow.com/a/19152273/6929343
        # Can't use shell=True if you want the pid of `du`, not the
        # shell, so we have to do the redirection to file ourselves
        proc = sp.Popen("/usr/bin/du folder", stdout=file("1.txt", "ab"))
        print "PID:", proc.pid
        print "Return code:", proc.wait()

        Use subprocess: https://stackoverflow.com/a/20218672/6929343
            import subprocess
            import time
            argument = '...'
            proc = subprocess.Popen(['python', 'bar.py', argument], shell=True)
            time.sleep(3) # <-- There's no time.wait, but time.sleep.
            pid = proc.pid # <--- access `pid` attribute to get the pid of the child process.

        Can then use:
            proc.terminate()

        Also: https://stackoverflow.com/a/27007047/6929343
        import psutil, time, subprocess

        cmd = "python target.py"
        P = subprocess.Popen(cmd,shell=True)
        psProcess = psutil.Process(pid=P.pid)

        while True:
            time.sleep(5)
            psProcess.suspend()
            print 'I am proactively leveraging my synergies!'
            psProcess.resume()

        Also: https://stackoverflow.com/a/27007047/6929343
        Since you are on Linux, you can use the following reader.py:
        import subprocess, signal, time, os

        cmd = "python target.py"
        P = subprocess.Popen(cmd,shell=True)

        while True:
           time.sleep(5)
           os.kill(P.pid, signal.SIGSTOP)
           print "doing something"
           os.kill(P.pid, signal.SIGCONT)

    """
    #t_init("launch_ext_command")
    all_pid = pid_list(ext_name)
    new_pid = all_pid

    os.popen(ext_name + ' &')           # Run command in background
    sleep_count = 0
    sleep_max = ms_wait / 10
    #import psutil  # ImportError: No module named psutil
    #current_process = psutil.Process()
    #children = current_process.children(recursive=True)
    #for child in children:
    #    print('Child pid is {}'.format(child.pid))
    while new_pid == all_pid:
        #t_init("pid_list")
        new_pid = pid_list(ext_name)
        #pid_list_time = t_end('no_print')
        if new_pid != all_pid:
            break  # Skip sleep cycle
        if sleep_count > 0:  # Don't sleep first time through loop
            if toplevel is None:
                time.sleep(.01)  # sleep 10 milliseconds
            else:
                toplevel.after(10)  # Fine tune for sleep count of 2
        sleep_count += 1
        if sleep_count >= sleep_max:  # 3 second time-out
            print('launch_ext_command() ERROR: ', ms_wait, 'ms timeout reached.')
            print('External command name:', ext_name)
            return 0  # Return no PID found

    #print('launch_ext_command() sleep_count:', sleep_count, all_pid)
    diff_list = list(set(new_pid) - set(all_pid))

    #total_time = t_end('no_print')
    #print("launch_ext_command(" + ext_name + ") pid_list_time:", pid_list_time,
    #      "total_time:", total_time)  # pid_list_time: 0.017 total_time: 0.037
    if len(diff_list) == 1:
        return int(diff_list[0])  # Return PID number found

    print('launch_ext_command() ERROR: A new PID could not be found')
    return 0  # Return no PID found


def pid_list(ext_name):
    """ Return list of PIDs for program name and arguments
        Whitespace output is compressed to single space
    """
    # Just grep up to first space in command line. It was failing on !
    prg_name = ext_name.split(' ', 1)[0]
    all_lines = os.popen("ps aux | grep -v grep | grep " +
                         "'" + prg_name + "'").read().strip().splitlines
    PID = []
    for line in all_lines():
        line = ' '.join(line.split())       # Compress whitespace to single space
        PID.append(int(line.split(' ', 2)[1]))

    #print('pid_list:',PID)
    return PID


def check_pid_running(active_pid):
    """ Some functions will call 10 times a second until process is finished. """
    if active_pid == 0:
        return 0                    # Could be running in loop until PID ends

    try:
        os.kill(active_pid, 0)      # 0 is simply status check, 9 really kills
        return active_pid           # pid is still running
    except OSError:
        return 0                    # pid has finished


def shell_quote(s):
    """ Escape quotes in shell variables """
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
        print("external.kill_pid_running() ERROR: argument" +
              " 'active_pid' is:", active_pid)
        return 0                    # Programmer error

    try:
        os.kill(active_pid, 9)  # 0 is status check, 9 kills
        return True  # pid killed. prints "killed" to console if just killed self
    except OSError:
        ''' Problem when 'pulseaudio -k' run in CLI '''
        # toolkit.print_trace()
        # File "/home/rick/python/mserve.py", line 4780, in close
        #     self.close_sleepers()  # Shut down running functions
        # File "/home/rick/python/mserve.py", line 4827, in close_sleepers
        #     self.play_close()
        # File "/home/rick/python/mserve.py", line 10665, in play_close
        #     ext.kill_pid_running(self.vu_meter_pid)
        # File "/home/rick/python/external.py", line 251, in kill_pid_running
        #     toolkit.print_trace()
        # File "/home/rick/python/toolkit.py", line 86, in print_trace
        #     for line in traceback.format_stack():
        # external.kill_pid_running() ERROR: os.kill  failed for PID: 6910
        print("external.kill_pid_running() ERROR: os.kill " + 
              " failed for PID:", active_pid)
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
        from: https://stackoverflow.com/a/10840586/6929343 """
    try:
        os.remove(filename)
        return True
    except OSError as e:   # this would be "except OSError, e:" before Python 2.6
        if e.errno != errno.ENOENT:   # err no.ENO ENT = no such file or directory
            raise   # re-raise exception if a different error occurred

    #print("external.py remove_existing() filename doesn't exist:", filename)
    return False    # File doesn't exist


def remove_group(file_group):
    """ Remove group of file ending in '*' if any exist """
    count = 0
    for filename in glob.glob(file_group):
        #print("file_group:", file_group, "filename:", filename)
        if remove_existing(filename):
            count += 1
        else:
            print("external.py remove_group() error removing file:\n", filename)
            print("of file_group:", file_group)

    #print("external.py remove_group() removed count:", count,
    #      "group:", file_group)
    return count


def join(topdir, bottom):
    """  BEWARE DOES NOT PLAY NICELY WITH unicode 
    Based on: https://stackoverflow.com/a/51276165/6929343 """
    topdir = topdir.rstrip(os.sep)
    bottom = bottom.lstrip(os.sep)
    #return os.path.join(os.sep, topdir + os.sep, bottom)
    # Doesn't work see encoding.py
    # prefix = ext.join(self.topdir, part)
    return os.path.join(os.sep, topdir.encode('utf-8') + os.sep, 
                        bottom.encode('utf-8'))


def legalize_dir_name(name):
    """ '/', ':', and '?' are some of the invalid characters for file and
        directory names that are replaced with "_".
        See: https://stackoverflow.com/a/31976060/6929343
    """
    name = legalize_filename(name)
    if name.endswith("."):  # In Windows & Linux dirs cannot end in `.`
        name = name[:-1]
    return name


def legalize_filename(name):
    """ '/', ':', and '"' are some of the invalid characters for file and
        directory names that are replaced with "_".

        `/`, `:`, `<`, `>`, `_` `"`, `_` `\\`, `|` and `*`

        Credit: https://stackoverflow.com/a/31976060/6929343
    """
    name = name.replace('/', '_')  # Only character that Linux forbids
    name = name.replace('?', '_')  # 2024-06-02 - Was commented out
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
    name = legalize_filename(name)
    if name.endswith("."):  # In Windows files cannot end in `.`
        name = name[:-1]
    ''' Skip this because iTunes allowed "Vol. 1.m4a" in filename 
    ext = name.count('.')  # How many extension characters?
    if ext > 1:
        name = name.replace('.', '_', ext - 1)  # Keep last extension
    '''
    return name


def get_running_apps(version):
    """ Return list of named tuples with PIDs and names of running python apps.
        Used to ensure only one copy of application runs at a time.
        For Windows use: WMI. Win32_Process function

    :param version: When version 3, search is for python3, else python
    :returns list of tuples: (pid, prg_name)
    """
    ''' Set python program version searched for. '''
    search = "python"
    if version and version.startswith("3"):
        search += "3"  # Don't append "2" to make "pyhon2", no such thing

    ''' Find all python programs running. If 'python', 'python3' returned too. '''
    all_lines = os.popen("ps -ef | grep -v grep | grep " + search).\
        read().strip().splitlines
    apps_running = []
    for line in all_lines():
        ''' process single line of ps output '''
        #line = ' '.join(line.split())       # Compress whitespace to single space
        parts = line.split()  # No need to compress whitespace above - rework all
        # Sample: 'rick', '3458', '2829', '0', 'Aug08', '?', '00:19:53',
        #         '/usr/bin/python3', '/usr/bin/indicator-sysmonitor'
        # rick     25253  2437  0 14:21 pts/22   00:00:03 
        # /usr/bin/python ./vu_meter.py stereo mserve
        ''' Split out the program: 'python' or 'python3' '''
        prg_path = parts[7]

        base_parts = prg_path.split(os.sep)  # last will be python or python3
        python_name = base_parts[-1]
        if python_name == search:
            #print("Keeping python version:", prg_path)
            pass
        else:
            #print("Version requested:", str(version), "Skipping:", prg_path)
            continue  # Wrong version

        ''' Split out the app behind python command '''
        try:
            base_parts = parts[8].split(os.sep)  # /usr/bin/indicator-sysmonitor
        except IndexError:  # list index out of range
            ''' This is python interpreter and there is no script '''
            base_parts = parts[7].split(os.sep)  # /usr/bin/python3 

        pid = int(parts[1])  # give it name of 'pid' for clarity
        app = base_parts[-1]
        try:  # Get parameters if they exist
            parameters = parts[9:]
        except IndexError:
            parameters = []
        apps_running.append((pid, app, parameters))
    return apps_running


class GracefulKiller:
    """ From: https://stackoverflow.com/a/31464349/6929343
    """
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    # noinspection PyUnusedLocal
    def exit_gracefully(self, *args):
        """ If sigint set kill flag """
        self.kill_now = True


# End of external.py
