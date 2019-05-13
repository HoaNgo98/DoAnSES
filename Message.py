from __future__ import print_function
import os
import sys
import Pyro4

@Pyro4.expose
class Message:
    sendBuffer={}
    clock=[]
    ID=None
    srcID=None
    destID=None
    data=''
    delay=0
    timestamp=0
    def __init__(self, id, srcID, destID):
        self.ID = id
        self.srcID = srcID
        self.destID = destID
        self.data = 'Message ' + str(self.ID)