========================================
    INTRODUCTION
========================================

Binder is a utility to safely manage a list of domain names for which DNS is to
be provided by a BIND 8 server. Binder assumes that all domains will share the
same SOA, MX records, and other configuration. This shared information is
expected to be in a zone file at namesrvr:/etc/namedb/binder.zone. We store our
list of domains as a pickle in a dat file, and whenever we update this list we
poop out two fragments for inclusion in a named.conf file:

    named.binder.master.conf -- fragment to be included in named.conf on the
    master DNS server; records are of the form:

        zone "example.com" {
                type master;
                file "binder.zone";
        };

    named.binder.slave.conf -- fragment to be included in named.conf on the
    slave DNS server; records are of the form:

        zone "example.com" {
                type slave;
                file "binder.zone";
        };


========================================
    INSTALLATION
========================================

1. Put Binder in your site-packages

2. Create a directory to store your data file, e.g., at /usr/local/binder

3. Create a directory to store your output file, e.g., /home/robot (assuming you
will be using some additional script to take incorporate Binder's output into
BIND).

4. Follow the instructions in bin/binder.
