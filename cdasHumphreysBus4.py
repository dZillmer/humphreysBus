# Title: CDAS Bus Sim v4
# Author: MAJ Devon Zillmer
# Date: 23 FEB 23

#Note, these sections are meant to be run IN ORDER, else things may not work properly!

####################### Imports ##############################################
import pandas as pd
import numpy as np
import numpy.random as r
import simpy as s
from matplotlib import pyplot as plt

#Optional, but suppresses the copy warnings...
pd.options.mode.chained_assignment = None

####################### Functions ############################################
def trim(row):
    temp = row['Stop']
    return temp[0:2]

def trim2(row):
    thisOne = row['Stop2']
    if thisOne[-1]=='A':
        return int(thisOne[0])
    else: return int(thisOne)

def bus10(sEnv,name,start,numPickup,doPerCent,numResidual):
    '''Increasingly complicated bus simulation. Current inputs:
    sEnv: the simPy environment, required for discrete sim to run
    name: so you can keep track of which process you're looking at
    numPickup: vectors of numbers for this bus to PU/DO
    doPerCent: avg percent alight at a given stop
    numResidual: residual number of passengers on a bus (calculated)
    Outputs
    - prints to screen major updates
    - records max number riding the bus and if full, when/where
    '''
    driveInt = 2 
    stopInt = 1
    busLoad = numResidual #intended to model the people on the bus initially... but doesn't work
    busMax = 0 #maximum count of people held on this bus at once
    maxStop = None #stop where we achieved the max
    thisBusUse = []
    yield sEnv.timeout(start) #this "delays" the start time
    for i in range(n):
        stop = stopList[i]
        print('%s driving to stop %s at time %d, with load %d' % (name,stop, sEnv.now,busLoad))
        yield sEnv.timeout(driveInt)
        if ( busLoad<busCapacity or numPickup[i]!=0 or doPerCent[i]>0 ):
            print("%s stopping at stop %s at time %d."%(name,stop,sEnv.now))
            busLoad -= np.round(doPerCent[i]*busLoad)
            if busLoad>=0: None
            else: busLoad=0
            print('     Dropping off, new load: %d' % busLoad )
            busLoad += numPickup[i]
            thisBusUse.append(busLoad)
            
            if busLoad == busCapacity:
                busMax = busLoad
                maxStop = i #recording stop where we hit max
                print('     Picking up. Bus is now full at time %d.' % sEnv.now )
            elif busLoad>busCapacity:
                busLoad=busCapacity
                busMax=busCapacity
                maxStop=i
                print("     Bus was full! Some passenger turned away at stop %s, time %d. Bus full." % (stop,sEnv.now))
            else:
                if busLoad>busMax: maxStop=i
                busMax = max(busMax,busLoad)
                print('     Picking up at time %d. Current load: %d' % (sEnv.now,busLoad ))
        else:
            print('%s Full, continuing from stop %s at time %d' %(name,stop, sEnv.now))
        yield sEnv.timeout(stopInt)
    #peakUsage.append((name,busMax,maxStop))
    busUse.append(thisBusUse)
    print("%s completed route at time %d, %d left on bus departed." % (name,sEnv.now,busLoad))

####################### Script ###############################################

### import the data ###
path = "C:\\Users\\devon.zillmer\\OneDrive - West Point\\Documents\\cdas\\humphreysBus\\busData.csv"
#path = "C:\\Users\\devon\\Documents\\workFiles\\cdas\\busData.csv"
countDF = pd.read_csv(path).fillna(0)
countDF['dtg'] = pd.to_datetime(countDF.Date + " " + countDF.Time)
residDict = dict()


### GREEN ROUTE PU numbers / DO percents ###
route="Green"
df2=countDF[countDF.Route==route]
riders=df2.ID.unique()
recordPU = [] #keeping count of pickup numbers
recordDO = [] #keeping track of dropoff numbers
record = [] #for count of people on the bus at one time
residualPax = [] #how many were on the bus when the KATUSA boarded
probDepart = [] # "percent" of people departing at a given stop from those present on the bus
for rider in riders:
    tempDF = df2[df2.ID==rider]
    recordPU.append(list(tempDF.Pickup))
    recordDO.append(list(tempDF.Dropoff))
    #print("Rider ",rider,': ',len(tempDF)," rows")    
    tempDF['Count'] = tempDF.Pickup-tempDF.Dropoff
    for i in range(len(tempDF)-1):
        tempDF.iloc[i+1,8]=tempDF.iloc[i,8]+[tempDF.iloc[i+1,8]]
    least = min(tempDF.Count)
    #print(least)
    if least<0: offset=abs(least)
    else: offset=0
    residualPax.append(offset)
    tempDF.Count = tempDF.Count+offset
    tempDF['probDepart'] = 0
    if offset>0: tempDF.iloc[0,9] = tempDF.iloc[0,4]/offset
    else: tempDF.iloc[0,9] = 0
    for i in range(len(tempDF)-1):
        if tempDF.iloc[i,8]>0:
            tempDF.iloc[i+1,9] = tempDF.iloc[i+1,4]/tempDF.iloc[i,8]
    probDepart.append(list(tempDF['probDepart']))
    record.append(list(tempDF.Count[0:31]))

