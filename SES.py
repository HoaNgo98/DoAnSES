from __future__ import print_function
from Message import Message
import time
import Pyro4
import jsonpickle
import threading
@Pyro4.expose
class SES:
    # store time vector of latest messages sent to other process
    sendBuffer={}
    # buffer of messages that cannnot be deliverd due to
    # delays of previous messages 
    pendingBuffer=[]
    # store all received messages
    receivedMessage=[]
    # Identify remote process, implement later
    processCache={}
    # local vector clock
    clock = []
    # Index of current process
    index = None
    # Number of processes 
    numProcesses=None
    lock = threading.RLock()
    def __init__(self, numProcesses, index):
        self.index = index
        self.numProcesses = numProcesses
        self.clock = [0]*numProcesses
    def reset(self):
        self.sendBuffer={}
        self.pendingBuffer=[]
        self.receivedMessage=[]
        self.processCache={}
        self.clock = [0]*self.numProcesses
    def deepcopy(self,copyList):
        if copyList == None:
            return None
        result=[]
        for i in range(len(copyList)):
            result.append(copyList[i])
        return result
    def deepcopyDict(self,copyDict):
        result = {}
        result.update(copyDict)
        return result
    def isDeliveryAllowed(self,message):
        # if (not message.sendBuffer.has_key(self.index)):
        # self.lock.acquire()
        if not (self.index in message.sendBuffer):
            return True
        result = True
        # Copy local clock and compare with the appropriate entry in
        # message sendbuffer
        #CS
        self.lock.acquire()
        localClockCopy = self.deepcopy(self.clock)
        self.lock.release()
        self.increaseLocalClock(localClockCopy)
        # clock vector in message
        messageClock = message.sendBuffer.get(self.index)
        for i in range(0,self.numProcesses):
            if localClockCopy[i] < messageClock[i]:
                return False
        # self.lock.release()
        return result

    # compare two clocks and return maximum value of clock
    def mergeClock(self,clock1, clock2):
        maxClock = []
        for i in range(0,self.numProcesses):
            maxClock.append(max(clock1[i],clock2[i]))
        return maxClock
    # increase local clock by one
    def increaseLocalClock(self, clock):
        # clock.set(self.index, clock.get(self.index)+1)
        self.lock.acquire()
        clock[self.index] +=1
        self.lock.release()
    # Notify received message and recevie
    def processMessage(self,message):
        message.timestamp = time.ctime(time.time())
        print("Deliverd message " + str(message.ID) + " from process " + str(message.srcID) \
            + " data: " + message.data + " at " + message.timestamp)
        self.lock.acquire()
        self.receivedMessage.append(message)
        self.lock.release()

    def deliver(self, message):
        self.processMessage(message)
        self.lock.acquire()
        self.increaseLocalClock(self.clock)
        # update local clock
        # CS 
        # self.lock.acquire()
        self.clock = self.mergeClock(self.clock,message.clock)
        messageBuffer = message.sendBuffer
        # self.lock.acquire()
        for entry in messageBuffer:
            existingValue = self.sendBuffer.get(entry)
            if existingValue == None:
                self.sendBuffer[entry] = messageBuffer[entry]
            else:
                self.sendBuffer[entry] = self.mergeClock(messageBuffer[entry],\
                    self.sendBuffer[entry])
        # self.lock.release()
        # self.lock.release()
        self.lock.release()

    def receive(self,messageJSON):
        message = jsonpickle.decode(messageJSON, keys=True)
        self.lock.acquire()
        print("Received message "+ str(message.ID) +" Content of this pending Buffer ")
        for x in self.pendingBuffer: print("[ %s ]" %x.data)
        # self.lock.release()
        # self.lock.acquire()  
        if (self.isDeliveryAllowed(message)):
            # pass
            self.lock.acquire()
            self.deliver(message)
            self.lock.release()
            delivered = []
            self.lock.acquire()
            for m in self.pendingBuffer:
                if(self.isDeliveryAllowed(m)):
                    self.lock.acquire()
                    self.deliver(m)
                    self.lock.release()
                    delivered.append(m)
            print("Delivered: ",str(delivered))
            self.lock.release()
            self.lock.acquire()
            for i in self.pendingBuffer:
                if (i in delivered):
                    self.pendingBuffer.remove(i)
            self.lock.release()
        else:
            self.lock.acquire()
            self.pendingBuffer.append(message)
            self.lock.release()
        # self.lock.release()        
        self.lock.release()        
    def getProcess(self, servername):
        ns = Pyro4.locateNS()
        uri = ns.lookup(servername)
        print(uri)
        remoteSES = Pyro4.core.Proxy(uri)
        print("URI: %s \n Name: %s" %(uri,servername))
        self.processCache[servername] = uri
        return remoteSES
    def send(self, servername, messageJSON):
        message = jsonpickle.decode(messageJSON, keys=True)
        self.lock.acquire()
        self.increaseLocalClock(self.clock)
        self.lock.release()
        # dest = self.getProcess(servername)
        dest = servername
        self.lock.acquire()
        print("Content of sentBuffer at process " +str(self.index) + \
            " before sending message " + str(message.ID) + ": "+str(self.sendBuffer))
        # print("Vector clock: " + str(self.clock))
        self.lock.release()

        self.lock.acquire()
        message.clock = self.deepcopy(self.clock)
        self.lock.release()

        self.lock.acquire()
        print("Vector clock: " + str(self.clock))
        self.lock.acquire()
        message.sendBuffer = self.deepcopyDict(self.sendBuffer)
        self.lock.release()
        self.lock.release()
        sendMessage = jsonpickle.encode(message, keys=True)
        try:
            self.lock.acquire()
            dest.receive(sendMessage)
            self.lock.release()
            print('Sent OK!')
            self.lock.acquire()
            remoteIndex = dest.getIndex()
            self.lock.acquire()
            self.sendBuffer[remoteIndex] = self.deepcopy(self.clock)
            self.lock.release()
            # self.sendBuffer[dest.getIndex()] = self.deepcopy(self.clock)
            self.lock.release()
        except Exception as e:
            print('Error has occured! '+ str(e))
    def getIndex(self):
        return self.index
    def spamMessage(self,processName,numMessage):
        dest = self.getProcess(processName)
        # dest = processName
        for i in range(numMessage):
            message = Message(i,self.index,dest.getIndex())
            messageJSON = jsonpickle.encode(message, keys=True)
            print("MESSAGE "+ str(i)+" FROM:" + threading.currentThread().getName())
            self.send(dest,messageJSON)
            time.sleep(0.5)
    def run(self, processNames):
        numThread = self.numProcesses - 1
        numMessage = 10
        # t1 = threading.Thread(target=self.spamMessage,args=(processNames[0],numMessage))
        # t2 = threading.Thread(target=self.spamMessage,args=(processNames[1],numMessage))
        # # t3 = threading.Thread(target=self.spamMessage,args=(processNames[1],numMessage))
        # t1.start()
        # t2.start()
        # # t3.start()
        # t1.join()
        # t2.join()
        # # t3.join()
        threads = []
        for i in range(numThread):
            threads.append(threading.Thread(target=self.spamMessage,\
                args=(processNames[i],numMessage)))
        for i in range(numThread):
            threads[i].start()
        for i in range(numThread):
            threads[i].join()


if __name__=='__main__':
    Process1 = SES(15,0)
    Process2 = SES(15,1)
    Process3 = SES(15,2)
    Message1 = Message(1,1,2)
    Message2 = Message(2,2,1)
    Message1JSON = jsonpickle.encode(Message1)
    Message2JSON = jsonpickle.encode(Message2)    
    Process1.run(["localhost.dtt.2","localhost.dtt.3","localhost.dtt.4", "localhost.dtt.5",
    "localhost.dtt.6","localhost.dtt.7","localhost.dtt.8","localhost.dtt.9","localhost.dtt.10",
    "localhost.dtt.11","localhost.dtt.12","localhost.dtt.13","localhost.dtt.14","localhost.dtt.15"])
    # Process2.run(["localhost.dtt.1","localhost.dtt.3"])

    # Process1.run([Process2,Process3])


    





        