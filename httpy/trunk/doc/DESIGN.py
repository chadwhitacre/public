httpy is an HTTP bridge for your Python applications. There are really only
three things going on:

    1. Request -- When an HTTP request comes in off the wire, we give it a
    rather literal object representation and hand that off to your application.

    2. Application -- Because HTTP is a stateless protocol, httpy expects you to
    represent each transaction within your application as an autonomous,
    standalone unit, encapsulated in a Application object.

    3. Response -- When your application has finished processing a transaction,
    it raises a Response object. This carries a payload back up into the httpy
    machinery, which writes back onto the wire.



filesystem website root
url-space app directories
filesystem app directories
filesystem magic directories
app objects (module/package) (could an app be a class in __init__.py?)
transaction objects (class)






Notes

I don't care what language httpy is written in, or if it is compiled or
interpreted. I am much more concerned about:

    the API it exposes to the site developer
    ease of installation (on Win though?)
    speed/robustness


The Stack

    TOP

        9. style (CSS)
        8. client-side logic (ECMAScript)
        7. media (JPEG, Flash, etc.)
        6. markup (XHTML)

        5. response marshalling
            cookies
            sessioning
            headers
            body

        4. applications
            specific apps:
                conversation (forums, discussion mailing lists)
                mailing lists
                content streams (blog, news)
                CMS (end-user-managed publications)
                catalog (i.e., gallery/album)
                commerce ( = catalog/calendar + credit cards)
                calendar
                search
                *publication -- serving a tree of files
            general application needs
                data storage/persistence
                workflow
                security
                user/group management
                versioning
                staging
                error handling
                templating (TAL)
                client-server communication
                user interface
                    browse
                        navigation -- e.g. tree, breadcrumbs, sitemap
                        orderable containers
                    find


        3. request comprehension -- translate a raw request into an object
            querystring
            headers
            cookies
            post body
            sessions

        2. application protocol (HTTP)
        1. transport protocol (TCP/IP)

    BOTTOM

HTTP errata: (but HTML version is auto-generated)
    ust not
    self- elimiting
    ransfer-length
    can arse it
    varriant
    is not be construed
    section 5.1.1 of RFC 2046
