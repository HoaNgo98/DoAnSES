import SES
import Pyro4

# Pyro4.config.SERIALIZER = 'pickle'
# Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')
numProcess = 15
this = "1"
index = 0
servername = "localhost.dtt." +this
daemon = Pyro4.core.Daemon()
obj = SES.SES(numProcess, index)
uri = daemon.register(obj)
ns = Pyro4.locateNS()
ns.register(servername, uri)

print("process %s started" %this)
daemon.requestLoop()
