#!/usr/bin/python3
import os
import json
import datetime
from base import DRIVER_PATH, OPT_ROOT, check_for_pi_book, check_for_hdmi, get_lsusb_lines

inst_msg = """
This tool collects the results of querying the state of USB and HDMI connections in 
order to create a comparison file that can be used by the switcher to 
configure the systeam for the desired monitor.

The results of this tool are placed in "{OPT_ROOT}/detected_modes.json". 
The original contents of that file are also present in "{OPT_ROOT}/default_modes.json".

Here is the recommended process:

1. Ensure that the Pi Book Pro is attached and working. Attach the HDMI monitor but remove
any USB connected devices that may not always be present, such as keyboards, mice, external
USB hubs, etc.

   Reboot

2. Ensure that the Pi Book Pro is still displaying. Run the detection tool:

    pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --pibook_and_hdmi (or -B)

3. Disconnect the HDMI monitor, reboot and run:

    pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --pibook (or -P)

3. R-eattach the HDMI monitor, and configure the system to boot with HDMI selected:

    pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_set_mode.py -H

    pi@raspberrypi:~ sudo /opt/pbp_switcher/bin/pbp_switch.py -u -n --force

    Now reboot.

4. Run the detection tool:

    pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --hdmi_and_pibook (or -b)

5. Disconnect the Pi Book Pro reboot, then run the tool:

    pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --hdmi (or -H)

6. Disconnect the HDMI monitor, reboot and then run the tool (you may have to use SSH to do this):

    pi@raspberrypi:~ /opt/pbp_switcher/bin/pbp_detect.py --virtual (or -V)

"""

def print_instructions():
    
    cols = os.get_terminal_size()[0]
    max_cols = min(cols, 80)

    wordcount = 0
    words = inst_msg.split(' ')
    line = ''
    for word in words:
        wordcount += 1
        if "\n\n" in word:
            x = word.strip('\n\n') 
            if word.startswith('\n\n'):
                print(f'\n')
                line = x + ' '
            elif word.endswith('\n\n'):
                line += x 
                print(f'{line}\n')
                line = ''
            else:
                x,y = word.split('\n\n')
                line += x 
                print(f'{line}\n')
                line = y + ' '
            continue
        word = word.strip('\n')
        if len(line) + len(word) >= max_cols:
            if line != '':
                print(line)
            line = ''
        line += word + ' '

    print(line)
            

def query_state(monitors, stdout=False):
    opts = ("hdmi", "pibook", "virtual")
    for monitor in monitors:
        if monitor not in opts:
            raise Exception('invalid monitor type "{monitor}", should be one of "{opts}"')
        
    fname = f"{OPT_ROOT}/detected_modes.json"
    if os.path.exists(fname):
        with open(fname) as f:
            rdata = f.read()
    else:
        rdata = '{"queries": {}}'
    data = json.loads(rdata)
    q_data = {}
    data['queries'][str(monitors)] = q_data
    q_data['when'] = datetime.datetime.utcnow().isoformat()
    q_data['lsusb'] = get_lsusb_lines()
    for monitor in monitors:
        if monitor == "pibook":
            q_data['check_for_pi_book'] = check_for_pi_book()
            q_data['evdi_driver_path'] = None
            if os.path.exists(DRIVER_PATH):
                q_data['evdi_driver_path'] = DRIVER_PATH
        q_data['check_for_hdmi'] = check_for_hdmi()
    if stdout:
        print(str(monitors))
        print(json.dumps(q_data, indent=4))
    if not stdout:
        with open(fname, 'w') as f:
            f.write(json.dumps(data, indent=4))

if __name__=="__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    help_tail = f"attached state in {OPT_ROOT}/detected_modes.json"
    parser.add_argument('-H', '--hdmi', action="store_true", default=False,
                        help="query state of monitor elements and save as hdmi display " + help_tail)
    parser.add_argument('-P', '--pibook', action="store_true", default=False,
                        help="query state of monitor elements and save as pi book pro " + help_tail)
    parser.add_argument('-B', '--pibook_and_hdmi',
                        action="store_true", default=False,
                        help="query state of monitor elements and save as pi book pro displaying and hdmi attached as well, place data in {OPT_ROOT}/detected_modes.json")
    parser.add_argument('-b', '--hdmi_and_pibook',
                        action="store_true", default=False,
                        help="query state of monitor elements and save as hdmi displaying and pit book pro attached as well, place data in {OPT_ROOT}/detected_modes.json")
    parser.add_argument('-V', '--virtual', action="store_true", default=False,
                        help="query state of monitor elements and save as no monitor " + help_tail)
    parser.add_argument('-i', '--instructions', action="store_true", default=False,
                        help="print instructions for how to use this tool and exit")
    parser.add_argument('-s', '--stdout', action="store_true", default=False,
                        help="Output the detected configuration to stdout instead of updating the file")
    args = parser.parse_args()
    if args.instructions:
        print_instructions()
        parser.print_help()
        sys.exit(0)
    elif args.hdmi:
        if args.pibook or args.virtual:
            print('you must choose state capture for at most one state')
            parser.print_help()
            sys.exit(1)
        print('doing boot state capture for hdmi display')
        query_state(('hdmi',), stdout=args.stdout)
    elif args.pibook:
        if args.virtual:
            print('you must choose state capture for at most one state')
            parser.print_help()
            sys.exit(1)
        print('doing boot state capture for pibook display')
        query_state(('pibook',), stdout=args.stdout)
    elif args.virtual:
        print('doing boot state capture for virtual display')
        query_state(('virtual',), stdout=args.stdout)
    elif args.pibook_and_hdmi:
        print('doing boot state capture for pi book displaying and hdmi attached')
        query_state(('pibook', 'hdmi'), stdout=args.stdout)
    elif args.hdmi_and_pibook:
        print('doing boot state capture for hdmi displaying and pi book  attached')
        query_state(('hdmi', 'pibook'), stdout=args.stdout)
    else:
        print('\n!!! You must choose exactly one of the query options (-H, -P, -B, -b, -V) !!!\n')
        parser.print_help()
        sys.exit(1)
        
    
