from CheezeError import CheezeError
from os import linesep
from pprint import pformat

class LocalDNSManager:
    """ provides functionality to manage local DNS using an etc/hosts file """

    etc_hosts = 'hosts'
    ip_list = ['127.0.0.1',]
    ips_constrain = 0

    _hosts = None
    _domain_map = {}
    _ip_map = {}

    def __init__(self):
        pass

    ##
    # Public interface
    ##

    def hosts_list(self):
        """ initialize _hosts and return a data structure for use in zpt """

        self._hosts_init()

        regex = self.filter_get('hosts')
        all_domains = results = self._domain_map.keys()

        if regex not in ['', self.regex_default]:
            import re
            results = []
            for domain in all_domains:
                str_to_search = self._domain_search_str(domain)
                try:
                    found = re.search(regex, str_to_search) != None
                except:
                    import sys
                    self.filter_set("hosts", "regex < %s > has an " % regex \
                                           + "error: %s" % sys.exc_info()[1])
                if found:
                    results.append(domain)
        domains = results
        domains.sort()
        output = []
        for domain in domains:
            output.append({'domain':domain,
                           'ip':self._ip_get(domain),})
        return output

    def _domain_search_str(self, domain):
        """ return a string to be used in regex filtering """
        # we are not implementing 'header:' here since we only have two columns
        # and they are of different types
        return '%s\n%s' % (domain, self._domain_map[domain])


    ##
    # Heavy lifting
    ##

    def _mapping_set(self, domain, ip):
        """ map a domain name to an IP address and vice versa """
        if not (self._valid_ip(ip) or ip ==''):
            raise CheezeError, "The IP address < %s > " % ip \
                             + "is not valid"
        elif not self._valid_domain(domain):
            raise CheezeError, "The domain < %s > " % ip \
                             + "is not valid"
        elif self.ips_constrain and ip in self.ip_list:
            raise CheezeError, "The IP address < %s > " % ip \
                             + "is not within range"
        else:
            # remove domain if it currently exists
            old_ip = ''
            if domain in self._domain_map.keys():
                old_ip = self._domain_map[domain]
                del self._domain_map[domain]
                self._ip_map[old_ip].remove(domain)

            # if that was the only domain on that ip, remove the ip
            if old_ip != '':
                if self._ip_map[old_ip] == []:
                    del self._ip_map[old_ip]

            # now set new mapping if we have one
            if ip != '':
                self._domain_map[domain] = ip
                if ip in self._ip_map.keys():
                    self._ip_map[ip].append(domain)
                else:
                    self._ip_map[ip] = [domain]

    def _hosts_init(self):
        """ initialize our instance w/ data """

        self._hosts_read()
        self._domain_map = {}
        self._ip_map = {}

        for line in self._hosts.split('\n'):
            # we were using linesep to split but were getting bad data
            line = line.replace('\r','').strip()
            if line == '' or line.startswith('#'):
                continue
            elif not line.count(' ') > 0:
                raise CheezeError, "Couldn't parse this line in your " \
                                 + "hosts file: %s" % line
            else:

                # line is parseable

                ip, domains = [foo.strip() for foo in line.split(' ',1)]

                if self.ips_constrain:
                    ip_list = list(self.ip_list)
                    if ip not in ip_list:
                        ip_list.append(ip)
                    self.ip_list = ip_list

                domains = [d.strip() for d in domains.split(' ') \
                                      if d != '']
                self._ip_map[ip] = domains
                for d in domains:
                    if d in self._domain_map.keys():
                        raise CheezeError, "The domain name < %s > " % d \
                                         + "should only appear once"
                    else:

                        # domain is good to go
                        self._domain_map[d] = ip



    def _hosts_read(self):
        """ read a hosts file into mem """
        hosts_file = file(self.etc_hosts)
        self._hosts = hosts_file.read()
        hosts_file.close()

    def _hosts_write(self):
        """ take the _hosts info and format it for storage """

        # first build output
        pattern = '%-17s %s'
        output = []
        for ip in self._ip_map:
            domain_str = ' '.join(self._ip_map[ip])
            output.append(pattern % (ip,domain_str))

        # then write it
        hosts_file = file(self.etc_hosts,'w')
        hosts_file.writelines(linesep.join(output))
        hosts_file.close()


    ##
    # Helpers
    ##

    def _ip_get(self, domain):
        """ given a domain name, return an IP address or None """
        if domain not in self._domain_map.keys():
            return None
        else:
            return self._domain_map[domain]

    def _valid_ip(self, ip):
        """ given an ip address, return a boolean """
        import re

        ip_re = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
              # from http://www.regular-expressions.info/examples.html

        match = re.match(ip_re,ip)

        return match != None

    def _valid_domain(self, domain):
        """ given an domain address, return a boolean """
        return True
