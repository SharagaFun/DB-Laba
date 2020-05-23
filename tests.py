from DB import DB
import random
import string
import time
import matplotlib.pyplot as plt
from tabulate import tabulate

def randString():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(random.randrange(6,14)))


db = DB()
def getRandStrings(num):
    strings = list()
    for i in range(num):
        strings.append(randString())
    return strings

def fillDB(names, amounts, prices):
    start = time.time()
    for i in range (len(names)):
        db.addRecord({"id": i, "name": names[i], "amount": amounts[i], "price": prices[i]})
    return time.time()-start

def findTest(names):
    start = time.time()
    for i in range (len(names)):
        db.getRecordsByName(names[i])
    return time.time() - start

def delTest(names):
    start = time.time()
    for i in range (len(names)):
        db.delRecordsByName(names[i])
    return time.time() - start

def genStrings(num):
    names = getRandStrings(num)
    amounts = getRandStrings(num)
    prices = getRandStrings(num)
    return names, amounts, prices

testingValues = [1000, 10000, 100000, 1000000]
filltests = list()
findtests = list()
deltests = list()
for i in testingValues:
    db.flushDB()
    names, amounts, prices = genStrings(i)
    filltests.append(fillDB(names, amounts, prices))
    findtests.append(findTest(names))
    deltests.append(delTest(names))

plt.title('Execution time')
plt.xlabel('Sizes')
plt.ylabel('Time')
plt.plot (testingValues, filltests, label = 'Fill')
plt.plot (testingValues, findtests, label='Find')
plt.plot (testingValues, deltests, label='Delete (by name)')
plt.legend(loc='upper left')

testingValues.insert(0, 'Iterations')
filltests.insert(0, 'Fill')
findtests.insert(0, 'Find')
deltests.insert(0, 'Delete (by name)')

print(tabulate([testingValues, filltests, findtests, deltests], tablefmt="github"))
plt.show()