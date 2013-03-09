'''
Created on Mar 9, 2013

@author: goof_troop
'''

class LoggingError(Exception):
    """
    General exception raised by Log
    """

    def __init__(self, msg):
        self._message = msg
        Exception.__init__(self, "Loging Error: " + msg)

    def toString(self):
        return self._message