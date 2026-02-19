#!/bin/bash

CHANNEL_URL="https://www.youtube.com/@thecatholicfaithchannel"
TV_IP="192.168.0.154"

# Generate today's date string in title format (IST assumed on Pi)
TODAY_STR=$(date "+%B %d")

# Fetch recent videos: title + id
VIDEO_LINE=$(yt-dlp \
  --flat-playlist \
  --playlist-items 1-3 \
  --print "%(title)s|%(webpage_url)s" \
  "$CHANNEL_URL" | grep -i "$TODAY_STR" | head -n 1)


# Safety check
if [ -z "$VIDEO_LINE" ]; then
  echo "!!!!!!!!!!!!! No Rosary video found for date: $TODAY_STR !!!!!!!!!!!!!!"
echo $(yt-dlp \
  --flat-playlist \
  --playlist-items 1-3 \
  --print "%(title)s|%(webpage_url)s" \
  "$CHANNEL_URL")
  exit 1
fi

# Extract ID
VIDEO_URL=$(echo "$VIDEO_LINE" | cut -d'|' -f2 | xargs)


echo "ROSARY --==--==--==--===: $(date)"
#echo "$VIDEO_LINE"rm 
echo "$VIDEO_URL"
# exit 0

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