# to save raw passenger total data
df3 = pd.DataFrame(record)
df3 = df3.transpose()
avgGreenBus=df3.mean(axis=1)
# plt.plot(avgGreenBus)
# plt.title("Plot Green Route DATA Average People on Bus, by stop")
# plt.ylabel("Average count of Passengers")
# plt.xlabel("Stop Element Number")
# plt.show

# to save raw average pick-up data
df3 = pd.DataFrame(recordPU)
df3 = df3.transpose()[0:31] #trimming occasional dudes who gave extra data
avgGreenPU=df3.mean(axis=1)
residDict[route]=np.mean(residualPax)

#this builds the average vector of probabilities of alighting at a given stop
df3 = pd.DataFrame(probDepart)
df3 = df3.transpose()
departProb=df3.mean(axis=1)
# plt.plot(departProb)
# plt.title("Plot Green Route DATA 'Alight Probability', by stop")
# plt.ylabel("Probability of Debarking")
# plt.xlabel("Stop Element Number")
# plt.show

## This section saves the information into my master dictionaries for later use ##
gStops = [23,24,25,27,26,13,12,8,11,6,2,
          1,33,32,33,1,2,6,11,8,12,
          13,26,27,25,24,23,17,50,15,54]
#this creates my oriented list for green route
gOStops = ["23G","24G","25G","27G","26G","13G","12G","8G","11G","6G","2G",
           "1","33A","32G","33G","1","2A","6A","11A","8A","12A",
           "13A","26A","27A","25A","24A","23A","17A","50A","15A","54G"] 
PUdict = dict.fromkeys(gOStops,[]) #building my dictionaries for future use
DOdict = dict.fromkeys(gOStops,[])
for i in range(len(gStops)):
    # PUdict[gOStops[i]] = [avgGreenPU[i]] #recording green averages to oriented stops
    # DOdict[gOStops[i]] = [departProb[i]] #recording green PROBABILITIES to oriented stops
    PUdict[gOStops[i]] = [avgGreenPU[i] for j in range(len(riders))] #this makes a bunch of entries to weight them
    DOdict[gOStops[i]] = [departProb[i] for j in range(len(riders))] #also weighted


