from LocalDNSManager import LocalDNSManager
l = LocalDNSManager()
l._hosts_path = 'hosts'
l._ip_addresses = ['127.0.0.1',
                   '192.168.1.1',
                   '192.168.1.2',
                   '192.168.1.3',
                   '192.168.1.4',
                   '192.168.1.10',
                   '192.168.1.22',
                   '192.168.1.23',
                   '192.168.1.25',
                   '192.168.1.69',
                   '192.168.1.42',
                   '192.168.1.43',
                   '192.168.1.49',
                   '216.17.130.128',
                   '216.17.130.129',
                   '216.17.130.133',
                   '216.17.130.134',
                   '216.17.130.135',
                   '216.17.130.136',
                   '216.17.130.162',
                   ]


def do_hosts_read(test=0):
    if test: print 'TEST _hosts_read()'
    if test: print l._hosts
    if test: print '--------------reading-----------------'
    l._hosts_read()
    if test: print l._hosts
    if test: print '\n'
    print 'hosts successfully read'
    if test: print '\n\n'


def do_hosts_init(test=0):
    if test: print 'TEST _hosts_init()'
    if test: print l._settings
    if test: print '--------------setting-----------------'
    l._hosts_init()
    if test: print l._settings
    if test: print '\n'
    print 'settings successfully inited'
    if test: print '\n\n'

def do_ip_get(test=0):
    print 'TEST ip_get()'
    print l.ip_get('beren1hand')
    print l.ip_get('router')
    print l.ip_get('tesm.us')
    print l.ip_get('tommy')
    print '\n'
    print 'IP addresses successfully gotten'
    print '\n\n'

def do_mapping_set(test=0):
    print 'TEST mapping_set()'
    ip = l.ip_get('beren1hand')
    print l.ip_get('beren1hand')
    print ''

    l.mapping_set('beren1hand','192.168.1.1')
    print l.ip_get('beren1hand')
    print ''

    l.mapping_set('tommy','192.168.1.2')
    print l.ip_get('beren1hand')
    print ''

    l.mapping_set('jimbo','192.168.1.3')
    print l.ip_get('beren1hand')
    print ''

    l.mapping_set('sammy','192.168.1.4')
    print l.ip_get('beren1hand')
    print ''

    l.mapping_set('beren1hand',ip)
    print l.ip_get('beren1hand')
    print ''


def do_hosts_write(test=1):
    print 'TEST hosts_write()'
    l._hosts_write()


do_hosts_read()
do_hosts_init()
do_mapping_set()
do_hosts_write()