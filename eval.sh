#!/bin/bash

#==== 1 week evaluator ====
# Runs all possible .json files, even with errors
# REQUIRES micheck_eval/*
# Update SCE, WK, H for scenario, week sequence and history repectively

SCE="n005w4"
WK="1,2,3,3"
H="0"

TARGET_SCRIPT_DIR="mischeck_eval"
TARGET_SCRIPT="run.sh"

#Checking for solution files
json_files=( *.json )   

#Check if files found
if [ ${#json_files[@]} -eq 0 ]; then
    echo "No JSON files found."
    exit 1
fi

shopt -s nullglob   #antiglob

#travel in
cd "$TARGET_SCRIPT_DIR" || { echo "Failed to enter directory $TARGET_DIR"; exit 1; }

for SOL in "${json_files[@]}"; do
    echo "============ RUNNING $SOL ============"

    bash "$TARGET_SCRIPT" "$SCE" "$WK" "$H" "$SOL"
    echo
done