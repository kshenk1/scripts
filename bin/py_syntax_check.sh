#!/bin/bash

FILE="$1"; shift

[ -z "$FILE" ] && echo "I Need the python file to syntax check..." && exit 1

COLOR_RESET="\033[0m"

## Basic colors
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
PURPLE="\033[35m"
CYAN="\033[36m"
WHITE="\033[37m"

FILE_COMPILED="${FILE}c"

PYTHON="$(which python)"
PY_VERSION="$($PYTHON --version 2>&1 | awk ' { print $2 } ')"

echo -e "\nUsing python: ${YELLOW}$PYTHON${COLOR_RESET} (${CYAN}$PY_VERSION${COLOR_RESET})\n"

echo -n "--> Syntax checking: $FILE ... "

OUT="$($PYTHON -m py_compile $FILE 2>&1)"
RETURN="$?"

[ "$RETURN" -ne 0 ] && {
    echo -e "\n${RED}$OUT${COLOR_RESET}"
} || {
    echo -e "${GREEN}Looks OK${COLOR_RESET}"
}

[ -f "$FILE_COMPILED" ] && rm "$FILE_COMPILED"

exit $RETURN
