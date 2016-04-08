#!/bin/sh

# Kill the daemons that were booted
echo "Killing geth..."
pkill geth > logs/kill.txt 2>&1
echo "Killing mongo..."
pkill mongo > logs/kill.txt 2>&1
echo "Killing node..."
pkill node > logs/kill.txt 2>&1
echo "Kill success!\n"



