#there are a few funcs stolen from ZetaUtils because it has bloated dependencies

def index_sort(slist,index,sorter):
    slist.sort(lambda x,y:sorter(x[index],y[index]))
    
def compare_domains(a,b):
    www=0
    a = a.strip().split('.')
    b = b.strip().split('.')
    if a[:4]=='www.':
        x = a[4:]    
        www=1
    else:
        x = a
    if b[:4]=='www.':
        y = b[4:]
        www=1
    else:
        y = b
    try:
        domain = cmp(x[-2], y[-2])
    except:
        return cmp(x[-1], y[-1])
    if domain == 0:
        tld = cmp(x[-1], y[-1])
        if tld == 0:
            for i in range(-3,-(min(len(x),len(y))+1),-1):
                if x[i]<y[i]:
                    return -1
                elif x[i]>y[i]:
                    return 1
            if len(x)<len(y):
                return -1
            elif len(x)>len(y):
                return 1
            if www:
                return cmp(a,b)
            return 0
        else:
            return tld
    else:
        return domain
