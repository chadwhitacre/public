This is a Zope product for managing multiple Zope instances on a given server 
TTW. It is intended to be installed on one master zope instance that 
will handle all of the admin tasks for all zetaserver instances. It will handle 
several tasks:


    - creation of new zope instances

    - registering instances with apache

    - registering domains with dns

    - centralized error management

    - per site bandwith, storage, and memory usage 

    - serving up data for zeta client apps, such as an app that would browse and 
    download instances for local dev purposes
