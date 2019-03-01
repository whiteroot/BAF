KILO = 'k'
MEGA = 'M'


def getMillionList(min_value, max_value, prefix):
    query_list = []
    if prefix == MEGA:
        for i in range(min_value, max_value+1):
            for j in range(10):
                query_list.append( (i, j, prefix) )
    else:
        query_list = [(x, 0, prefix) for x in range(min_value, max_value+1)]
    return query_list
