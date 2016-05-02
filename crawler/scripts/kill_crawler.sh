#!/bin/sh

# DO NOT run this script from its current directory. It is meant to be called from crawl.py in the parent directory.
LOG="scripts/logs/kill.log"

# Kill the daemons that were booted
pkill geth > ${LOG} 2>&1
pkill mongo > ${LOG} 2>&1
pkill node > ${LOG} 2>&1



