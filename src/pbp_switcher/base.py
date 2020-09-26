import os
import json
import subprocess
import shutil
import datetime
import logging
import logging.config

def get_kernel_version():
    p1 = subprocess.Popen(['uname', '-r'], stdout=subprocess.PIPE)
    res = p1.communicate()[0]
    return res.decode('UTF-8').strip('\n')

OPT_ROOT="/opt/pbp_switcher"
SAVE_DIR = f"{OPT_ROOT}/saved_drivers"
KERNEL_VERSION=get_kernel_version()
MODULES_DIR = f"/lib/modules/{KERNEL_VERSION}"
MODULE_RELDIR="kernel/drivers/gpu/drm/evdi"
DRIVER_PATH=os.path.join(MODULES_DIR, MODULE_RELDIR, "evdi.ko")
    
module_logger = None


def setup_logger():
    global module_logger
    if module_logger is not None:
        return module_logger
    logging.config.fileConfig(os.path.join(OPT_ROOT, 'log.conf'))
    module_logger = logging.getLogger()
    return module_logger
    
def get_logger():
    return setup_logger()

def get_dev_logger():
    logger = setup_logger()
    return logging.getLogger('devSupport')

def read_config():
    logger = get_logger()
    dev_logger = get_dev_logger()
    c_path = f'{OPT_ROOT}/pbp_switch_conf.json'
    try:
        with open(c_path) as f:
            buff = f.read()
            dev_logger.debug(f'config file is {buff}')
    except Exception as e:
        print(f'cannot read config file "{c_path}", exception {e}')
        return
    
    config = json.loads(buff)
    dev_logger.debug(f'config  {config}')
    if "op_mode" not in config:
        logger.error(f'config in "{c_path}" not valid, must be a dictionary that contains the key "op_mode"')
        return
    op_mode = config['op_mode']
    good_modes = ('auto', 'pibook', 'hdmi', 'virtual')
    if op_mode not in good_modes:
        logger.error(f'config in "{c_path}" not valid, "op_mode" must be one of {good_modes}, not "{op_mode}"')
        return
    dev_logger.debug(f'op_mode is {op_mode}')
    return config
    
def get_lsusb_lines():
    dev_logger = get_dev_logger()
    p1 = subprocess.Popen(['lsusb',], stdout=subprocess.PIPE)
    ans = p1.communicate()[0]
    ans = ans.decode('UTF-8')
    lines = []
    for line in ans.split('\n'):
        lines.append(line)
        dev_logger.debug(f'lsusb: {line}')
    return lines

def check_for_pi_book():
    dev_logger = get_dev_logger()
    d_string = "Novatek Microelectronics Corp."
    lines = get_lsusb_lines()
    have = False
    detected_by = []
    for line in lines:
        if "DisplayLink" in line:
            have = True
            detected_by.append(line)
        if d_string in line:
            have = True
            detected_by.append(line)
    res = dict(pi_book_pro=have, detected_by=detected_by)
    dev_logger.debug(f'check_for_pi_book yields {res}')
    return res

    
def check_for_hdmi():
    p1 = subprocess.Popen(['tvservice', '-s'], stdout=subprocess.PIPE)
    ans = p1.communicate()[0]
    ans = ans.decode('UTF-8')
    dev_logger = get_dev_logger()
    dev_logger.debug(f'tvservice yields {ans}')
    return dict(tvservice=ans)
    
def have_evdi_driver():
    p1 = subprocess.Popen(['lsmod',], stdout=subprocess.PIPE)
    ans = p1.communicate()[0]
    ans = ans.decode('UTF-8')
    loaded = False
    lines = []
    for line in ans.split('\n'):
        if "evdi" in line:
            lines.append(line)
        if line.startswith('evdi'):
            loaded = True
    # see if the driver file is preset so that it will load on next reboot
    if os.path.exists(DRIVER_PATH):
        have_file = DRIVER_PATH
    else:
        have_file = None
    res = dict(evdi_loaded=loaded, lsmod_lines=lines, evdi_driver_file=have_file)
    dev_logger = get_dev_logger()
    dev_logger.debug(f'evdi detect yields {res}')
    return res