### BLUE ROUTE PU numbers / DO percents ###
route="Blue"
df2=countDF[countDF.Route=="Blue"]
riders=df2.ID.unique()
recordPU = [] #keeping count of pickup numbers
recordDO = [] #keeping track of dropoff numbers
record = [] #for count of people on the bus at one time
residualPax = [] #how many were on the bus when the KATUSA boarded
probDepart = [] # "percent" of people departing at a given stop from those present on the bus
#for the alternate ordering of the stops! (blue only... I hope...)
recordPU1 = [] #keeping count of pickup numbers
recordDO1 = [] #keeping track of dropoff numbers
record1 = [] #for count of people on the bus at one time
residualPax1 = [] #how many were on the bus when the KATUSA boarded
probDepart1 = [] # "percent" of people departing at a given stop from those present on the bus
for rider in riders:
    tempDF = df2[df2.ID==rider]
    if list(tempDF.Stop)[0]=='23':
        recordPU.append(list(tempDF.Pickup))
        recordDO.append(list(tempDF.Dropoff))  
        tempDF['Count'] = tempDF.Pickup-tempDF.Dropoff
        for i in range(len(tempDF)-1):
            tempDF.iloc[i+1,8]=tempDF.iloc[i,8]+[tempDF.iloc[i+1,8]]
        least = min(tempDF.Count)
        if least<0: offset=abs(least)
        else: offset=0
        residualPax.append(offset)
        tempDF.Count = tempDF.Count+offset
        tempDF['probDepart'] = 0
        if offset>0: tempDF.iloc[0,9] = tempDF.iloc[0,4]/offset
        else: tempDF.iloc[0,9] = 0
        for i in range(len(tempDF)-1):
            if tempDF.iloc[i,8]>0:
                tempDF.iloc[i+1,9] = tempDF.iloc[i+1,4]/tempDF.iloc[i,8]
        probDepart.append(list(tempDF['probDepart']))
        record.append(list(tempDF.Count))
    elif list(tempDF.Stop)[0]=='1': #to save the other information
        recordPU1.append(list(tempDF.Pickup))
        recordDO1.append(list(tempDF.Dropoff))
        tempDF['Count'] = tempDF.Pickup-tempDF.Dropoff
        for i in range(len(tempDF)-1):
            tempDF.iloc[i+1,8]=tempDF.iloc[i,8]+[tempDF.iloc[i+1,8]]
        least = min(tempDF.Count)
        if least<0: offset=abs(least)
        else: offset=0
        residualPax1.append(offset)
        tempDF.Count = tempDF.Count+offset
        tempDF['probDepart'] = 0
        if offset>0: tempDF.iloc[0,9] = tempDF.iloc[0,4]/offset
        else: tempDF.iloc[0,9] = 0
        for i in range(len(tempDF)-1):
            if tempDF.iloc[i,8]>0:
                tempDF.iloc[i+1,9] = tempDF.iloc[i+1,4]/tempDF.iloc[i,8]
        probDepart1.append(list(tempDF['probDepart']))
        record1.append(list(tempDF.Count))
    else: print("Error! Something went awry, you should check your code...")

### for the 1-starting portion of the route... save raw data
df3 = pd.DataFrame(record1)
df3 = df3.transpose()
avgBlueBus=df3.mean(axis=1)
# plt.plot(avgBlueBus)
# plt.title("Plot Blue1 Route DATA Average People on Bus, by stop")
# plt.ylabel("Average count of Passengers")
# plt.xlabel("Stop Element Number")
# plt.show
# to save raw average pick-up data
df3 = pd.DataFrame(recordPU1)
df3 = df3.transpose()
avgBluePU=df3.mean(axis=1)
#this builds the average vector of probabilities of alighting at a given stop
df3 = pd.DataFrame(probDepart1)
df3 = df3.transpose()
departProb=df3.mean(axis=1)
# plt.plot(departProb)
# plt.title("Plot Blue1 Route DATA 'Alight Probability', by stop")
# plt.ylabel("Probability of Debarking")
# plt.xlabel("Stop Element Number")
# plt.show

bStops = [1,33,32,31,30,29,28,27,26,25,24,23,
          18,19,20,21,22,20,19,18,17,16,15,14,
          13,12,9,10,11,8,7,6,3,4,5,2]
#this creates my oriented list for blue route
bOStops = ["1","33A","32A","13A","30","29A","28A","27A","26A","25A","24A","23A",
           "18A","19A","20A","21","22","20G","19G","18G","17G","16G","15G","14G",
           "13G","12G","9G","10G","11G","8G","7G","6G","3G","4G","5G","2G"] 
bPUdict = dict.fromkeys(bOStops,[]) #build blue dictionary for temporary use
bDOdict = dict.fromkeys(bOStops,[])
bPAXdict = dict.fromkeys(bOStops,[])
for i in range(len(bStops)):
    bPUdict[bOStops[i]] = [20/51*avgBluePU[i]] #weighted average PU numbers
    bDOdict[bOStops[i]] = [20/51*departProb[i]] #weighted average DO probability
    bPAXdict[bOStops[i]] = [avgBlueBus[i] for j in range(20)]

### for the 23-starting portion of the route... save raw data
df3 = pd.DataFrame(record)
df3 = df3.transpose()
avgBlueBus=df3.mean(axis=1)
# to save raw average pick-up data
df3 = pd.DataFrame(recordPU)
df3 = df3.transpose()
avgBluePU=df3.mean(axis=1)
residDict[route]=np.mean(residualPax1+residualPax)
#this builds the average vector of probabilities of alighting at a given stop
df3 = pd.DataFrame(probDepart)
df3 = df3.transpose()
departProb=df3.mean(axis=1)

bStops2 = [23,
          18,19,20,21,22,20,19,18,17,16,15,14,
          13,12,9,10,11,8,7,6,3,4,5,2,
          1,33,32,31,30,29,28,27,26,25,24]
