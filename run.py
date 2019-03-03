#!/usr/bin/env python3

import sys
import logging
import tempfile
from platform import system

from gui import gui
import settings


if __name__ == '__main__':
    resolution = {
            'small': (800, 640),
            'medium': (1024, 768),
            'large': (1920, 1080)
            }

    # set default values
    current_resolution = 'medium'
    _loglevel = logging.INFO
    _logfilename = 'baf.log'
    argc = len(sys.argv)
    i = 1
    while (i < argc):
        if sys.argv[i] in ('--log', '--level', '--loglevel', '--log-level'):
            _loglevel = getattr(logging, sys.argv[i+1].upper())
            i += 2
        elif sys.argv[i] in ('--console', '--tty', '--dev', '--test'):
            _logfilename = ''
            i += 1
        elif sys.argv[i] in ('--res', '--resolution'):
            current_resolution = sys.argv[i+1]
            if current_resolution not in resolution:
                print ("unknown resolution : %s" % (sys.argv[i+1]))
                sys.exit(1)
            i += 2
        elif sys.argv[i] in ('-h', '--help'):
            print("usage:")
            print(f"{sys.argv[0]} [--console|--tty] [--level debug] [--resolution small|medium|large]")
            sys.exit()
        else:
            print ("unknown argument : %s" % (sys.argv[i]))
            sys.exit(1)

    if _logfilename == '':
        logging.basicConfig(format='%(asctime)s [%(filename)s] [%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s',
                level=_loglevel)
    else:
        temp_dir = tempfile.gettempdir()
        dir_sep = '\\' if system() == 'Windows' else '/'
        _logfilename = temp_dir + dir_sep + _logfilename
        logging.basicConfig(format='%(asctime)s [%(filename)s] [%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s',
                handlers=[ logging.FileHandler(_logfilename, 'w', 'utf-8') ], level=_loglevel)

    logging.info('Starting B.A.F version {}.{}.{}'.format(
        settings.software['version_major'],
        settings.software['version_minor'],
        settings.software['version_patch']))

    window = gui(resolution, current_resolution)
    window.mainloop()
