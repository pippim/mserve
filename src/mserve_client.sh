#!/bin/bash
# NAME: mserve_client.sh
# DATE: August 2, 2023.
# DESC: Runs on SSH Host Server and is controlled by SSH client (remote).
#       Check if /tmp/mserve_client.time has been modified. If so, simulate
#       as user activity to keep host awake. Also check workstation activity.
#       Use gsettings to get settings for screen saver and AC idle shutdown.
#       If simulating user activity disables screen saver, turn it back on.
#       When idle time is long enough, broadcast warning message that
#       system is going down in 60, 30, 15, 10, 5, 3, 2, 1, 0 minute(s).
#       Based on ssh-activity created June 21, 2020 and modified July 18, 2020.
# NOTE: For Debugging, run the following commands on the host and client:
#       HOST (Open a terminal enter command to run forever):
#           mserve_client.sh -d
#       CLIENT (Copy to terminal and replace "<HOST>" with Host name):
#           while : ; do ssh <HOST> "cat /tmp/mserve_client.log" ; sleep 60 ; done

# Global CONSTANTS and Variables
export LANG=C  # Force english names for sed & grep searches
SLEEP_SECS=60  # Seconds to sleep between 'w -ish' command usage
OUTPUT_FN=/tmp/mserve_client.log
TIME_FN=/tmp/mserve_client.time
DECADE=315360000  # In case you were counting, 315 million seconds in a decade
REMOTE="192.168.0"  # What to 'grep' for in 'w -ish' output

# Global gsettings set by GsInit () function need to control screen & suspending
GsSuspendDelay=0   # idle seconds until system sleeps (0=never for all settings)
GsBlankDelay=0   # idle seconds until screen blanks (a good thing for server)
GsLockDelay=0   # idle seconds until screen locks (a bad thing if logged in)
GsLockEnabled=0 # is lock screen enabled? ('false' overrides GsLockDelay)
SSC_Result=""  # Screen Saver Command return value

# Global debug and Last Seconds variables
fOneTime=false  # for displaying debugging information one time only
fDebug=false  # When debug is on issue progress messages
HostIdle=0  # The REAL xprintidle last activity time. On startup it's just now.
FakeIdle=0  # xprintidle last activity time caused by Fake Simulated Activity.
LastWish="$DECADE"  # Lowest seconds since remote user activity
LastClient="$DECADE"  # Seconds since /tmp/mserve file modified

# Must have the xprintidle package.
command -v xprintidle >/dev/null 2>&1 || { echo >&2 \
        "'xprintidle' package required but it is not installed.  Aborting."; \
        exit 3; }

# Must have gsettings package.
command -v gsettings >/dev/null 2>&1 || { echo >&2 \
        "'gsettings' package required but it is not installed.  Aborting."; \
        exit 3; }

# Must have 'w' command.
command -v w >/dev/null 2>&1 || { echo >&2 \
        "'w' command required but it is not installed.  Aborting."; \
        exit 3; }

ParseParameters () {
  # Extract "$@" startup parameters passed to mainline now in "$1" (parameter 1)
    while [[ $# -gt 0 ]] ; do
        key="$1"
        case $key in
            -d|--debug)
                fDebug=true
                echo "Debug Mode = $fDebug"
                shift # past argument
                ;;
            *)  # unknown option
                echo "Usage: mserve_client.sh -d (--debug)"
                exit
            ;;
        esac
    done
} # ParseParameters

mInit () {
    # If DEBUG turned on, empty output file and append message header to file.
    [[ $fDebug == false ]] && return 0
    echo "" >| "$OUTPUT_FN"  # Empty last output file.  ">|" = allow clobber.
    echo "-----   $OUTPUT_FN   ---   $(date)   -----" >> "$OUTPUT_FN"
} # mInit ()

m () {
    # If DEBUG turned on, print messages to screen and append to file.
    [[ $fDebug == false ]] && return 0
    echo "$1"  # Print to console same as output file
    echo "$1" >> "$OUTPUT_FN"
} # m ()

GsInit () {
    # gsettings is called to know when system should shut down and screen should
    #   be blanked (screen saver turned on) due to inactivity $(xprintidle)
  # GsSuspendDelay - Gsettings on AC Power time to suspend
    GsSuspendDelay=$(gsettings get org.gnome.settings-daemon.plugins.power \
                     sleep-inactive-ac-timeout)
  # GsAcIdleDelay - Gnome Settings idle time to blank screen
    GsBlankDelay=$(gsettings get org.gnome.desktop.session idle-delay)
    GsBlankDelay="${GsBlankDelay##* }"  # Cut out right side value from 'uint32 0'
    [[ $GsBlankDelay -eq 0 ]] && GsBlankDelay="$DECADE"
  # GsLockDelay - Gnome Settings idle time to lock screen
    GsLockDelay=$(gsettings get org.gnome.desktop.screensaver lock-delay)
    GsLockDelay="${GsLockDelay##* }"
    [[ $GsLockDelay -eq 0 ]] && GsLockDelay="$DECADE"
  # GsLockEnabled - Is lock screen enabled? ('false' overrides GsLockDelay)
    GsLockEnabled=$(gsettings get org.gnome.desktop.screensaver lock-enabled)

  # print Gsettings values at program start, regardless of debug state
    if [[ $fDebug == true && $fOneTime == false ]] ; then
        echo "$0 started at: $(date)"
        echo "GsSuspendDelay: $GsSuspendDelay"
        echo "GsBlankDelay: $GsBlankDelay"
        echo "GsLockDelay: $GsLockDelay"
        echo "GsLockEnabled: $GsLockEnabled"
        fOneTime=true  # Never reprint Gsettings values
    fi
} # Init ()

