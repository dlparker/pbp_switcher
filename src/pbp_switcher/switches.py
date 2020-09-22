import os
import sys
import json
from base import (DRIVER_PATH, OPT_ROOT, have_evdi_driver, restore_evdi_driver, read_config,
                  remove_evdi_driver, run_depmod, get_lsusb_lines, check_for_hdmi)
from compares import compare_classes


class BaseSwitch(object):

    def __init__(self, compare_class=None, skip_reboot=False):
        if compare_class is None:
            CompareClass = compare_classes[0]
        self.skip_reboot = skip_reboot
        self.config = read_config()
        self.comparator = CompareClass()
        

    def switch_to_pibook(self):
        print('restoring evdi driver file and running depmod')
        try:
            restore_evdi_driver()
            run_depmod()
        except Exception as e:
            print(f'switcher encountered a problem, could not restore evdi driver {e}')
            sys.exit(1)

    def switch_to_hdmi(self):
        driver_state = have_evdi_driver()
        try:
            print('saving and deleting evdi driver file and running depmod, reboot required to remove it')
            remove_evdi_driver() # also saves if needed
            run_depmod()
        except Exception as e:
            print(f'switch encountered a problem, could not save and remove evdi driver {e}')
            sys.exit(1)
        
    def switch_to_virtual(self):
        print(f'switch does not have code for virtual op_mode yet')

    def do_op(self, force=False):
        op_mode = self.config['op_mode']
        if op_mode == "auto":
            if force:
                print('Cannot honor force flag when chosen mode is auto')
                return
            first = self.config['prefered']
            print(f'auto mode trying to find a working mode, starting with prefered {first}')
            c_res = self.comparator.compare_to_config(first)
            print(c_res)
            if not c_res['switch_needed'] and not c_res['reboot_needed']:
                print(f'switch found prefered {first} already active and staged, no action required')
                return
            if c_res['can_switch']:
                op_mode = first
                print(f'switch choosing to switch to prefered mode {op_mode}')
            else:
                res = {}
                for mode in ('pibook', 'hdmi', 'virtual'):
                    if mode == first:
                        continue
                    res[mode] = c_res = self.comparator.compare_to_config(mode)
                    if not c_res['switch_needed'] and not c_res['reboot_needed']:
                        print(f'switch found {mode} already active and staged, no action required')
                        return
                # if we got here, then attached device is not ready to go
                op_mode = None
                for mode in res:
                    c_res = res[mode]
                    if c_res['can_switch']:
                        op_mode = mode
                        print(f'auto mode selected {op_mode} as first mode that is ready for switch')
                if op_mode is None:
                    print(f'auto mode cannot locate a mode that is ready for switch')
                    sys.exit(1)

        if not force:
            self.compare_result = self.comparator.compare_to_config(op_mode)
            self.modes = self.comparator.modes
            if not self.compare_result['switch_needed']:
                print(f'switch found {op_mode} already active and staged, no action required')
                return
            if not self.compare_result['can_switch']:
                print(f'requested mode {op_mode} cannot be activated, detection comparison failed')
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
                print('not rebooting though reboot is required')
            else:
                print('rebooting as required')
                os.system('reboot')
            
        

switch_classes = [BaseSwitch,]
