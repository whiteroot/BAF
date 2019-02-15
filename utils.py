import os
import logging
import tempfile

def get_tld_cache_file():
    temp_dir = tempfile.gettempdir()
    cache_file = temp_dir + os.path.sep + 'baf_tld_cache.txt'
    logging.debug('TLD cache file : {}'.format(cache_file))
    return cache_file

