from Products.TheZetaServer.interfaces import ITheZetaServer
from Products.ZetaUtils import compare_domains, pformat, index_sort
from Products.TheZetaServer.vh_utils import update_vhosts, \
                                            recreate_vhosts, \
                                            get_vhosts
from AccessControl import ModuleSecurityInfo


class TheZetaServer:

    __implements__ = ITheZetaServer

    def __init__(self):
        pass

    security = ModuleSecurityInfo()

    security.declarePublic('')

    ##
    # vhost wrappers
    ##

    def waxit(self):
        "clear out the vhosts"
        recreate_vhosts({})
        return 'waxed'

    def delete_vhosts(self, vhostname):
        "deletes a vhost given a name"
        request = self.REQUEST
        response = request.RESPONSE
        from Products.ZetaServerAdmin import delete_vhost
        
        delete_vhost(vhostname)
        
        return response.redirect(request.HTTP_REFERER)


    ##
    # Helpers for the domains pt
    ##

    def domains_info(self, troubleshoot=0):
        "deletes a vhost given a name"
        vhosts = self.domains_list()
        index_sort(vhosts,0,compare_domains)
        info = {} 
        info['vhosts'] = vhosts
        server_info = {}
        for domain, server in vhosts:
            domain_list = server_info.get(server,[])
            domain_list.append(domain)
            server_info[server]=domain_list
        info['servers'] = server_info
        if troubleshoot:
            print pformat(info)
            return printed
        else:
            return info

    def domains_list(self):
        "list the available domains"
        from Products.ZetaServerAdmin import get_vhosts
        vhosts = get_vhosts().items()
        domains = []
        print 'hey'
        for vhost in vhosts:
            name, port = vhost
            pattern = '0.zetaserver.com'
            if not name.count(pattern):
                domains.append(vhost)
        return domains



    ##
    # Helpers for the zopes pt
    ##

    def zopes_list(self):
        "list available zopes"
        vhosts = get_vhosts().items()
        zopes = []
        print 'hey'
        for vhost in vhosts:
            name, port = vhost
            pattern = '0.zetaserver.com'
            if name.count(pattern):
                name = name[:-1*(len(pattern)+3)]
                zopes.append((name, port))
        return zopes

    def zopes_info(self, troubleshoot=0):
        "populate the zopes pt"
        avail_ports = [str(x) for x in range(8010,9000,10)]
        zopes = self.zopes_list()
        index_sort(zopes,0,cmp)
        for name, port in zopes:
            if port in avail_ports:
                avail_ports.remove(port)
        info={
        'avail_ports':avail_ports,
        'zopes':zopes,
        }
        return info

    def zopes_process(self):
        "this processes the zopes pt"
        request = self.REQUEST
        response = request.RESPONSE
        form = request.form
        zope = form['zope']
        if zope['name']:
            zs_name = zope['name'] + zope['port'] + '.zetaserver.com'
            update_vhosts({zs_name:zope['port']},www=1)
        return response.redirect('zopes')
