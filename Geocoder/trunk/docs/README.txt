given ...

class Alumnus:

    address1
    city
    state
    zip
    

This is what chad wants to do from his scripts/templates:

    context.portal_catalog.searchResults(Type = 'Alumnus',
                                         location = 'central address/ZIP',
                                         miles_out = '50')




So there are at least two layers:

A python layer that does all the heavy lifting. The geocoder can be outside of 
zope, i.e., pure python w/ its own db.

We need a catalog index called 'geocode' or something. This will look for 
various field on objects (e.g., address1, address2, city, state, zip) and will 
build a "geocode id" that gets indexed. Could have more than one address per 
object :/



API for Python Geocoder

def getGeocode():
    """ This takes address info and returns a geocode. This drives our Zope 
    catalog index 
    """
    pass

def getNear():
    """ This takes geocode and radius, and search through all 
    indexed objects and returns those within the radius"""
    pass





