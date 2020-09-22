import os
import json
import subprocess
import shutil
import datetime

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
    

def read_config():
    c_path = f'{OPT_ROOT}/pbp_switch_conf.json'
    try:
        with open(c_path) as f:
            buff = f.read()
    except Exception as e:
        print(f'cannot read config file "{c_path}", exception {e}')
        return
    
    config = json.loads(buff)
    if "op_mode" not in config:
        print(f'config in "{c_path}" not valid, must be a dictionary that contains the key "op_mode"')
        return
    op_mode = config['op_mode']
    good_modes = ('auto', 'pibook', 'hdmi', 'virtual')
    if op_mode not in good_modes:
        print(f'config in "{c_path}" not valid, "op_mode" must be one of {good_modes}, not "{op_mode}"')
        return
    return config
    
def get_lsusb_lines():
    p1 = subprocess.Popen(['lsusb',], stdout=subprocess.PIPE)
    ans = p1.communicate()[0]
    ans = ans.decode('UTF-8')
    lines = []
    for line in ans.split('\n'):
        lines.append(line)
    return lines

def check_for_pi_book():
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
    return dict(pi_book_pro=have, detected_by=detected_by)

    
def check_for_hdmi():
    p1 = subprocess.Popen(['tvservice', '-s'], stdout=subprocess.PIPE)
    ans = p1.communicate()[0]
    ans = ans.decode('UTF-8')
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
        
    return dict(evdi_loaded=loaded, lsmod_lines=lines, evdi_driver_file=have_file)

def run_depmod():
    res = None
    try:
        p1 = subprocess.Popen(['depmod', '-a'], stdout=subprocess.PIPE)
        res = p1.communicate()[0].decode('UTF-8')
    except Exception as e:
        res = str(e)
    return res
    

def cmp_evdi_driver(saved):
    source = os.path.join(MODULES_DIR, MODULE_RELDIR, 'evdi.ko')
    p1 = subprocess.Popen(['cmp', source,saved], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = p1.communicate()[1].decode('UTF-8')
    if res.strip() == '':
        return True
    return False
    
def save_evdi_driver():
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)
                
    latest = os.path.join(SAVE_DIR, 'latest')
    do_copy = False
    if os.path.exists(latest):
        latest_version = os.path.join(latest, MODULE_RELDIR)
        if os.path.exists(latest_version):
            cmp_res = cmp_evdi_driver(os.path.join(latest_version, 'evdi.ko'))
            if not cmp_res:
                do_copy = True
                os.unlink(latest)
    else:
        do_copy = True
    if do_copy:
        source = os.path.join(MODULES_DIR, MODULE_RELDIR)
        now = datetime.datetime.now()
        target = os.path.join(SAVE_DIR, now.isoformat(), MODULE_RELDIR)
        shutil.copytree(source, target)
        os.symlink(os.path.join(SAVE_DIR, now.isoformat()), os.path.join(SAVE_DIR, 'latest'))

        
def remove_evdi_driver():
    save_evdi_driver()
    source = os.path.join(MODULES_DIR, MODULE_RELDIR)
    shutil.rmtree(source)

    
def restore_evdi_driver():
    source = os.path.join(SAVE_DIR, 'latest', MODULE_RELDIR)
    target = os.path.join(MODULES_DIR, MODULE_RELDIR)
    shutil.copytree(source, target)