#alternate ordered, oriented list
bOStops2 = ["23A",
           "18A","19A","20A","21","22","20G","19G","18G","17G","16G","15G","14G",
           "13G","12G","9G","10G","11G","8G","7G","6G","3G","4G","5G","2G",
           "1","33A","32A","13A","30","29A","28A","27A","26A","25A","24A"] 
for i in range(len(bStops2)):
    bPUdict[bOStops2[i]].append(31/50*avgBluePU[i])
    bDOdict[bOStops2[i]].append(31/50*departProb[i])
    bPAXdict[bOStops2[i]].extend([avgBlueBus[i] for j in range(31)])


### to merge the blue dictionaries with the green...
avgBlueBus = list()
for stop in bOStops:
    if stop in PUdict.keys(): #add data if already a stop present
        PUdict[stop].extend([np.mean(bPUdict[stop]) for j in range(len(riders))])
        DOdict[stop].extend([np.mean(bDOdict[stop]) for j in range(len(riders))])
    else: #else create a new entry
        PUdict[stop]=[np.mean(bPUdict[stop]) for j in range(len(riders))]
        DOdict[stop]=[np.mean(bDOdict[stop]) for j in range(len(riders))]
    avgBlueBus.append(np.mean(bPAXdict[stop]))



### RED ROUTE PU numbers / DO percents ###
route="Red"
df2=countDF[countDF.Route==route]
riders=df2.ID.unique()
recordPU = [] #keeping count of pickup numbers
recordDO = [] #keeping track of dropoff numbers
record = [] #for count of people on the bus at one time
residualPax = [] #how many were on the bus when the KATUSA boarded
probDepart = [] # "percent" of people departing at a given stop from those present on the bus
#for the alternate ordering of the stops! (blue only... I hope...)
recordPU1 = [] #keeping count of pickup numbers
recordDO1 = [] #keeping track of dropoff numbers
record1 = [] #for count of people on the bus at one time
residualPax1 = [] #how many were on the bus when the KATUSA boarded
probDepart1 = [] # "percent" of people departing at a given stop from those present on the bus
for rider in riders:
    tempDF = df2[df2.ID==rider]
    if list(tempDF.Stop)[0]=='23':
        recordPU.append(list(tempDF.Pickup))
        recordDO.append(list(tempDF.Dropoff))  
        tempDF['Count'] = tempDF.Pickup-tempDF.Dropoff
        for i in range(len(tempDF)-1):
            tempDF.iloc[i+1,8]=tempDF.iloc[i,8]+[tempDF.iloc[i+1,8]]
        least = min(tempDF.Count)
        if least<0: offset=abs(least)
        else: offset=0
        residualPax.append(offset)
        tempDF.Count = tempDF.Count+offset
        tempDF['probDepart'] = 0
        if offset>0: tempDF.iloc[0,9] = tempDF.iloc[0,4]/offset
        else: tempDF.iloc[0,9] = 0
        for i in range(len(tempDF)-1):
            if tempDF.iloc[i,8]>0:
                tempDF.iloc[i+1,9] = tempDF.iloc[i+1,4]/tempDF.iloc[i,8]
        probDepart.append(list(tempDF['probDepart']))
        record.append(list(tempDF.Count))
    elif list(tempDF.Stop)[0]=='1': #to save the other information
        recordPU1.append(list(tempDF.Pickup))
        recordDO1.append(list(tempDF.Dropoff))
        tempDF['Count'] = tempDF.Pickup-tempDF.Dropoff
        for i in range(len(tempDF)-1):
            tempDF.iloc[i+1,8]=tempDF.iloc[i,8]+[tempDF.iloc[i+1,8]]
        least = min(tempDF.Count)
        if least<0: offset=abs(least)
        else: offset=0
        residualPax1.append(offset)
        tempDF.Count = tempDF.Count+offset
        tempDF['probDepart'] = 0
        if offset>0: tempDF.iloc[0,9] = tempDF.iloc[0,4]/offset
        else: tempDF.iloc[0,9] = 0
        for i in range(len(tempDF)-1):
            if tempDF.iloc[i,8]>0:
                tempDF.iloc[i+1,9] = tempDF.iloc[i+1,4]/tempDF.iloc[i,8]
        probDepart1.append(list(tempDF['probDepart']))
        record1.append(list(tempDF.Count))
    else: print("Error! Something went awry, you should check your code...")

