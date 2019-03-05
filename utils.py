import os
import platform

KILO = 'k'
MEGA = 'M'


def getHomeDir():
    if platform.system() == 'Linux':
        return os.environ.get('HOME')
    elif platform.system() == 'Windows':
        return os.environ.get('UserProfile')
    else:
        return ''

def getMillionList(min_value, max_value, prefix):
    query_list = []
    if prefix == MEGA:
        for i in range(min_value, max_value+1):
            for j in range(10):
                query_list.append( (i, j, prefix) )
    else:
        query_list = [(x, 0, prefix) for x in range(min_value, max_value+1)]
    return query_list

def isAccount(link):
    if link.count('/') == 4:
        # https://www.instagram.com/bob/
        return True
    elif link.count('/') == 3:
        # https://www.instagram.com/bob is OK but
        # https://www.instagram.com/ is not
        if link[-1] != '/':
            return True
    else:
        return False