GetWish () {
    # Get time of last activity from remotely signed on terminals
    # 'w' command '-ish' arguments (--ip-add dr, --short, --no-header) returns:
    #       rick     pts/21   192.168.0.12      4.00s sshd: rick [pri v]
    local ThisCheckSeconds ArrEntCnt ArrCols=5 ArrRows CheckSum i
    ThisCheckSeconds="$DECADE"  # Assume no results from 'w -ish' command.
    WishArr=( $(w -ish | grep "$REMOTE" | tr -s " " | \
             cut -d' ' -f1-"$ArrCols") )
  # The fifth column on each row repurposed to be idle time seconds
    ArrEntCnt="${#WishArr[@]}"
    [[ $ArrEntCnt -lt "$ArrCols" ]] && return 1  # No remote logins
    ArrRows=$(( ArrEntCnt / ArrCols ))
    CheckSum=$(( ArrRows * ArrCols ))
    [[ $ArrEntCnt -ne "$CheckSum" ]] && { echo WishArr CheckSum failed ; \
                                               return 2 ; }
  # Loop through 'w -ish' output
    for (( i=0; i<ArrEntCnt; i=i+ArrCols )) ; do
        # Time formatted as D days, HH:MMm, MM:SSs & SS.CC convert to Seconds
        WishSeconds "${WishArr[i+3]}" Seconds  # Place result in $Seconds
        [[ "$Seconds" -lt "$ThisCheckSeconds" ]] && ThisCheckSeconds="$Seconds"
        WishArr[i+4]=$Seconds   # Store in repurposed array column # 5
        # Display debug results
        m "${WishArr[i]}  | ${WishArr[i+1]}  | ${WishArr[i+2]}\
  | Wish Time: ${WishArr[i+3]}  | Seconds: ${WishArr[i+4]}"
    done
  # If terminal activity found, record it as LastWish
    if [[ "$ThisCheckSeconds" -ne "$DECADE" ]] ; then
        LastWish="$ThisCheckSeconds"  # A terminal is logged in via ssh.
    fi
    return 0  # return 0 is for cosmetics only. Value not checked by caller.
} # GetWish ()

: <<'END'
/* ------------ NOTES  --------------------------------------------------------

$ w -ish

rick     tty7     :0                2days /sbin/upstart --user
rick     pts/21   192.168.0.12      4.00s sshd: rick [pri v]
AND THEN LATER ON....
rick     pts/21   192.168.0.12     44.00s sshd: rick [pri v]
rick     pts/21   192.168.0.12      1:24  sshd: rick [pri v]
rick     pts/21   192.168.0.12      2:04  sshd: rick [pri v]

From: https://serverfault.com/questions/302455/
      how-to-read-the-idle-column-in-the-output-of-the-linux-w-command/
      302462#302462

From the man page:

    The standard format is D days, HH:MMm, MM:SS or SS.CCs .
    if the times are greater than 2 days, 1hour, or 1 minute respectively.
    so your output is MM:SS (>1m and <1 hour).

---------------------------------------------------------------------------- */
END

WishSeconds () {
    # Convert Wish unique time formats to seconds
    # PARM 1: 'w -ish' command idle time 44.00s, 5:10, 1:28m, 3days, etc.
    #      2: Variable name (no $ is used) to receive idle time in seconds
    # NOTE: Idle time resets to zero when user types something in terminal.
    #       A looping job calling a command doesn't reset idle time.
    local Wish Unit1 Unit2
    Wish="$1"
    declare -n Seconds=$2
  # Leading 0 is considered octal value in bash. Change ':09' to ':9'
    Wish="${Wish/:0/:}"
    if [[ "$Wish" == *"days"* ]] ; then
        Unit1="${Wish%%days*}"
        Seconds=$(( Unit1 * 86400 ))
    elif [[ "$Wish" == *"m"* ]] ; then
        Unit1="${Wish%%m*}"
        Unit2="${Unit1##*:}"
        Unit1="${Unit1%%:*}"
        Seconds=$(( (Unit1 * 3600) + (Unit2 * 60) ))
    elif [[ "$Wish" == *"s"* ]] ; then
        Seconds="${Wish%%.*}"
    else
        Unit1="${Wish%%:*}"
        Unit2="${Wish##*:}"
        Seconds=$(( (Unit1 * 60) + Unit2 ))
    fi
} # WishSeconds ()

