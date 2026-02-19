#!/bin/bash

echo " "

# Ensure Bluetooth controller is powered on
# bluetoothctl power on

# Connect to the HT-CT180 speaker
bluetoothctl connect 6C:5A:B5:E0:9D:2B

# Give the speaker time to wake up and establish A2DP
sleep 8


# --- CONFIGURATION ---
START_VOL=10
END_VOL=75
RAMP_TIME=180 #300        # 5 minutes (in seconds)
PLAY_TIME=2100       # 35 minutes (in seconds)
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

#echo $CURRENT_VOL
#/usr/bin/mpc volume

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

