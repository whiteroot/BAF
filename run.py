#!/usr/bin/env python3
# coding: utf8

from gui import gui
import settings

import sys
import tldextract
import logging
import tempfile
from utils import get_tld_cache_file
from platform import system


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
        else:
            print ("unknown argument : %s" % (sys.argv[i]))
            sys.exit(1)

    if _logfilename != '':
        temp_dir = tempfile.gettempdir()
        dir_sep = '\\' if system() == 'Windows' else '/'
        _logfilename = temp_dir + dir_sep + _logfilename

    logging.basicConfig(format='%(asctime)s [%(filename)s] [%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s', filename=_logfilename, level=_loglevel, filemode='w')
    logging.info('Starting B.A.F version {}.{}.{}'.format(
        settings.software['version_major'],
        settings.software['version_minor'],
        settings.software['version_patch']))
    logging.debug('Settings : {} {}'.format(settings.nb_pages_to_scrap, settings.nb_serp_results))

    te = tldextract.TLDExtract(cache_file=get_tld_cache_file())
    try:
        ignored_sites = [te(line.rstrip('\n')).registered_domain for line in open('ignored_sites.txt')]
        logging.info('ignored sites : %s', ignored_sites)
    except:
        ignored_sites = []

    window = gui(resolution, current_resolution, ignored_sites)
    window.mainloop()
