#!/bin/bash

# NAME: mserve_client.sh
# DESC: Check if /tmp/mserve_client.time has been modified. If so, simulate
#       as user activity to keep host awake.

#       Reverse screen turning on after simulating user activity.
#       Use gsettings to get settings for screen blanking and shutdown.
#       Runs on host. If inactive, will broadcast warning message that
#       system is going down in 60, 30, 15, 10, 5, 3, 2, 1, 0 minute(s).
#       Based on ssh-activity: June 21, 2020. Modified: July 18, 2020

# DATE: August 1, 2023.

# NOTE: Program must be restarted once every ten years minimum.

#       For Debugging run on host and client

#       HOST: 
#           mserve_client.sh -d

#       CLIENT: 
#           while : ; do ssh <HOST> "cat /tmp/mserve_client.log" ; sleep 60 ; done

#               Where: "<HOST>" = Host name

# Global CONSTANTS and Variables
export LANG=C  # Force english names for sed & grep searches
SLEEP_SECS=60  # Seconds to sleep between 'w -ish' command usage
OUTPUT_FN=/tmp/mserve_client.log
TIME_FN=/tmp/mserve_client.time
DECADE=315360000
REMOTE="192.168.0"  # What we 'grep' for in 'w -ish' output

# Global gsettings set by GsInit () function need to control screen & suspending
GsSuspendDelay=0   # idle seconds until system sleeps (0=never for all settings)
GsBlankDelay=0   # idle seconds until screen blanks (a good thing for server)
GsLockDelay=0   # idle seconds until screen locks (a bad thing if logged in)
GsLockEnabled=0 # is lock screen enabled? ('false' overrides GsLockDelay)

# Global debug and Last Seconds variables
fOneTime=false  # for displaying debugging information one time only
fDebug=false  # When debug is on issue progress messages
LastWish=0  # Lowest seconds since remote user activity
LastClient=0  # Seconds since /tmp/mserve file modified

ParseParameters () {

    while [[ $# -gt 0 ]] ; do
        key="$1"
        case $key in
            -d|--debug)
                fDebug=true
                echo "Development Mode = $fDebug"
                shift # past argument
                ;;
            -n|--no-blank-lock)
                fNoBlankLock=true  # Aug 1/23 ignored.
                shift # past argument
                ;;
            -i|--ignore-idle)
                fIgnoreIdle=true  # Aug 1/23 ignored.
                shift # past argument
                ;;
            *)  # unknown option
                #echo "Usage: mserve_client.sh -d (--debug) -n (--no-blank-lock) -i (--ignore-idle)"
                echo "Usage: mserve_client.sh -d (--debug)"
                exit
            ;;
        esac
    done
} # ParseParameters

# Must have the xprintidle package.
command -v xprintidle >/dev/null 2>&1 || { echo >&2 \
        "'xprintidle' package required but it is not installed.  Aborting."; \
        exit 3; }

mInit () {
    # If DEBUG turned on create output file message header.
    [[ $fDebug == false ]] && return 0

    # Empty last output file and allow clobber >|
    echo "===== mserve_client.log results ===  $(date) ====" >| "$OUTPUT_FN"
} # mInit ()

m () {
    # If DEBUG turned on echo messages to screen and file.
    [[ $fDebug == false ]] && return 0
    echo "$1"
    echo "$1" >> "$OUTPUT_FN"
} # m ()

GsInit () {

    # gsettings required to know when system shuts down due to xidle time
    # GsSuspendDelay - Gsettings on AC Power time to suspend
    GsSuspendDelay=$(gsettings get org.gnome.settings-daemon.plugins.power \
                     sleep-inactive-ac-timeout)

    # gsettings required for blanking and locking screen when no host activity
    #if [[ $fNoBlankLock == false ]] ; then
    # GsAcIdleDelay - Gnome Settings idle time to blank screen
    GsBlankDelay=$(gsettings get org.gnome.desktop.session idle-delay)
    # Cut out right side value from 'uint32 0'
    GsBlankDelay="${GsBlankDelay##* }"
    [[ $GsBlankDelay -eq 0 ]] && GsBlankDelay="$DECADE"
    # GsLockDelay - Gnome Settings idle time to lock screen
    GsLockDelay=$(gsettings get org.gnome.desktop.screensaver lock-delay)
    GsLockDelay="${GsLockDelay##* }"
    [[ $GsLockDelay -eq 0 ]] && GsLockDelay="$DECADE"
    # GsLockEnabled - Is lock screen enabled? ('false' overrides GsLockDelay)
    GsLockEnabled=$(gsettings get org.gnome.desktop.screensaver lock-enabled)
    #fi

    if [[ $fDebug == true && $fOneTime == false ]] ; then
        # print Gsettings values at program start, regardless of debug state
        echo "$0 started at: $(date)"
        echo "GsSuspendDelay: $GsSuspendDelay"
        echo "GsBlankDelay: $GsBlankDelay"
        echo "GsLockDelay: $GsLockDelay"
        echo "GsLockEnabled: $GsLockEnabled"
        fOneTime=true  # Never reprint Gsettings values
    fi

} # Init

