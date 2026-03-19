#!/bin/bash

echo " "
echo "ROSARY --==--==--==--===: $(date)"

if [ $# -ne 2 ]; then
echo "Usage: $0 <string> <boolean>"
exit 1
fi

CHANNEL_URL="$1"
ONLY_AUDIO="$2"


echo "CHANNEL_URL set to: $CHANNEL_URL"

#CHANNEL_URL="https://www.youtube.com/@DailyRosaryandPrayerGroup"
# CHANNEL_URL="https://www.youtube.com/@KristinsCrosses"
# "https://www.youtube.com/@thecatholicfaithchannel"
TV_IP="192.168.0.154"

# Generate today's date string in title format (IST assumed on Pi)
TODAY_STR=$(date "+%B %-d")

# Fetch recent videos: title + id
# VIDEO_LINE=$(yt-dlp --flat-playlist --playlist-items 1-3 --print "%(title)s|%(webpage_url)s" "$CHANNEL_URL" | grep "$TODAY_STR" | head -n 1)
VIDEO_LINE=$(yt-dlp --flat-playlist --playlist-items 1-3 --print "%(title)s$%(webpage_url)s$%(duration_string)s" "$CHANNEL_URL" | grep "$TODAY_STR" | grep "Rosary" | head -n 1)


# Safety check
if [ -z "$VIDEO_LINE" ]; then
  echo "!!!!!!!!!!!!! No Rosary video found for date: $TODAY_STR !!!!!!!!!!!!!!"
echo "The Video Line: $VIDEO_LINE"
  
  # If no video found, try again without the "Rosary" filter, in case the title format changed
  VIDEO_LINE=$(yt-dlp --flat-playlist --playlist-items 1 --print "%(title)s|%(webpage_url)s|%(duration_string)s" "$CHANNEL_URL" )
fi

# Extract ID
VIDEO_URL=$(echo "$VIDEO_LINE" | cut -d'$' -f2 | xargs)
DURATION_STR=$(echo "$VIDEO_LINE" | cut -d'$' -f3 | xargs)

IFS=':' read -r minutes seconds <<< "$DURATION_STR"
echo "$VIDEO_URL" "$DURATION_STR"
# exit 0

# Safety check
if [ -z "$VIDEO_URL" ]; then
  echo "!!!!!!!!!!!!! Failsafe also failed:   $VIDEO_LINE!!!!!!!!!!!!!!"
  exit 0
fi

# Connect to TV
/usr/bin/adb connect "$TV_IP"
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

if [ "$ONLY_AUDIO" = "true" ]; then
./AutoTimeTable/AudioOnlyTv.sh
fi

sleep $((minutes * 60 + seconds -28))
adb shell input keyevent 26
echo $?