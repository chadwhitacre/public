import os,dbm,pprint
from config import *

def bounce_apache():
    os.spawnl(os.P_WAIT,apachectl_path+' graceful')
    return 'restarting apache'

def get_vhosts(www=0):
    data = dbm.open(db_path,'r')
    output = {}
    for vhost in data.keys():
        server = data[vhost]
        if (vhost[:4]=='www.' and www) or vhost[:4]<>'www.':
            output[vhost]=server
    data.close()
    return output

def delete_vhost(vhost,www=1):
    vhosts_dict = get_vhosts(www)
    del(vhosts_dict[vhost])
    if vhosts_dict.has_key('www.'+vhost):
        del(vhosts_dict['www.'+vhost])
    recreate_vhosts(vhosts_dict)

def update_vhosts(vhosts_dict,www=1):
    data = dbm.open(db_path,'w')
    for vhost,server in vhosts_dict.items():
        data[vhost]=server
        if www:
           wwwvhost = 'www.'+vhost
           data[wwwvhost]=server
    data.close()
    return 'updated'

def recreate_vhosts(vhosts_dict,www=1):
    data = dbm.open(db_path,'n')
    for vhost,server in vhosts_dict.items():
        data[vhost]=server
        if vhost[:4]<>'www.' and www:
            wwwvhost = 'www.'+vhost
            data[wwwvhost]=server
    data.close()
    return 'recreated'

def get_servers():
    server_file = open('/usr/local/apache/conf/vhosts/vhost_servers.txt')
    server_list = server_file.read().strip().split('\n')
    server_file.close()
    server_list.sort()
    return server_list                    