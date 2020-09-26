import os
import sys
import json
from base import (get_logger, get_dev_logger, DRIVER_PATH, OPT_ROOT,
                  have_evdi_driver, restore_evdi_driver, read_config,
                  remove_evdi_driver, run_depmod, get_lsusb_lines, check_for_hdmi)
from compares import compare_classes


class BaseSwitch(object):

    def __init__(self, compare_class=None, skip_reboot=False):
        if compare_class is None:
            CompareClass = compare_classes[0]
        self.skip_reboot = skip_reboot
        self.config = read_config()
        self.comparator = CompareClass()
        self.logger = get_logger()
        self.dev_logger = get_dev_logger()
        

    def switch_to_pibook(self):
        msg = 'restoring evdi driver file and running depmod'
        print(msg)
        self.dev_logger.debug(msg)
        try:
            restore_evdi_driver()
            run_depmod()
        except Exception as e:
            msg = f'switcher encountered a problem, could not restore evdi driver {e}'
            print(msg)
            self.logger.error(msg)
            self.dev_logger.error(msg)
            sys.exit(1)

    def switch_to_hdmi(self):
        driver_state = have_evdi_driver()
        try:
            msg = 'saving and deleting evdi driver file and running depmod, reboot required to remove it'
            print(msg)
            self.dev_logger.debug(msg)
            remove_evdi_driver() # also saves if needed
            run_depmod()
        except Exception as e:
            msg = f'switch encountered a problem, could not save and remove evdi driver {e}'
            print(msg)
            self.logger.error(msg)
            self.dev_logger.error(msg)
            sys.exit(1)
        
    def switch_to_virtual(self):
        msg = f'switch does not have code for virtual op_mode yet'
        print(msg)
        self.logger.error(msg)
        self.dev_logger.error(msg)

    def do_op(self, force=False):
        op_mode = self.config['op_mode']
        if op_mode == "auto":
            if force:
                msg = 'Cannot honor force flag when chosen mode is auto'
                print(msg)
                self.logger.error(msg)
                self.dev_logger.error(msg)
                return
            first = self.config['preferred']
            msg = f'auto mode trying to find a working mode, starting with preferred {first}'
            print(msg)
            self.dev_logger.debug(msg)
            c_res = self.comparator.compare_to_config(first)
            self.dev_logger.debug(c_res)
            if not c_res['switch_needed'] and not c_res['reboot_needed']:
                msg = f'switch found preferred {first} already active and staged, no action required'
                print(msg)
                self.dev_logger.debug(msg)
                return
            if c_res['can_switch']:
                op_mode = first
                msg = f'switch choosing to switch to preferred mode {op_mode}'
                print(msg)
                self.dev_logger.debug(msg)
            else:
                res = {}
                for mode in ('pibook', 'hdmi', 'virtual'):
                    if mode == first:
                        continue
                    res[mode] = c_res = self.comparator.compare_to_config(mode)
                    if not c_res['switch_needed'] and not c_res['reboot_needed']:
                        msg = f'switch found {mode} already active and staged, no action required'
                        print(msg)
                        self.dev_logger.debug(msg)
                        return
                # if we got here, then attached device is not ready to go
                op_mode = None
                for mode in res:
                    c_res = res[mode]
                    if c_res['can_switch']:
                        op_mode = mode
                        msg =f'auto mode selected {op_mode} as first mode that is ready for switch'
                        print(msg)
                        self.dev_logger.debug(msg)
                if op_mode is None:
                    msg = f'auto mode cannot locate a mode that is ready for switch'
                    print(msg)
                    self.logger.error(msg)
                    self.dev_logger.error(msg)
                    sys.exit(1)

        if not force:
            self.compare_result = self.comparator.compare_to_config(op_mode)
            self.modes = self.comparator.modes
            if not self.compare_result['switch_needed']:
                msg = f'switch found {op_mode} already active and staged, no action required'
                print(msg)
                self.dev_logger.debug(msg)
                return
            if not self.compare_result['can_switch']:
                msg = f'requested mode {op_mode} cannot be activated, detection comparison failed'
                print(msg)
                self.dev_logger.debug(msg)
                return
        else:
            self.compare_result = dict()
            self.compare_result['reboot_needed'] = True
            self.compare_result['can_switch'] = True
            self.compare_result['switch_needed'] = True
            
        if op_mode == "auto":
            self.auto_switch()
        elif op_mode == "pibook":
            self.switch_to_pibook()
        elif op_mode == "hdmi":
            self.switch_to_hdmi()
        elif op_mode == "virtual":
            self.switch_to_virtual()
        if self.compare_result['reboot_needed']:
            if self.skip_reboot:
                msg = 'not rebooting though reboot is required'
                print(msg)
                self.dev_logger.debug(msg)
            else:
                msg = 'rebooting as required'
                print(msg)
                self.dev_logger.debug(msg)
                self.logger.warning(msg)
                self.logger.warning('PBP_SWITCHER FINISHED')
                self.dev_logger.warning('PBP_SWITCHER FINISHED')
                os.system('reboot')
            
        

switch_classes = [BaseSwitch,]
