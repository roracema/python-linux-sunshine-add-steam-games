#!/bin/bash

# --- Configuration ---
SCRIPT_DIR="/home/<USER>/Documents/Projects/python-linux-sunshine-add-steam-games"
LOG_FILE="$SCRIPT_DIR/sunshine_import_log.txt"
PYTHON_BIN="/usr/bin/python3"
# ---------------------

# 1. Wait a moment to ensure the desktop environment is loaded.
sleep 15

# 2. Navigate to the script's directory.
cd "$SCRIPT_DIR"

# 3. Execute the Python script.
#    - 'nohup' prevents termination upon terminal close.
#    - '-u' forces UNBUFFERED output (CRITICAL for logging/debugging).
#    - '>' redirects stdout/stderr to the log file.
#    - '&' runs the job in the background.
nohup "$PYTHON_BIN" -u ./sunshine-games-import.py > "$LOG_FILE" 2>&1 &

# 4. Wait briefly to ensure the background job is fully detached before exiting.
sleep 0.5

exit 0