def run_depmod():
    res = None
    try:
        p1 = subprocess.Popen(['depmod', '-a'], stdout=subprocess.PIPE)
        res = p1.communicate()[0].decode('UTF-8')
    except Exception as e:
        logger = get_logger()
        dev_logger = get_dev_logger()
        logger.error(f'Exception running depmod {e}')
        dev_logger.error(f'Exception running depmod {e}')
        raise
    return res
    

def cmp_evdi_driver(saved):
    source = os.path.join(MODULES_DIR, MODULE_RELDIR, 'evdi.ko')
    p1 = subprocess.Popen(['cmp', source,saved], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = p1.communicate()[1].decode('UTF-8')
    dev_logger = get_dev_logger()
    dev_logger.debug(f'Compare of {source} to {saved} got {res}')
    if res.strip() == '':
        return True
    return False
    
def save_evdi_driver():
    dev_logger = get_dev_logger()
    if not os.path.exists(SAVE_DIR):
        dev_logger.debug(f'Making save dir {SAVE_DIR}')
        os.mkdir(SAVE_DIR)
                
    latest = os.path.join(SAVE_DIR, 'latest')
    do_copy = False
    if os.path.exists(latest):
        latest_version = os.path.join(latest, MODULE_RELDIR)
        if os.path.exists(latest_version):
            dev_logger.debug(f'Testing latest saved driver against current')
            cmp_res = cmp_evdi_driver(os.path.join(latest_version, 'evdi.ko'))
            if not cmp_res:
                dev_logger.debug(f'Current driver different than latest saved, saving it as latest')
                do_copy = True
                os.unlink(latest)
    else:
        do_copy = True
    if do_copy:
        source = os.path.join(MODULES_DIR, MODULE_RELDIR)
        now = datetime.datetime.now()
        t_parent = os.path.join(SAVE_DIR, now.isoformat())
        target = os.path.join(t_parent, MODULE_RELDIR)
        dev_logger.debug(f'Saving {source} to {target}')
        shutil.copytree(source, target)
        dev_logger.debug(f'Linking latest to {t_parent}')
        os.symlink(t_parent, os.path.join(SAVE_DIR, 'latest'))

        
def remove_evdi_driver():
    dev_logger = get_dev_logger()
    save_evdi_driver()
    source = os.path.join(MODULES_DIR, MODULE_RELDIR)
    shutil.rmtree(source)
    dev_logger.debug('removed evdi driver file')

    
def restore_evdi_driver():
    dev_logger = get_dev_logger()
    source = os.path.join(SAVE_DIR, 'latest', MODULE_RELDIR)
    target = os.path.join(MODULES_DIR, MODULE_RELDIR)
    dev_logger.debug(f'Restoring evdi driver from {source} to {target}')
    shutil.copytree(source, target)

def get_proc_pid(procname):
    p1 = subprocess.Popen(['pgrep', procname], stdout=subprocess.PIPE)
    res = p1.communicate()[0]
    ans = res.decode('UTF-8').strip('\n')
    if ans == '':
        return None
    return int(ans)

def run_xrandr(extra_args=None):
    command = ['sudo', 'su', '-', 'pi', 'bash', '-c']
    dash_c_items = ['DISPLAY=:0.0', 'xrandr']
    if extra_args is not None:
        dash_c_items += extra_args
    dash_c = ' '.join(dash_c_items)
    command.append(dash_c)
    p1 = subprocess.Popen(command, stdout=subprocess.PIPE)
    res = p1.communicate()[0]
    ans = res.decode('UTF-8')
    if ans.strip() == '':
        ans = None
    return ans

def get_screen_res(raw=None):
    if raw == None:
        raw = run_xrandr()
    if raw == '':
        raise Exception('no data from run_xrandr')
    lines = raw.split('\n')
    items_1 = lines[0].split()
    needed = ['Screen', 'current']
    for x in needed:
        if x not in items_1:
            raise Exception(f'did not find "{x}"\n{raw}')
    pos = items_1.index('current')
    pos += 1
    trip = items_1[pos:pos+3]
    res = ''.join(trip).strip(',')
    return res
    
def get_monitor_res(raw=None, any_connection=False):
    if raw == None:
        raw = run_xrandr()
    if raw == '':
        raise Exception('no data from run_xrandr')
    lines = raw.split('\n')
    # example line
    # HDMI-1 connected 1280x1024+4+8
    # example two line:
    # DVI-I-1 connected (normal left inverted right x axis y axis)
    #    1920x1080     59.72 +  48.00
    line_pos = 1
    for line in lines[1:]:
        if "disconnected" not in line and "connected" in line:
            data = line.split()
            pos = data.index('connected')
            pos += 1
            for word in data[pos:]:
                if "x" not in word:
                    continue
                xy = word.split('+')[0]
                try:
                    x = int(xy.split('x')[0])
                    y = int(xy.split('x')[1])
                    return xy
                except Exception as e:
                    pass
        line_pos += 1
    return None

def capture_monitor_specs(monitor_name, raw=None):
    if raw == None:
        raw = run_xrandr()
    if raw == '':
        raise Exception('no data from run_xrandr')
    lines = raw.split('\n')
    captures = []
    for line in lines[1:]:
        if line.startswith(monitor_name):
            captures.append(line)
        elif not line.startswith(' '):
            if len(captures) > 0:
                return captures
        elif len(captures) > 0:
            captures.append(line)
    return captures

def check_pibook_xrandr_modes():
    raw = run_xrandr()
    mon_name = find_connected_monitor(raw=raw)
    if mon_name != 'DVI-I-1':
        return "not_connected"
    specs = capture_monitor_specs(mon_name, raw=raw)
    mon_res = get_monitor_res(raw=raw)
    if mon_res is None:
        return "no_valid_mode"
    screen_res = get_screen_res(raw=raw)
    if screen_res == mon_res:
        return "ok"
    return "needs_resize"

def find_connected_monitor(raw=None):
    if raw == None:
        raw = run_xrandr()
    if raw == '':
        raise Exception('no data from run_xrandr')
    lines = raw.split('\n')
    # example line, not connected
    # DVI-I-1 disconencted (normal left inverted right x axis y axis)
    # example two line, mode selected:
    # DVI-I-1 connected 1920x1080 (normal left inverted right x axis y axis)
    # example three line, no valid mode:
    # DVI-I-1 connected (normal left inverted right x axis y axis)
    #    1920x1080     59.72 +  48.00
    line_pos = 1
    for line in lines[1:]:
        if "connected" in line:
            return line.split()[0]
    return None

def fix_resolution():
    from compares import compare_classes
    CompareClass = compare_classes[0]
    CC = CompareClass()
    cmpres = CC.compare_to_config('pibook', do_print=False)
    # currently only fixes for pibook, not sure other monitor types
    # need this
    if cmpres['switch_needed'] or cmpres['reboot_needed']:
        return
    # we are using pibook and it should be working
    code = check_pibook_xrandr_modes()
    dev_logger = get_dev_logger()
    if code == "not_connected":
        dev_logger.debug('pibook pro check not connected')
        return
    elif code == "ok":
        dev_logger.debug('pibook pro check screen res matches monitor res')
        return
    elif code == "needs_resize":
        dev_logger.debug('pibook pro check screen does no match monitor res, resizing')
        monitor_res = get_monitor_res()
        run_xrandr(('-s', monitor_res))
        return
    elif code == "no_valid_mode":
        dev_logger.debug('pibook has no valid mode, creating mode')
        # sometimes it gets borked, so fix it with temporary mode
        # create mode
        try:
            run_xrandr(('--newmode','1920x1080_60.00','172.80','1920',
                        '2040', '2248', '2576', '1080',
                        '1081', '1084', '1118', '-HSync', '+Vsync'))
            run_xrandr(('--addmode', 'DVI-I-1', '1920x1080_60.00'))
            run_xrandr(('--output', 'DVI-I-1', '--mode', '1920x1080_60.00'))
        except Exception as e:
            dev_logger.error(f'problem setting new mode with xrandr "{e}"')
            return
        return
    else:
        dev_logger.error(f'no code for check_pibook_xrandr_modes result "{code}"')
  
    
        
