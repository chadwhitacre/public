This is a Zope product for managing multiple Zope instances on a given server 
TTW. The idea is to make Zopes as cheap as possible, in order to streamline both 
development and production hosting. Install a CheapZopeManager on one master 
Zope instance, and install a CheapZope obj on each cheap zope instance (prolly 
do this in your skel).

Theoretically multiple CheapZopeManagers could manage different instance roots. 
You could even implement central mgmt of different Zope software versions on one 
server.

CheapZopeManager

    instance_root
    skel_root
    
    

CheapZopeManager will handle several tasks:

    - creation of new zope instances

    - registering instances with apache



    - registering domains with dns



    - centralized error management

    - per site bandwith, storage, and memory usage 




    - serving up data for zeta client apps, such as an app that would browse and 
    download instances for local dev purposes
