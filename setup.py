#!/usr/bin/env python3
# coding: utf8

import sys
import subprocess

try:
    from tkinter import *
except:
    print('install tkinter package for python 3:')
    print('on Debian, Ubuntu, Mint: sudo apt-get install python3-tk')
    print('on CentOS, RedHat: sudo yum install python3-tkinter')
    print('on other distros, you are supposed to know how to do it ;)')
    sys.exit(1)

cmde = 'python3 -m pip install --user -r requirements.txt'
p = subprocess.run(cmde.split())
