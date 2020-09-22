#!/bin/bash
if [[ $EUID -ne 0 ]]; then
   echo "you must be root or sudo to run this script"
   exit 1
fi
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
echo $DIR

export PYTHONPATH=$DIR/src
/usr/bin/python3 $DIR/install.py
