#!/usr/bin/python3
import os
import sys
import json
import time
import datetime
import logging
from base import (get_logger, get_dev_logger, get_proc_pid,
                  run_xrandr, fix_resolution, find_connected_monitor,
                  DRIVER_PATH, OPT_ROOT,
                  have_evdi_driver, restore_evdi_driver, read_config,
                  remove_evdi_driver, run_depmod, get_lsusb_lines,
                  check_for_hdmi)
from compares import compare_classes
from switches import switch_classes

class Switcher(object):

    def __init__(self):
        self.config = read_config()
        # create logger

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

    def check_resolution(self):
        xpid = get_proc_pid('Xorg')
        while xpid is None:
            xpid = get_proc_pid('Xorg')
            time.sleep(1)
        dev_logger = get_dev_logger()
        dev_logger.debug(f'Xorg running at {xpid}')
        time.sleep(2) # let it settle
        xres = None
        count = 0
        limit_seconds = 120
        while xres is None and count < limit_seconds:
            dev_logger.debug(f"running xrandr count={count}")
            try:
                xres = run_xrandr()
                dev_logger.debug(xres)
            except Exception as e:
                dev_logger.error(e)
            time.sleep(1)
            count += 1
        if xres is None:
            dev_logger.error("never got an xrandr output")
            return
        connected = False
        while not connected and count < limit_seconds:
            dev_logger.debug(f"running xrandr count={count}")
            try:
                mon = find_connected_monitor()
                if mon:
                    connected = True
            except Exception as e:
                dev_logger.error(e)
            time.sleep(1)
            count += 1
        if not connected:
            msg = f"no monitor reports as connected after {limit_seconds} seconds"
            dev_logger.error(msg)
            return
        fix_resolution()
        
        
            
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
    parser.add_argument('--write_to_logs', action="store_true", default=False,
                        help=f"Write log messages at each level to each logger then exit")

    
    args = parser.parse_args()
    s = Switcher()
    logger = get_logger()
    dev_logger = get_dev_logger()
    arg_dict = vars(args)
    logger.warning(f'PBP_SWITCHER PROCESS STARTED {arg_dict}')
    dev_logger.warning('PBP_SWITCHER PROCESS STARTED')
    if args.write_to_logs:
        dev_logger.critical('critical message')
        dev_logger.error('error message')
        dev_logger.warning('warn message')
        dev_logger.info('info message')
        dev_logger.debug('debug message')
        logger.critical('critical message')
        logger.error('error message')
        logger.warning('warn message')
        logger.info('info message')
        logger.debug('debug message')
    elif args.update:
        s.do_op(skip_reboot=args.no_reboot, force=args.force)
    elif args.compare:
        s.compare_to_config()
    else:
        # this is the mode that runs on boot, assuming not not_reboot
        res = s.compare_to_config()
        if not res:
            s.do_op(skip_reboot=args.no_reboot)
        s.check_resolution()
    logger.warning('PBP_SWITCHER FINISHED')
    dev_logger.warning('PBP_SWITCHER FINISHED')

            