GetClient () {
    # Get file modify time of /tmp/mserve_client.time and set delta in $LastClient
    if ModifySeconds=$(date -r "$TIME_FN" '+%s') ; then
        CurrentSeconds=$(date +%s)
        LastClient=$(( CurrentSeconds - ModifySeconds ))
    else
        LastClient="$DECADE"
    fi
} # GetClient ()

CheckHostSuspend () {
    # Send wall message 60, 30, 15, 10, 5, 3, 2 and 1 minute(s) before shutdown
    [[ $GsSuspendDelay == 0 ]] && return  # System never shuts down
    MinutesLeft=$(( ( GsSuspendDelay / 60 ) - ( FakeIdle / 60 ) ))
    (( MinutesLeft-- ))  # Assume system suspended before 0 minutes are reached
    case $MinutesLeft in
        60|30|15|10|5|3|2|1)
            m "     'wall' broadcast: suspending Host in: $MinutesLeft minute(s)."
            wall "If no activity, suspending Host in: $MinutesLeft minute(s)." ;;
        0)
            m "Host suspended at: $(date)"
            wall "HOST SUSPENDED at: $(date)" ;;
    esac
} # CheckHostSuspend ()

ScreenSaverCommand () {
    # Send dbus method to screen saver
    local Parm1="$1"    # 'GetActive', 'SetActive', or 'SimulateUserActivity'
    local Parm2="$2"    # Optional, value 'true' required for 'SetActive' parm 1
  # If parameter 2 not passed force it to be unset, instead of null parm
    SSC_Result=$(gdbus call --session --dest org.gnome.ScreenSaver \
                 --object-path /org/gnome/ScreenSaver \
                 --method org.gnome.ScreenSaver."$Parm1" ${Parm2:+"$Parm2"})
    m "Screen Saver Command: $Parm1 $Parm2 Result: $SSC_Result"
} # ScreenSaverCommand ()

CheckToBlankOrLock () {
  # Check if screen saver needs to be activated after simulating activity
    ScreenSaverCommand "GetActive"  # Get screen saver active status
    if [[ $SSC_Result == *"false"* ]] ; then  # If screen saver turned off
        if [[ $HostIdle -gt $GsBlankDelay ]] ; then  # If it should be on
            m "FORCING SCREEN BLANK (Set screen saver active)"
            ScreenSaverCommand "SetActive" true
        fi
    fi
} # CheckToBlankOrLock ()

main () {
  # Parse parameters and then loop forever (until <Control>+C)
    ParseParameters "$@"  # Set -d (--debug) options on commandline
    local IdleSeconds LowestSeconds

    while : ; do  # Loop forever until <Control>+C
      # Initialize variables with last seconds
        mInit  # Initialize new debug group output
        GsInit  # Get Gnome Settings (Gsettings / Gs)
        GetWish  # Get remote/terminal activity using 'w -ish'
        GetClient  # Get '/tmp/mserve_client.time' modification time
      # Get current idle seconds using xprintidle
        IdleSeconds=$(( $(xprintidle) / 1000 ))  # xprintidle uses milliseconds
        [[ "$IdleSeconds" -lt "$FakeIdle" ]] && HostIdle="$IdleSeconds"
      # Set lowest last seconds out of the group of tests
        LowestSeconds="$DECADE"
        [[ "$LastWish" -lt "$LowestSeconds" ]] && LowestSeconds="$LastWish"
        [[ "$LastClient" -lt "$LowestSeconds" ]] && LowestSeconds="$LastClient"
      # Simulate user activity if test results < last xprintidle reset
        if [[ "$LowestSeconds" -lt "$FakeIdle" ]] ; then
            ScreenSaverCommand "SimulateUserActivity"
            CheckToBlankOrLock  # Blank screen based on $HostIdle seconds
            FakeIdle=0
        else
            CheckHostSuspend  # Check to send shutdown message
        fi
      # Format and print debug line if requested with -d (--debug) parameter
        line="Host Idle: $HostIdle  | Fake Idle: $FakeIdle"
        [[ "$LastWish" -lt "$DECADE" ]] && line="$line  | LastWish: $LastWish"
        [[ "$LastClient" -lt "$DECADE" ]] && line="$line  | LastClient: $LastClient"
        m "$line"  # Display debug results when -d switch used.
      # Sleep then increment last W-ish seconds and idle seconds
        sleep "$SLEEP_SECS"
        [[ "$LastWish" -ne "$DECADE" ]] && LastWish=$(( LastWish + SLEEP_SECS ))
        HostIdle=$(( HostIdle + SLEEP_SECS ))
        FakeIdle=$(( FakeIdle + SLEEP_SECS ))
    done  # Continue looping forever until <Control>+C
} # main ()

main "$@"

# End of mserve_client.sh
