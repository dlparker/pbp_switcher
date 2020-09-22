#!/usr/bin/python3
import os
import sys
import json
import datetime
from base import (DRIVER_PATH, OPT_ROOT, have_evdi_driver, restore_evdi_driver, read_config,
                  remove_evdi_driver, run_depmod, get_lsusb_lines, check_for_hdmi)
from compares import compare_classes
from switches import switch_classes

class Switcher(object):

    def __init__(self):
        self.config = read_config()

    def compare_to_config(self, compare_class=None):
        if compare_class is None:
            CompareClass = compare_classes[0]
        CC = CompareClass()
        CC.compare_to_config(self.config['op_mode'])
        
    def do_op(self, force=False, switch_class=None, compare_class=None, skip_reboot=False):
        if switch_class is None:
            SwitchClass = switch_classes[0]
        if compare_class is None:
            CompareClass = compare_classes[0]
        SC = SwitchClass(compare_class=compare_class, skip_reboot=skip_reboot)
        SC.do_op(force=force)
            
if __name__=="__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--no_reboot', action="store_true", default=False,
                        help="do switch op but do not reboot")
    parser.add_argument('-u', '--update', action="store_true", default=False,
                        help=f"Update driver configuration to match desired state specified in {OPT_ROOT}/pbp_switch_conf.json")
    parser.add_argument('-c', '--compare', action="store_true", default=False,
                        help=f"Compare current state to desired state specified in {OPT_ROOT}/pbp_switch_conf.json")
    parser.add_argument('--force', action="store_true", default=False,
                        help=f"Force the configures switch regardless of current configuation. WARNING, DANGEROUS")

    
    args = parser.parse_args()
    s = Switcher()
    if args.update:
        s.do_op(skip_reboot=args.no_reboot, force=args.force)
    elif args.compare:
        s.compare_to_config()
    else:
        res = s.compare_to_config()
        if not res:
            s.do_op(skip_reboot=args.no_reboot)