GetWish () {
    # Get time of last commands received from client
    # 'w' command '-ish' arguments (--ip-adddr, --short, --no-header) returns:
    #       rick     pts/21   192.168.0.12      4.00s sshd: rick [priv] 

    local ArrEntCnt ArrCols=5 ArrRows CheckSum i

    LastWish="$DECADE"
    WishArr=( $(w -ish | grep "$REMOTE" | tr -s " " | \
             cut -d' ' -f1-"$ArrCols") )
    # The fifth column on each row repurposed to be idle time seconds
    ArrEntCnt="${#WishArr[@]}"
    [[ $ArrEntCnt -lt "$ArrCols" ]] && return 1  # No remote users

    ArrRows=$(( ArrEntCnt / ArrCols ))
    CheckSum=$(( ArrRows * ArrCols ))
    # Error possible if 'w -ish' command breaks down
    [[ $ArrEntCnt -ne "$CheckSum" ]] && { echo WishArr CheckSum failed ; \
                                               return 2 ; }

    for (( i=0; i<ArrEntCnt; i=i+ArrCols )) ; do
        # Time formatted as D days, HH:MMm, MM:SSs & SS.CC convert to Seconds
        WishSeconds "${WishArr[i+3]}" Seconds  # Place result in $Seconds
        [[ "$Seconds" -lt "$LastWish" ]] && LastWish="$Seconds"
        WishArr[i+4]=$Seconds   # Store in repurposed array column # 5

        m "${WishArr[i]} ${WishArr[i+1]} \
${WishArr[i+2]} Wish Time: ${WishArr[i+3]} Seconds: ${WishArr[i+4]} "
    done

    return 0

} # GetWish

: <<'END'
/* ------------ NOTES  --------------------------------------------------------

$ w -ish

rick     tty7     :0                2days /sbin/upstart --user
rick     pts/21   192.168.0.12      4.00s sshd: rick [priv] 
AND THEN LATER ON....
rick     pts/21   192.168.0.12     44.00s sshd: rick [priv]
rick     pts/21   192.168.0.12      1:24  sshd: rick [priv]
rick     pts/21   192.168.0.12      2:04  sshd: rick [priv]

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

} # WishSeconds

GetClient () {
    # Get file modify time of /tmp/mserve_client.time and set delta in $LastClient
    ModifySeconds=$(date -r "$TIME_FN" '+%s')
    if [[ $? -eq 0 ]]; then
        CurrentSeconds=$(date +%s)
        LastClient=$(( CurrentSeconds - ModifySeconds ))
    else
        LastClient="$DECADE"
    fi

} # GetClient

HostShutDownMessage () {

    # Send wall message 60, 30, 15, 10, 5, 3, 2 and 1 minute(s) before shutdown
    # Messages can double up if program running on exactly 60 second wakeup

    [[ $GsSuspendDelay == 0 ]] && return           # System never shuts down
    MinutesLeft=$(( ( GsSuspendDelay / 60 ) - ( IdleSeconds / 60 ) ))
    case $MinutesLeft in
        60|30|15|10|5|3|2|1)
            m "     'wall' broadcast: shutdown in: $MinutesLeft minute(s)."
            wall "If no activity, shutdown in: $MinutesLeft minute(s)." ;;
        0)
            m "Host system shutdown at: $(date)"
            wall "HOST SYSTEM SHUTDOWN at: $(date)" ;;
    esac

} # HostShutDownMessage

SSC_Result=""           # Global context so caller can see result
ScreenSaverCommand () {

    # Send dbus method to screen saver
    local Parm1="$1"    # GetActiveTime, Inhibit, Throttle, Lock, UnThrottle, 
                        # UnInhibit, GetActive, SetActive (requires true), 
                        # SimulateUserActivity,  GetSessionIdleTime (broken!)
    local Parm2="$2"    # Optional, a value like 'true'

    # If parameter 2 not passed force it to be unset, instead of null parm    
    SSC_Result=$(gdbus call --session --dest org.gnome.ScreenSaver \
                 --object-path /org/gnome/ScreenSaver \
                 --method org.gnome.ScreenSaver."$Parm1" ${Parm2:+"$Parm2"})
    m "Screen Saver Command: $Parm1 $Parm2 Result: $SSC_Result"

} # ScreenSaverCommand

CheckToBlankOrLock () {
    ScreenSaverCommand "GetActive"  # Get screen saver active status
    if [[ $SSC_Result == *"false"* ]] ; then  # If screen saver turned off
        if [[ $IdleSeconds -gt $GsBlankDelay ]] ; then  # If it should be on
            m "FORCING SCREEN BLANK (Set screen saver active)"
            ScreenSaverCommand "SetActive" true
        fi
    fi

} # CheckToBlankOrLock

SimulateUserActivity () {
    # Give illusion user typed something
    ScreenSaverCommand "SimulateUserActivity"
    NewIdle="$(xprintidle)" # NewIdle to verify simulation worked.
    [[ $NewIdle -gt 1000 ]] && echo "ERROR: Idle time not reset: $NewIdle"
    CheckToBlankOrLock
} # SimulateUserActivity

main () {
    ParseParameters "$@"
    while : ; do    # Loop forever
        mInit  # Initialize new debug group output
        GsInit  # Get Gnome Settings (Gsettings / Gs)
        GetWish  # Get remote user activity times using 'w -ish'
        GetClient  # Get /tmp/mserve_client.time modification time
        LowestSeconds="$DECADE"  # ten years so first test is lower
        [[ "$LastWish" -lt "$LowestSeconds" ]] && LowestSeconds=$LastWish
        [[ "$LastClient" -lt "$LowestSeconds" ]] && LowestSeconds=$LastClient
        IdleSeconds=$(( $(xprintidle) / 1000 ))  # xprintidle uses milliseconds
        line="IdleSeconds: $IdleSeconds  | LowestSeconds: $LowestSeconds"
        [[ "$LastWish" -lt "$DECADE" ]] && line="$line  | Last Wish: $LastWish"
        [[ "$LastClient" -lt "$DECADE" ]] && line="$line  | Last Client: $LastClient"
        m "$line"

        if [[ $LowestSeconds -lt "$IdleSeconds" ]] ; then
            SimulateUserActivity  # Fake user activity for new $IdleSeconds
        else
            HostShutDownMessage  # Check to send shutdown message
        fi
        sleep "$SLEEP_SECS"
    done
} # main

main "$@"
