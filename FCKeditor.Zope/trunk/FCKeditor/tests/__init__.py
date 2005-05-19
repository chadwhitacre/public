def dict2tuple(d):
    """convert a dictionary to a sorted list of tuples
    """
    l = [(k, d[k]) for k in d]
    l.sort()
    return l
