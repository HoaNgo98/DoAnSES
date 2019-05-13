import SES
import Pyro4

numProcess = 15
this = "12"
index = 11
servername = "localhost.dtt." +this
daemon = Pyro4.core.Daemon()
obj = SES.SES(numProcess, index)
uri = daemon.register(obj)
ns = Pyro4.locateNS()
ns.register(servername, uri)

print("process %s started" %this)
daemon.requestLoop()