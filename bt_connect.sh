#!/bin/bash

# Ensure Bluetooth controller is powered on
bluetoothctl power on

# Connect to the HT-CT180 speaker
bluetoothctl connect 6C:5A:B5:E0:9D:2B

# Give the speaker time to wake up and establish A2DP
sleep 8
