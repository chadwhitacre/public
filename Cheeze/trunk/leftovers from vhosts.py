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
        "populates the domains pt"
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
