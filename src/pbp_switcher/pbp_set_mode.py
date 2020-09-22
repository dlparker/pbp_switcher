#!/usr/bin/python3
import os
import json
import datetime
from base import OPT_ROOT, DRIVER_PATH

def set_mode(mode, preferred_choice=None):
    config = dict(op_mode=mode)
    if mode == "auto" and preferred_choice is not None:
        config['preferred'] = preferred_choice
    with open(f'{OPT_ROOT}/pbp_switch_conf.json', 'w') as f:
        f.write(json.dumps(config, indent=4))
                
if __name__=="__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hdmi', action="store_true", default=False,
                        help="set switch mode to  hdmi display")
    parser.add_argument('-A', '--auto', action="store_true", default=False,
                        help="set switch mode to auto select display base on what is connected")
    parser.add_argument('-C', '--preferred_choice', required=False,
                        help="set a preferred display for auto select when multiple are possible, must be one of hdmi, pibook, virtual")
    parser.add_argument('-P', '--pibook', action="store_true", default=False,
                        help="set switch mode to pi book pro displayport display")
    parser.add_argument('-V', '--virtual', action="store_true", default=False,
                        help="set switch mode to virtual display")

    args = parser.parse_args()
    if args.hdmi:
        if args.preferred_choice is not None:
            print('--preferred_choice only works with --auto')
            parser.print_help()
            sys.exit(1)
        if args.pibook or args.virtual:
            print('you must choose state capture for at most one state')
            parser.print_help()
            sys.exit(1)
        print('setting switch mode to hdmi display')
        set_mode('hdmi')
    elif args.pibook:
        if args.preferred_choice is not None:
            print('--preferred_choice only works with --auto')
            parser.print_help()
            sys.exit(1)
        if args.virtual:
            print('you must choose state capture for at most one state')
            parser.print_help()
            sys.exit(1)
        print('setting switch mode to pi book pro display')
        set_mode('pibook')
    elif args.virtual:
        if args.preferred_choice is not None:
            print('--preferred_choice only works with --auto')
            parser.print_help()
            sys.exit(1)
        print('doing boot state capture for virtual display')
        print('setting switch mode to virtual display')
        set_mode('virtual')
    elif args.auto:
        set_mode('auto', args.preferred_choice)
    else:
        parser.print_help()
        sys.exit(1)
        
    
