# import json
import jsonpickle
class A(object):
    items = {1:[1,2,3], 2:[4,5,6]}
    def __init__(self, id, name, age):
        self.id = id
        self.name = name
        self.age = age
class Message:
    sendBuffer={1:[1,2,3], 2:[4,5,6]}
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
        self.content = 'Message ' + str(self.ID)

# message = Message(0,1,2)
# messageJSON = jsonpickle.encode(message, keys=True)
# print(messageJSON)
# cloneMessage = jsonpickle.decode(messageJSON, keys=True)
# print(cloneMessage.sendBuffer)
dict1 = {'name':'Hung','age':21}
dict2 = {}
dict2.update(dict1)
# dict2 = dict1
print(dict1)
print(dict2)
if dict2 is dict1 :
    print("Shallow copy")
else:
    print("deep copy")