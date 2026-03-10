#!/bin/bash



echo " "

# Ensure Bluetooth controller is powered on
# bluetoothctl power on

# Connect to the HT-CT180 speaker
bluetoothctl connect 6C:5A:B5:E0:9D:2B

# Give the speaker time to wake up and establish A2DP
sleep 8

# Clear the current playlist, load the new one, and start playback
/usr/bin/mpc clear 
/usr/bin/mpc load "$1" 
/usr/bin/mpc play 



# --- CONFIGURATION ---
START_VOL=10
END_VOL=75
RAMP_TIME=180 #300        # 5 minutes (in seconds)

# If sys.argv[2] is provided, use it as the play time, otherwise default to 35 minutes
if [ ! -z "$2" ]; then
    PLAY_TIME=$2
else
    PLAY_TIME=2100 # 35 minutes (in seconds)
fi

STEP_TIME=14


echo "Alarm --==--==--==--===: $(date)"

# --- SET INITIAL VOLUME ---
/usr/bin/mpc volume $START_VOL

# --- CALCULATIONS ---
STEPS=$((RAMP_TIME / STEP_TIME))
VOL_STEP=$(( (END_VOL - START_VOL) / STEPS ))
CURRENT_VOL=$START_VOL

echo "Current system time is: $(date)"


# --- VOLUME RAMP ---
for ((i=1; i<=STEPS; i++)); do
    CURRENT_VOL=$((CURRENT_VOL + VOL_STEP))

    /usr/bin/mpc volume $CURRENT_VOL

    sleep $STEP_TIME
done

# --- ENSURE FINAL VOLUME ---
/usr/bin/mpc volume $END_VOL

# --- PLAY FOR 30 MINUTES ---
sleep $PLAY_TIME

# --- STOP PLAYBACK ---
/usr/bin/mpc stop

# --- Disconnect  speaker so it  can auto standby --
bluetoothctl disconnect 6C:5A:B5:E0:9D:2B

