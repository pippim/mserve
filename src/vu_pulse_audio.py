#!/usr/bin/env python
# -*- coding: utf-8 -*-

#==============================================================================
#
#       vu_pulse_audio.py - Manage audio sinks and set volume
#
#       July 07 2023 - Create init. Use import vu_pulse_audio.py as 
#
#==============================================================================
"""

NOTE: Use pavucontrol to create loopback from sound output to microphone:
      https://wiki.ubuntu.com/record_system_sound - Required by vu_meter.py

"""

from __future__ import print_function       # Must be first import
from __future__ import with_statement       # Error handling for file opens

import global_variables as g
if g.USER is None:
    print('vu_pulse_audio.py was forced to run g.init()')
    g.init()

try:
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

# Subdirectory /pulsectl under directory where mserve.py located
from pulsectl import pulsectl

# Pippim modules
import external as ext
import timefmt as tmf
import toolkit


class PulseAudio:
    """ an abstraction for Amplitudes (with an underlying float value)
    that packages a display function and many more
    
    January 25, 2021 - Remove unused add, sub, gt, eq, int & str functions
    """

    def __init__(self, value=0):
        self.value = value
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
        self.sinks_at_init = self.sink_master()
        # noinspection SpellCheckingInspection
        ''' 
WHILE Fine-Tune Index is playing:
        
>>> pulse.sink_input_list()
[
<PulseSinkInputInfo at 7f3c2a188410 - index=569L, mute=0, name=u'AudioStream'>, 
<PulseSinkInputInfo at 7f3c2a188910 - index=571L, mute=0, name=u'Simple DirectMedia Layer'>, 
<PulseSinkInputInfo at 7f3c2a188ed0 - index=573L, mute=0, name=u'Simple DirectMedia Layer'>
]

>>> pulse.sink_input_list()
[
<PulseSinkInputInfo at 7f3c2a188290 - 
index=569L, mute=0, name=u'AudioStream'>, 

<PulseSinkInputInfo at 7f3c2a1884d0 - 
index=571L, mute=0, name=u'Simple DirectMedia Layer'>, 

<PulseSinkInputInfo at 7f3c2a188b50 - 
index=573L, mute=0, name=u'Simple DirectMedia Layer'>, 

<PulseSinkInputInfo at 7f3c2a188fd0 - 
index=575L, mute=0, name=u'Simple DirectMedia Layer'>
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

$ pgrep -f ffplay
7654
13166
14765


        '''


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


    def sink_master(self):
        """ Get PulseAudio list of all sinks
            Return list of tuples with sink #, flat volume and application name
            April 29, 2023 - app_vol has glitch "0]" for speech-dispatcher
        """

        all_sinks = []  # List of tuples

        # If Python pulseaudio is working, use the fast method
        if self.pulse_is_working:
            for sink in self.pulse.sink_input_list():
                this_volume = str(sink.volume)
                # sink.volume = channels = 2, volumes = [100 % 100 %]
                this_volume = this_volume.split('[')[1]
                this_volume = this_volume.split(' ')[0]
                this_volume = this_volume.replace('%', '')
                if this_volume.endswith(']'):
                    # Bug end up with "0]" fixed Bug April 29, 2023
                    this_volume = this_volume[:-1]
                all_sinks.append(tuple((str(sink.index), int(this_volume),
                                        str(sink.proplist['application.name']))))
            return all_sinks

        # If no Python pulseaudio, then use the slow method
        all_lines = os.popen('pactl list sink-inputs').read().splitlines()

        this_sink = ""
        in_sink = False
        this_volume = ""
        in_volume = False
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
            # noinspection SpellCheckingInspection
            if in_sink is True and in_volume is True and "tion.name =" in line:
                # inspection SpellCheckingInspection
                # application.name = "ffplay"
                this_name = line.split('=')[1]
                this_name = this_name.replace(' ', '')
                this_name = this_name.replace('"', '')
                # Add tuple to the list
                all_sinks.append(tuple((this_sink, this_volume, this_name)))
                # Reset searching for first and second targets again
                in_sink = False
                in_volume = False
                continue

        # noinspection SpellCheckingInspection
        ''' return list of tuples (sink#, volume percent, application name) 
        
>>> import pulsectl
>>> with pulsectl.Pulse('volume-increaser') as pulse:
...   for sink in pulse.sink_list():
...     # Volume is usually in 0-1.0 range, with >1.0 being soft-boosted
...     pulse.volume_change_all_chans(sink, 0.1)
... 
>>> 

>>> pulse = pulsectl.Pulse('mserve 2023-07-07 16:45:30')

>>> pulse.sink_list()
[
<PulseSinkInfo at 7f3c2a188250 - 
description=u'GM204 High Definition Audio Controller Digital Stereo (HDMI)', 
index=0L, mute=0, 
name=u'alsa_output.pci-0000_01_00.1.hdmi-stereo', channels=2, 
volumes=[110% 110%]>, 

<PulseSinkInfo at 7f3c2a188a90 - 
description=u'Built-in Audio Digital Stereo (HDMI)', 
index=1L, mute=0, 
name=u'alsa_output.pci-0000_00_1f.3.hdmi-stereo', channels=2, 
volumes=[110% 110%]>
]

>>> pulse.sink_input_list()
[
<PulseSinkInputInfo at 7f3c2a188d50 - 
index=545L, mute=0, name=u'Simple DirectMedia Layer'>, 
<PulseSinkInputInfo at 7f3c2a188dd0 - 
index=552L, mute=0, name=u'AudioStream'>
]

>>> pulse.sink_input_list()[0].proplist
{
u'window.x11.display': u':0', 
u'application.process.session_id': u'c2', 
u'application.process.host': u'alien', 
u'native-protocol.peer': u'UNIX socket client', 
u'application.process.binary': u'ffplay', 
u'native-protocol.version': u'30', 
u'application.process.machine_id': u'1ff17e6df1874fb3b2a75e669fa978f1', 
u'application.name': u'ffplay', 
u'application.process.id': u'23981', 
u'media.name': u'Simple DirectMedia Layer', 
u'module-stream-restore.id': 
u'sink-input-by-application-name:ffplay', 
u'application.process.user': u'rick', 
u'application.language': u'C'
}

>>> pulse.source_list()
[
<PulseSourceInfo at 7f3c2a188990 - 
description=u'Monitor of GM204 High Definition Audio Controller Digital Stereo (HDMI)',
index=0L, mute=0, name=u'alsa_output.pci-0000_01_00.1.hdmi-stereo.monitor', 
channels=2, volumes=[100% 100%]>, 

<PulseSourceInfo at 7f3c2a188850 - 
description=u'Monitor of Built-in Audio Digital Stereo (HDMI)', 
index=1L, mute=1, name=u'alsa_output.pci-0000_00_1f.3.hdmi-stereo.monitor', 
channels=2, volumes=[100% 100%]>
]

>>> pulse.server_info().default_sink_name
u'alsa_output.pci-0000_01_00.1.hdmi-stereo'

>>> sink = pulse.sink_list()[0]
>>> pulse.default_set(sink)
>>> card = pulse.card_list()[0]
>>> card.profile_list
[
<PulseCardProfileInfo at 7f3c2a1889d0 - 
available=1, description=u'Digital Stereo (HDMI) Output', n_sinks=1L, 
n_sources=0L, name=u'output:hdmi-stereo', priority=5400L>, 

<PulseCardProfileInfo at 7f3c2a188e50 - 
available=1, description=u'Digital Surround 5.1 (HDMI) Output', n_sinks=1L, 
n_sources=0L, name=u'output:hdmi-surround', priority=300L>, 

<PulseCardProfileInfo at 7f3c2a188a90 - 
available=1, description=u'Off', n_sinks=0L, 
n_sources=0L, name=u'off', priority=0L>
]

>>> pulse.card_profile_set(card, 'output:hdmi-stereo')
        
        '''
        return all_sinks

# End of vu_pulse_audio.py
