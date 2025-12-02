#!/opt/homebrew/bin/bash

echo "$(date +'%Y-%m-%d %H:%M:%S') start"

# Detect the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Path to your virtual environment (assuming it's in the same directory)
VIRTUALENV_DIR="$DIR/.venv"

# Activate the virtual environment
source "$VIRTUALENV_DIR/bin/activate"

# Execute the Python script (assuming it's in the same directory as this script)
python "$DIR/cal-to-org.py" > "${ORG_CALENDAR_FILE}"

# Deactivate the virtual environment (optional, since the script ends anyway)
deactivate

echo "$(date +'%Y-%m-%d %H:%M:%S') end"
