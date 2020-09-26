import json
from base import OPT_ROOT, have_evdi_driver, get_lsusb_lines, check_for_hdmi, get_logger, get_dev_logger

class BaseCompare(object):

    def __init__(self):
        self.modes = None
        self.logger = get_logger()
        self.dev_logger = get_dev_logger()
        
    def load_modes_file(self, path=None):
        if path is None:
            path = f"{OPT_ROOT}/detected_modes.json"
        with open(path) as f:
            buff = f.read()
            self.dev_logger.debug(f'detected modes raw: {buff}')
        self.modes = json.loads(buff)
        self.dev_logger.debug(f'detected modes decoded: {self.modes}')

    def compare_to_config(self, op_mode, do_print=True):
        if self.modes is None:
            self.load_modes_file()
        
        pibook_needed = []
        h_mode = self.modes['queries']["('hdmi',)"]
        p_mode = self.modes['queries']["('pibook',)"]
        for line in p_mode['lsusb']:
            if line not in h_mode['lsusb']:
                pibook_needed.append(line)
        
        self.dev_logger.debug(f'lines to detect pibook {pibook_needed}')
        hdmi_should_not_be = p_mode['check_for_hdmi']['tvservice']
        self.dev_logger.debug(f'not result to detect hdmi {hdmi_should_not_be}')
        can_switch = False
        switch_needed = True
        reboot_needed = True
        if op_mode == "pibook":
            # get the difference between HDMI running with no Pi Book attached, and Pi Book attached
            fp = '\n'.join(pibook_needed)
            msg = f'need to see these lines in lsusb to confirm pi book pro attached: \n{fp}'
            if do_print:
                print(msg)
            else:
                self.logger.info(msg)
            self.dev_logger.debug(msg)
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
                msg = f'did not find all needed lsusb lines, missing: {missing}'
                if do_print:
                    print(msg)
                else:
                    self.logger.info(msg)
                self.dev_logger.debug(msg)
            else:
                can_switch = True
                msg = 'pi book pro attached state properly detected'
                if do_print:
                    print(msg)
                else:
                    self.logger.info(msg)
                self.dev_logger.debug(msg)
                check = have_evdi_driver()
                if check['evdi_loaded'] and check['evdi_driver_file'] is not None:
                    msg = 'evdi driver loaded and staged for loading at next boot'
                    if do_print:
                        print(msg)
                    else:
                        self.logger.info(msg)
                    self.dev_logger.debug(msg)
                    switch_needed = False
                    reboot_needed = False
                else:
                    msg ='evdi driver not ready for next boot, need to install'
                    if do_print:
                        print(msg)
                    else:
                        self.logger.info(msg)
                    self.dev_logger.debug(msg)
                    switch_needed = True
                    if not check['evdi_loaded']:
                        reboot_needed = True
        if op_mode == "hdmi":
            current = check_for_hdmi()
            msg = f'need to ensure that check_for_hdmi does not look like:\n {hdmi_should_not_be}'
            if do_print:
                print(msg)
            else:
                self.logger.info(msg)
            self.dev_logger.debug(msg)
                                

            if hdmi_should_not_be in current['tvservice']:
                msg =f'hdmi does not appear attached, tvservice says:\n {current["tvservice"]}'
                if do_print:
                    print(msg)
                else:
                    self.logger.info(msg)
                self.dev_logger.debug(msg)
            else:
                msg = f'hdmi looks attached, tvservice says:\n {current["tvservice"]}'
                if do_print:
                    print(msg)
                else:
                    self.logger.info(msg)
                self.dev_logger.debug(msg)
                can_switch = True
                check = have_evdi_driver()
                if check['evdi_loaded']:
                    msg ='hdmi is not in use because evdi driver is loaded'
                    switch_needed = True
                else:
                    msg ='hdmi driver is in use because evdi driver is not loaded'
                    switch_needed = False
                    reboot_needed = False
                if check['evdi_driver_file'] is not None:
                    msg = 'hdmi will not be used on reboot because evdi driver will be loaded'
                    switch_needed = True
                    reboot_needed = True
                else:
                    msg = 'hdmi will be used because evdi driver is not configured for load on boot'
                    reboot_needed = True
                if do_print:
                    print(msg)
                else:
                    self.logger.info(msg)
                self.dev_logger.debug(msg)
        elif op_mode == "virtual":
            msg = 'virtual mode does not work with base Raspbian install. If you have arranged some sort of'
            msg += ' headless setup you need to add a Compare and Switch class to support that mode'
            if do_print:
                print(msg)
            else:
                self.logger.info(msg)
            self.dev_logger.debug(msg)
        result = dict(can_switch=can_switch, switch_needed=switch_needed, reboot_needed=reboot_needed)
        self.dev_logger.debug(result)
        return result

compare_classes = [BaseCompare,]
