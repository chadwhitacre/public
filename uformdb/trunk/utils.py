import time, random, md5

def uuidgen(*args):
    """

    Hmmm ... doesn't appear to be a python uuid library. uuidgen.exe from M$
    is hard to get. I am using this script from:

      http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/213761

    Will work for demo purposes but we will need true uuid at some point.

    """

    t = long( time.time() * 1000 )
    r = long( random.random()*100000000000000000L )
    a = random.random()*100000000000000000L
    data = str(t)+' '+str(r)+' '+str(a)+' '+str(args)
    uuid = md5.md5(data).hexdigest()
    return uuid

