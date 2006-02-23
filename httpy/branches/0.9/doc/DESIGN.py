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



how do I call security for every request when I have multiple applications? oops?
since I am not storing data in-site, it is crusty to have blog/__/app.py
    better to just have blog.py? or blog/index.py?
so maybe each site should only have one application (=request handler), and we should
    build *.py support right into httpy?

or what if we had a distinction between applications and applings
    application would, yes, be the main request handler, with security/error handling
    applings should all share security and error handling
    but each appling is where you implement MVC. so right now you do ...
        __/site-packages/foo/   model
        __/templates/foo.pt     view
        _styles/foo.css             view
        _scripts/foo.js              view
        foo.py              controller
    but wouldn't it be nicer if you could do ...
        __/site-packages/foo/   model
        foo/foo.pt              view
        foo/foo.css             view
        foo/foo.js              view
        foo/foo.py              controller
maybe app.Application --> responder.Responder? (to distinguish from flynn app)

httpy is intelligible within the following abstraction of the web application
problem:

    protocol -- This is the subproblem that httpy directly addresses; it
                provides an HTTP API for your Python website.

    framework -- hook for security, skinning, error handling, etc.
        on the way in:  request = framework.wrap_request(request)
                        request = framework.Request(request)
        on the way out: response = framework.wrap_response(response)
                        response = framework.Response(response)

    application -- (servlet, appling?)
        if a requested file actually exists on the fs under an appling, do we
        automatically serve it, or do we make the appling responsible for that?

        one common case is going to be support files -- CSS, JavaScript, images,
        etc. -- that are located in the application's directory

        app.py


    data -- maybe stored hierarchically along with applings, or maybe elsewhere


    protocol
    framework
    application
    data

/
/__/
/__/app.py -- default application for publication or hybrid site
/__/framework.py
/app.py -- default application for application site
/foo-app/
/foo-app/app.py -- def respond(request):
/foo-app/style.css
/foo-app/scripts.js




These are the things people are going to write based on httpy:

    couplers
    responders
    frameworks


Do we care to support multiple frameworks per site? I.e., when someone is
assembling a site, are they going to need to use a different framework to support

I want to use responder X for blogging, but responder Y for commerce. responder
X requires framework A, but responder Y requires framework B. Future!!!!

For now, only one framework per site.




/__/framework.py
    class Framework:
/blog/__/framework/



