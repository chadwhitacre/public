from citlib import CitServer, Citadel

citserver = CitServer(host, port)
citserver.login()



citadel = Citadel(host, port, username, password)

class CitServer:
    """This is a low-level representation of a Citadel server.

    Our job here is to adapt the Citadel protocol to Python's data types. The
    API corresponds exactly to the Citadel protocol.

    """





class Citadel:
    """



citadel.floors


class Citadel:

    floors = {} # a table of floor objects

    def config

    def echo

    def identify

    def info

    def noop

    def quit

    def qnoop

    def terminate

    def start_tls

    def get_tls_status



class User





class Floor



class Room


class User
