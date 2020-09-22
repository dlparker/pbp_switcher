#!/usr/bin/python3
import os
import sys
import shutil

DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR=os.path.join(DIR, 'src')
sys.path.append(os.path.join(SRC_DIR, 'pbp_switcher'))
from base import OPT_ROOT, save_evdi_driver
from pbp_set_mode import set_mode
if not os.path.exists(OPT_ROOT):
   os.makedirs(OPT_ROOT)
BIN_DIR=os.path.join(OPT_ROOT, 'bin')
if not os.path.exists(BIN_DIR):
   os.makedirs(BIN_DIR)
try:
   save_evdi_driver()
except Exception as e:
   print('Got error {e}')
   print('Are you sure you have Pi Book Pro setup and working?')
   sys.exit(1)
   
MODULE_DIR=os.path.join(SRC_DIR, 'pbp_switcher')

bin_copy = ('base.py', 'compares.py', 'pbp_detect.py',
            'pbp_set_mode.py', 'pbp_switcher.py', 'switches.py')
for fname in bin_copy:
    print(fname)
    shutil.copyfile(os.path.join(MODULE_DIR, fname),
                    os.path.join(BIN_DIR, fname))


shutil.copyfile(os.path.join(MODULE_DIR, "default_modes.json"),
                os.path.join(OPT_ROOT, "default_modes.json"))

shutil.copyfile(os.path.join(MODULE_DIR, "default_modes.json"),
                os.path.join(OPT_ROOT, "detected_modes.json"))


                    

os.system(f'chown -R pi:pi {OPT_ROOT}')
os.system(f'chmod +x {OPT_ROOT}/bin/pbp_switcher.py')
os.system(f'chmod +x {OPT_ROOT}/bin/pbp_detect.py')
os.system(f'chmod +x {OPT_ROOT}/bin/pbp_set_mode.py')
os.system(f'cp  {SRC_DIR}/pbp_switcher.service /etc/systemd/system')
os.system('systemctl daemon-reload')
os.system('systemctl enable pbp_switcher.service')

set_mode('auto', preferred_choice='pibook')
