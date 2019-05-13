from SES import SES
from Message import Message
import Pyro4
import jsonpickle

def deepcopy(copyList):
        if copyList == None:
            return None
        result=[]
        for i in range(len(copyList)):
            result.append(copyList[i])
        return result
if __name__ == '__main__':
    # servername1 = "localhost.dtt.1"
    # servername2 = "localhost.dtt.2"
    # objProcess1 = Pyro4.core.Proxy("PYRONAME:" + servername1)
    # objProcess2 = Pyro4.core.Proxy("PYRONAME:" + servername2)
    # objProcess1.run(servername1)
    with open('process_uri.txt','r') as fi:
       processUris = fi.readlines()
    processUris = [x.strip('"\n') for x in processUris]
    # for i in processUris:
    #     print(i)
    # print(processUris)
    processes = []
    # print("PYRONAME:" + servername2)
    for uri in processUris:
        # print("PYRONAME:" + uri)
        processes.append(Pyro4.core.Proxy("PYRONAME:" + uri))
    # processes[0].run()
    for i in range(15):
        receiverList = deepcopy(processUris)
        # receiverList.update(processUris)
        receiverList.remove(processUris[i])
        # print(receiverList)
        processes[i].run(receiverList)



