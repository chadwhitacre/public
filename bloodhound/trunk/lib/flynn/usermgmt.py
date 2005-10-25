#!/usr/bin/env python
"""[Re]create the database if it isn't there, and add a root login.
"""

import sets
import sha
import string
from random import choice
from rdflib import Graph, Namespace, RDF, BNode, URIRef, Literal

from httpy.utils import log

from acn.storage import db, USERS, USERMGMT, acn_users


def passwd(username, password=''):
    """Given a username and possibly a password, reset the password.
    """

    # Digest the password. Create one if necessary.
    # =============================================

    if password == '':
        unambiguous = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789"
        for c in xrange(8):
            password += choice(unambiguous)
    digested = sha.new(password).hexdigest()


    # Remove and re-add a password statement.
    # =======================================

    current = db.triples((USERS[username], USERMGMT["passwd-digest"], None))
    for triple in tuple(current):
        log(65, "removing digested password '%s...'" % triple[2][:20])
        db.remove(triple)
    db.add((USERS[username], USERMGMT["passwd-digest"], Literal(digested)))

    return password


def passget(username):
    """Get a digested password. Return None if there is no statement.
    """
    passwds = tuple(db.objects(USERS[username], USERMGMT['passwd-digest']))
    if len(passwds) == 0:
        return None
    elif len(passwds) == 1:
        return passwds[0]
    else:
        raise StandardError("More than one password.")


def users(role=None):
    """List all users.
    """
    users = sets.Set()
    if role is not None:
        # constrain by role
        role = Literal(role)
        for user_ in db.subjects(USERMGMT['role'], role):
            users.add(user_.rsplit('/', 1)[1])
    else:
        # no constraint
        for triple in db.triples((None, None, None)):
            if triple[0].startswith(acn_users):
                users.add(triple[0].rsplit('/', 1)[1])
    return tuple(sorted(users))


def userdel(username):
    """Delete a user.
    """
    for triple in tuple(db.triples((USERS[username], None, None))):
        log(68, "removing statement where '%s' is the subject" % username)
        db.remove(triple)
    for triple in tuple(db.triples((None, None, USERS[username]))):
        log(68, "removing statement where '%s' is the object" % username)
        db.remove(triple)
    log(62, "removed user '%s'" % username)


def userget(username):
    """Given a username, return a single role and a single password digest.
    """
    roles = tuple(db.objects(USERS[username], USERMGMT["role"]))
    passwds = tuple(db.objects(USERS[username], USERMGMT["passwd-digest"]))
    if len(roles) != 1:
        raise StandardError("User '%s' has more than one role " % username +
                            "-- %s." % str(roles))
    elif len(passwds) != 1:
        raise StandardError("User '%s' has more than one password " % username +
                            "-- %s." % str(passwds))
    return (roles[0], passwds[0])


def userset(username, role):
    """Remove and re-add a role statement.
    """
    current = db.triples((USERS[username], USERMGMT["role"], None))
    for triple in tuple(current):
        log(67, "removing role '%s'" % triple[2])
        db.remove(triple)
    db.add((USERS[username], USERMGMT["role"], Literal(role)))
    log(66, "role for '%s' set to '%s'" % (username, role))


def useradd(username, password='', role='guest'):
    _password = password
    password = passwd(username, password)
    userset(username, role)
    if _password == '':
        return password
