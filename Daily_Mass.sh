#!/bin/bash

echo " "
TV_IP="192.168.0.154"
CHANNEL_URL="https://www.youtube.com/@DailyTVMass"
MUSIC_URL="$1"
# Generate today's date string in title format (IST assumed on Pi)
TODAY_STR=$(date "+%B %-d")

# Fetch recent videos: title + id
VIDEO_LINE=$(yt-dlp \
  --flat-playlist \
  --playlist-items 1-3 \
  --print "%(title)s$%(webpage_url)s$%(duration_string)s" \
  "$CHANNEL_URL" | grep "$TODAY_STR" | head -n 1)


# Safety check
if [ -z "$VIDEO_LINE" ]; then
  echo "!!!!!!!!!!!!! No Mass video found for date: $TODAY_STR !!!!!!!!!!!!!!"
echo $(yt-dlp \
  --flat-playlist \
  --playlist-items 1-3 \
  --print "%(title)s|%(webpage_url)s" \
  "$CHANNEL_URL")
  exit 1
fi

# Extract ID
VIDEO_URL=$(echo "$VIDEO_LINE" | cut -d'$' -f3 | xargs)
DURATION_STR=$(echo "$VIDEO_LINE" | cut -d'$' -f4 | xargs)
IFS=':' read -r minutes seconds <<< "$DURATION_STR"

echo "MASS --==--==--==--===: $(date)"
#echo "$VIDEO_LINE"rm 
echo "$VIDEO_URL"  
# exit 0

# Connect to TV
/usr/bin/adb connect "$TV_IP"
/usr/bin/adb shell input keyevent KEYCODE_SLEEP 
sleep 3

#Force stop Youtube  in case it had crashed earlier on the TV
#/usr/bin/adb shell am force-stop com.google.android.youtube.tv
#sleep 2


# Launch YouTube with the correct video
/usr/bin/adb shell am start \
  -n com.google.android.youtube.tv/com.google.android.apps.youtube.tv.activity.ShellActivity \
  -a android.intent.action.VIEW \
  -d "$VIDEO_URL"


# Handle profile selector (safe)
sleep 5
/usr/bin/adb shell input keyevent KEYCODE_DPAD_CENTER
sleep 2
/usr/bin/adb shell input keyevent KEYCODE_MEDIA_PLAY



# After Mass, Play the News on Radio 4 assuming Mass  get over in 35 mins
sleep $((minutes * 60 + seconds))

# Ensure Bluetooth controller is powered on
# /usr/bin/bluetoothctl power on


# Connect to the HT-CT180 speaker
# /usr/bin/bluetoothctl connect 6C:5A:B5:E0:9D:2B
#sleep 3

/usr/bin/adb connect  "$TV_IP"

# Give time to wake up
sleep 3
./AutoTimeTable/AudioOnlyTv.sh

# Play the music from Youtube
./AutoTimeTable/YTmusic.sh "$MUSIC_URL"

echo "Switching to Radio at: $(date)" 


# Moode needs an output in order to http stream. But it is out of sync, hence set BT speaker volumn to 1
/usr/bin/mpc volume 1

# Clear current MPD queue
/usr/bin/mpc clear

# Add BBC Radio 3 stream
/usr/bin/mpc load BBC3Radio


# Start playback
/usr/bin/mpc play

sleep 3

# Play it on the TV speakers
/usr/bin/adb shell am start -a android.intent.action.VIEW -d "http://192.168.0.133:8031"

# Wait a bit for the tv to setup is browser, then set Audio Only mode o
# sleep 10
# ./AudioOnlyTv.sh


# Clear current MPD queue
# /usr/bin/mpc stop
# /usr/bin/mpc clear

# Add BBC Radio 3 stream
#/usr/bin/mpc load BBC3Radio
#/usr/bin/mpc add http://lsn.lv/bbcradio.m3u8?station=bbc_radio_three&bitrate=96000


# Start playback of some music till 3pm (mum's prayer time)
#/usr/bin/mpc play

sleep 3600

/usr/bin/mpc stop


# --- Disconnect  speaker so it  can auto standby --
# /usr/bin/bluetoothctl disconnect 6C:5A:B5:E0:9D:2B

# -- Put off the TV
/usr/bin/adb shell input keyevent KEYCODE_SLEEP 
