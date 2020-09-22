#!/usr/bin/python3
import os
import sys
import shutil

DIR = os.path.dirname(os.path.abspath(__file__))
from pbp_switcher.base import OPT_ROOT, have_evdi_driver, restore_evdi_driver
if not os.path.exists(OPT_ROOT):
    os.makedirs(OPT_ROOT)
BIN_DIR=os.path.join(OPT_ROOT, 'bin')
if not os.path.exists(BIN_DIR):
    os.makedirs(BIN_DIR)
try:
    res = have_evdi_driver()
    if res['evdi_driver_file'] is None:
        restore_evdi_driver()
except Exception as e:
    print('Got error {e}')
    print('Are you sure you have installed this?')
    sys.exit(1)
   
os.system('systemctl disable pbp_switcher.service')
os.system(f'rm /etc/systemd/system/pbp_switcher.service')
os.system('systemctl daemon-reload')

shutil.rmtree(OPT_ROOT)

