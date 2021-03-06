# -*- coding: utf-8 -*-
#==============================================================================
#
#       external.py - Used by mserve, encoding.py and dell_start
#
#==============================================================================

from __future__ import print_function   # Must be first import

import signal                           # Trap shutdown to close files
import os
import errno
import time

# Common routines used by many programs put here

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


def launch_command(ext_name, toplevel=None):
    """ Launch external command in background and return PID to parent.
        Use for programs requiring more than .2 seconds to run.
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
    s = s.replace("'", "'\\''")
    return s.replace('"', '"\\""')


def kill_pid_running(active_pid):
    """ Kill running process we launched earlier. """
    if active_pid == 0:
        print("kill_pid_running() ERROR: argument is '0'")
        return 0                    # Programmer error

    try:
        os.kill(active_pid, 9)      # 0 is status check, 9 kills
        return True                 # pid killed
    except OSError:
        print("kill_pid_running() ERROR: os.kill failed")
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
        print("stop_pid_running() ERROR: os.kill failed")
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
        print("continue_pid_running() ERROR: os.kill failed")
        return 0                    # pid has finished


def stat_existing(filename):
    """ Remove file if it exists
        from: https://stackoverflow.com/a/10840586/6929343
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


# End of external.py
