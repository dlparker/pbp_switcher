import json
from base import OPT_ROOT, have_evdi_driver, get_lsusb_lines, check_for_hdmi

class BaseCompare(object):

    def __init__(self):
        self.modes = None

    def load_modes_file(self, path=None):
        if path is None:
            path = f"{OPT_ROOT}/detected_modes.json"
        with open(path) as f:
            buff = f.read()
        self.modes = json.loads(buff)

    def compare_to_config(self, op_mode):
        if self.modes is None:
            self.load_modes_file()
        
        pibook_needed = []
        h_mode = self.modes['queries']["('hdmi',)"]
        p_mode = self.modes['queries']["('pibook',)"]
        for line in p_mode['lsusb']:
            if line not in h_mode['lsusb']:
                pibook_needed.append(line)
        hdmi_should_not_be = p_mode['check_for_hdmi']['tvservice']
        can_switch = False
        switch_needed = True
        reboot_needed = True
        if op_mode == "pibook":
            # get the difference between HDMI running with no Pi Book attached, and Pi Book attached
            fp = '\n'.join(pibook_needed)
            print(f'need to see these lines in lsusb to confirm pi book pro attached: \n{fp}')
            lsusb = get_lsusb_lines()
            missing = []
            for line in pibook_needed:
                # lets just look for the ID portion, since the device numbers can change
                tmp = line.split('ID')
                ID = tmp[1].strip().split()[0]
                found = False
                for cmpline in lsusb:
                    if ID in cmpline:
                        found = True
                        break
                if not found:
                    missing.append(ID)
            if len(missing) > 0:
                print(f'did not find all needed lsusb lines, missing: {missing}')
            else:
                can_switch = True
                print('pi book pro attached state properly detected')
                check = have_evdi_driver()
                if check['evdi_loaded'] and check['evdi_driver_file'] is not None:
                    print('evdi driver loaded and staged for loading at next boot')
                    switch_needed = False
                    reboot_needed = False
                else:
                    print('evdi driver not ready for next boot, need to install')
                    switch_needed = True
                    if not check['evdi_loaded']:
                        reboot_needed = True
        if op_mode == "hdmi":
            current = check_for_hdmi()
            print(f'need to ensure that check_for_hdmi does not look like:\n {hdmi_should_not_be}')
            if hdmi_should_not_be in current['tvservice']:
                print(f'hdmi does not appear attached, tvservice says:\n {current["tvservice"]}')
            else:
                print(f'hdmi looks attached, tvservice says:\n {current["tvservice"]}')
                can_switch = True
                check = have_evdi_driver()
                if check['evdi_loaded']:
                    print('hdmi is not in use because evdi driver is loaded')
                    switch_needed = True
                else:
                    print('hdmi driver is in use because evdi driver is not loaded')
                    switch_needed = False
                    reboot_needed = False
                if check['evdi_driver_file'] is not None:
                    print('hdmi will not be used on reboot because evdi driver will be loaded')
                    switch_needed = True
                    reboot_needed = True
                else:
                    print('hdmi will be used because evdi driver is not configured for load on boot')
                    reboot_needed = True
        elif op_mode == "virtual":
            msg = 'virtual mode does not work with base Raspbian install. If you have arranged some sort of'
            msg += ' headless setup you need to add a Compare and Switch class to support that mode'
            print(msg)
        result = dict(can_switch=can_switch, switch_needed=switch_needed, reboot_needed=reboot_needed)
        return result

compare_classes = [BaseCompare,]