### for the 1-starting portion of the route... save raw data
df3 = pd.DataFrame(record1)
df3 = df3.transpose()
avgRedBus=df3.mean(axis=1)
# plt.plot(avgRedBus)
# plt.title("Plot Red1 Route DATA Average People on Bus, by stop")
# plt.ylabel("Average count of Passengers")
# plt.xlabel("Stop Element Number")
# plt.show
#to save raw average pick-up data
df3 = pd.DataFrame(recordPU1)
df3 = df3.transpose()
avgRedPU=df3.mean(axis=1)
#this builds the average vector of probabilities of deparking at a given stop
df3 = pd.DataFrame(probDepart1)
df3 = df3.transpose()
departProb=df3.mean(axis=1)
# plt.plot(departProb)
# plt.title("Plot Red1 Route DATA 'Alight Probability', by stop")
# plt.ylabel("Probability of Debarking")
# plt.xlabel("Stop Element Number")
# plt.show

rStops = [1,2,3,4,5,6,7,8,9,10,11,12,
          13,14,15,16,17,18,19,20,21,22,20,19,
          18,23,24,25,26,27,28,29,30,31,32,33]
#this creates my oriented list for blue route
rOStops = ["1","2A","3A","4A","5A","6A","7A","8A","9A","10A","11A","12A",
           "13A","14A","15A","16A","17A","18A","19A","20A","21","22","20G","19G",
           "18G","23G","24G","25G","26G","27G","28G","29G","30G","31G","32G","33G"] 
rPUdict = dict.fromkeys(rOStops,[]) #build blue dictionary for temporary use
rDOdict = dict.fromkeys(rOStops,[])
rPAXdict = dict.fromkeys(rOStops,[])
for i in range(len(rStops)):
    rPUdict[rOStops[i]] = [9/57*avgBluePU[i]] #weighted average PU numbers
    rDOdict[rOStops[i]] = [9/57*departProb[i]] #weighted average DO probability
    rPAXdict[rOStops[i]] = [avgRedBus[i] for j in range(9)]

### for the 23-starting portion of the route... save raw data
df3 = pd.DataFrame(record)
df3 = df3.transpose()
avgRedBus=df3.mean(axis=1)
# to save raw average pick-up data
df3 = pd.DataFrame(recordPU)
df3 = df3.transpose()
avgRedPU=df3.mean(axis=1)
residDict[route]=np.mean(residualPax1+residualPax)
#this builds the average vector of probabilities of deparking at a given stop
df3 = pd.DataFrame(probDepart)
df3 = df3.transpose()
departProb=df3.mean(axis=1)
rStops2 =  [23,24,25,26,27,28,29,30,31,32,33,
            1,2,3,4,5,6,7,8,9,10,11,12,
            13,14,15,16,17,18,19,20,21,22,20,19,
            18]
#alternate ordered, oriented list
rOStops2 = ["23G","24G","25G","26G","27G","28G","29G","30G","31G","32G","33G",
            "1","2A","3A","4A","5A","6A","7A","8A","9A","10A","11A","12A",
           "13A","14A","15A","16A","17A","18A","19A","20A","21","22","20G","19G",
           "18G"] 
for i in range(len(rStops2)):
    rPUdict[rOStops2[i]].append(48/57*avgRedPU[i])
    rDOdict[rOStops2[i]].append(48/57*departProb[i])
    rPAXdict[rOStops2[i]].extend([avgRedBus[i] for j in range(48)])


### to merge the red dictionary with the existing dictionary...
avgRedBus = list()
for stop in rOStops:
    if stop in PUdict.keys(): #add data if already a stop present
        PUdict[stop].extend([np.mean(rPUdict[stop]) for j in range(len(riders))])
        DOdict[stop].extend([np.mean(rDOdict[stop]) for j in range(len(riders))])
    else: #else create a new entry
        PUdict[stop]=[np.mean(rPUdict[stop]) for j in range(len(riders))]
        DOdict[stop]=[np.mean(rDOdict[stop]) for j in range(len(riders))]
    avgRedBus.append(np.mean(rPAXdict[stop]))

wPUdict = dict()
wDOdict = dict()
for stop in PUdict.keys():
    wPUdict[stop] = np.mean(PUdict[stop])
    wDOdict[stop] = np.mean(DOdict[stop])


