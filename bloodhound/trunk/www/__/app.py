"""flynn
"""

import os
import stat
import sys
import urllib

from httpy.DefaultApp import DefaultApplication
from httpy.Response import Response
from httpy.utils import log, parse_body, parse_query

from flynn.authentication import Auth, User
from flynn.storage import db, USERS, USERMGMT
from flynn.usermgmt import passwd, users, useradd, userdel, userget, userset
from zope.pagetemplate.pagetemplatefile import PageTemplateFile



class Application:

    def __repr__(self):
        return "<flynn>"
    __str__ = __repr__


    def close(self):
        """
        """
        log(81, "closing database")
        db.close()


    def respond(self, request):

        # Do some initial validation.
        # ===========================

        if request.method not in ('GET', 'POST'):
            raise Response(501)
        if request.path != '/':
            response = Response(301)
            response.headers['Location'] = '/'
            raise response


        # Security
        # ========

        user = Auth.get_user(request)


        # Only admins are allowed to manage users.
        # ========================================

        if 'wheel' not in user.groups:
            if user.groups == ['nobody']:
                Auth.redirect_to_login()
            else:
                raise Response(403)


        # UI
        # ==

        user_mgmt_form_path = os.path.join(app.__, 'templates', 'users.pt')



        # GET
        # ===
        # Serve the UI form.

        if request.method == 'GET':
            context = {}
            context['users'] = [User(u) for u in users()]
            app.serve_pt(user_mgmt_form_path, request, user, **context)


        # POST
        # ====
        # add, edit, remove

        elif request.method == 'POST':
            log(69, "got post request: <%s>" % request.raw_body)

            post = parse_body(request)
            action = post.getfirst('action', '')


            # add
            # ===

            if action == 'add':
                username = post.getfirst('username', '')
                role = post.getfirst('role', '')

                if username == '':
                    raise Response(400, "No username provided")
                elif role == '':
                    raise Response(400, "No role provided")
                elif username in users():
                    roles, passwords = userget(username)
                    if len(roles) == 0:
                        rolemsg = "(no role assigned)"
                    elif len(roles) == 1:
                        rolemsg = "(role: %s)" % roles[0]
                    else:
                        rolemsg = "(roles: %s)" % ' '.join(roles)

                    raise Response(400, "The username '%s' is already " % username +
                                        "taken %s." % rolemsg)
                else:
                    password = useradd(username, '', role)
                    raise Response(200, "'%s' added, " % username +
                                        "password is '%s'." % password)

            # edit
            # ====

            elif action == 'edit':
                username = post.getfirst('username', '')
                role = post.getfirst('role', '')
                newpass = post.getfirst('newpass', '') == 'true'
                password = post.getfirst('password', '')

                if username == '':
                    raise Response(400, "No username provided.")
                elif role == '':
                    raise Response(400, "No role provided.")
                elif newpass and (password == ''):
                    raise Response(400, "Password change requested but no new "
                                        "password given.")
                else:
                    userset(username, role)
                    if newpass:
                        passwd(username, password)
                    raise Response(200)


            # remove
            # ======

            elif action == 'remove':
                username = post.getfirst('username', '')
                if user.name == username:
                    raise Response(400, "You cannot remove yourself.")
                elif username == '':
                    raise Response(400, "No username provided.")
                else:
                    userdel(username)
                    raise Response(200, "'%s' removed." % username)


            # bad action
            # ==========

            else:
                raise Response(400, "The '%s' action is not supported." % action)


        # Bad request method
        # ==================
        # Safety belt; should be caught in app.py.

        else:
            raise Response(501)

