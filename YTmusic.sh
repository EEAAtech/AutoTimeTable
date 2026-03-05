# if the video duration is shorter than 2700 seconds (45 mins), it will play another randomly selected video from the same channel
# and will continue playing videos from the channel until 2700 seconds are over.

MUSIC_URL="$1"
total_duration=0


# if the video duration is shorter than 2700 seconds (45 mins), it will play another randomly selected video from the same channel
# and will continue playing videos from the channel until 2700 seconds are over.
total_duration=0
while [ $total_duration -lt 2700 ]; 
do
  
    # Fetch lines for first 50 videos: title|url|duration_string
  VIDEO_LINES=$(yt-dlp \
      --flat-playlist \
      --playlist-items 1-50 \
      --print "%(title)s$%(webpage_url)s$%(duration_string)s" \
      "$MUSIC_URL")


  # Safety check
  if [ -z "$VIDEO_LINES" ]; then
    echo "!!!!!!!!!!!!! No Music video found for URL: $MUSIC_LINE !!!!!!!!!!!!!! $MUSIC_URL"
  fi

  # Pick random line
  RANDOM_LINE=$(echo "$VIDEO_LINES" | shuf -n 1)

  echo "Playing: $RANDOM_LINE at: $(date), On: $total_duration " 
  
  # Extract ID
  VIDEO_URL=$(echo "$RANDOM_LINE" | cut -d'$' -f2 | xargs)
  # Extract duration string and convert to seconds
  DURATION_STR=$(echo "$RANDOM_LINE" | cut -d'$' -f3)

  #Handle case where duration string is in format "1:23:45" (hours:minutes:seconds)
  if [[ "$DURATION_STR" == *:*:* ]]; then
    IFS=':' read -r hours minutes seconds <<< "$DURATION_STR"
    DURATION_SEC=$((hours * 3600 + minutes * 60 + seconds))
  else  # Handle case where duration string is in format "1:23" (minutes:seconds)
    IFS=':' read -r minutes seconds <<< "$DURATION_STR"
    DURATION_SEC=$((minutes * 60 + seconds))
  fi
 

  # Launch YouTube with the correct video
  /usr/bin/adb shell am start \
    -n com.google.android.youtube.tv/com.google.android.apps.youtube.tv.activity.ShellActivity \
    -a android.intent.action.VIEW \
    -d "$VIDEO_URL"

  #If $DURATION_SEC is more than 2700, set it to 2700 so that the loop will end after this video
  if [ $((total_duration + DURATION_SEC)) -gt 2700 ]; then
    DURATION_SEC=$((2700-total_duration))
  fi

  sleep $DURATION_SEC

  total_duration=$((total_duration + DURATION_SEC))
done