### This establishes some generalized dictionaries for easy lookup data
stopDict = dict()
stopDict["Red"] = rOStops
stopDict["Green"] = gOStops
stopDict["Blue"] = bOStops
paxDict = dict()
paxDict["Red"] = avgRedBus
paxDict["Blue"] = avgBlueBus
paxDict["Green"] = avgGreenBus





####  Simulation w/generalized dictionary  ####

route = "Green"
stopList = stopDict[route]
n = len(stopList) #to keep track of how many stops on this route
PUvector = [wPUdict[stop] for stop in stopList]
DOvector = [wDOdict[stop] for stop in stopList]
r.seed(1) # this sets a seed for repeatability
m = 1000 #number of busses
busCapacity = 1000
startInterval = 15 #just to space out my busses
peakUsage = []
busUse = []
env = s.Environment() #create the SimPy environment
for j in range(m):
    busName = '%s Bus %s'%(route,j+1)
    numPickup = [r.poisson(PUvector[x],1)[0] for x in range(n)]
    env.process(bus10(env,busName,j*startInterval,numPickup,DOvector,r.poisson(residDict[route],1)[0])) # create m buses, spaced apart by startInterval length
env.run()
#this saves the bus load information from the simulation and converts into a single vector
df3 = pd.DataFrame(busUse)
df3 = df3.transpose()
avgSim=df3.mean(axis=1)
#For comparison....
plt.plot(paxDict[route])
plt.plot(avgSim)
plt.title("Generalized %s Route Sim. Average Bus Load, by stop"%route)
plt.ylabel("Average count of Passengers")
plt.xlabel("Stop Element Number")
plt.show

avgDiff = np.mean(paxDict[route]-avgSim)
print("The average difference between bus10 sim and reality was around %.2f off." %avgDiff)


route = "Red"
stopList = stopDict[route]
n = len(stopList) #to keep track of how many stops on this route
PUvector = [wPUdict[stop] for stop in stopList]
DOvector = [wDOdict[stop] for stop in stopList]
r.seed(1) # this sets a seed for repeatability
m = 1000 #number of busses
busCapacity = 1000
startInterval = 15 #just to space out my busses
peakUsage = []
busUse = []
env = s.Environment() #create the SimPy environment
for j in range(m):
    busName = '%s Bus %s'%(route,j+1)
    numPickup = [r.poisson(PUvector[x],1)[0] for x in range(n)]
    env.process(bus10(env,busName,j*startInterval,numPickup,DOvector,r.poisson(residDict[route],1)[0])) # create m buses, spaced apart by startInterval length
env.run()
#this saves the bus load information from the simulation and converts into a single vector
df3 = pd.DataFrame(busUse)
df3 = df3.transpose()
avgSim=df3.mean(axis=1)
#For comparison....
plt.plot(paxDict[route])
plt.plot(avgSim)
plt.title("Generalized %s Route Sim. Average Bus Load, by stop"%route)
plt.ylabel("Average count of Passengers")
plt.xlabel("Stop Element Number")
plt.show

avgDiff = np.mean(paxDict[route]-avgSim)
print("The average difference between bus10 sim and reality was around %.2f off." %avgDiff)


route = "Blue"
stopList = stopDict[route]
n = len(stopList) #to keep track of how many stops on this route
PUvector = [wPUdict[stop] for stop in stopList]
DOvector = [wDOdict[stop] for stop in stopList]
r.seed(1) # this sets a seed for repeatability
m = 1000 #number of busses
busCapacity = 1000
startInterval = 15 #just to space out my busses
peakUsage = []
busUse = []
env = s.Environment() #create the SimPy environment
for j in range(m):
    busName = '%s Bus %s'%(route,j+1)
    numPickup = [r.poisson(PUvector[x],1)[0] for x in range(n)]
    env.process(bus10(env,busName,j*startInterval,numPickup,DOvector,r.poisson(residDict[route],1)[0])) # create m buses, spaced apart by startInterval length
env.run()
#this saves the bus load information from the simulation and converts into a single vector
df3 = pd.DataFrame(busUse)
df3 = df3.transpose()
avgSim=df3.mean(axis=1)
#For comparison....
plt.plot(paxDict[route])
plt.plot(avgSim)
plt.title("Generalized %s Route Sim. Average Bus Load, by stop"%route)
plt.ylabel("Average count of Passengers")
plt.xlabel("Stop Element Number")
plt.show

avgDiff = np.mean(paxDict[route]-avgSim)
print("The average difference between bus10 sim and reality was around %.2f off." %avgDiff)


