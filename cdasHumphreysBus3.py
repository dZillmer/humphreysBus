# Title: CDAS Bus Sim v3
# Author: MAJ Devon Zillmer
# Date: 08 FEB 23

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

gStops = [23,24,25,27,26,13,12,8,11,6,2,1,33,32,33,1,2,6,11,8,12,13,26,27,25,24,23,17,50,15,54]
busCapacity = 100
startInterval = 15 #how long between buses
n = len(gStops) #number of stops
def bus8(sEnv,name,start,numPickup,numDropoff,numResidual):
    '''Increasingly complicated bus simulation. Current inputs:
    sEnv: the simPy environment, required for discrete sim to run
    name: so you can keep track of which process you're looking at
    numPickup,numDropoff: vectors of numbers for this bus to PU/DO
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
        stop = gStops[i]
        print('%s driving to stop %d at time %d, with load %d' % (name,stop, sEnv.now,busLoad))
        yield sEnv.timeout(driveInt)
        if ( busLoad<busCapacity or numPickup[i]!=0 or numDropoff[i]>0 ):
            print("%s stopping at stop %d at time %d."%(name,stop,sEnv.now))
            busLoad -= numDropoff[i]
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
                print("     Bus was full! Some passenger turned away at stop %d, time %d. Bus full." % (i,sEnv.now))
            else:
                if busLoad>busMax: maxStop=i
                busMax = max(busMax,busLoad)
                print('     Picking up at time %d. Current load: %d' % (sEnv.now,busLoad ))
        else:
            print('%s Full, continuing from stop %d at time %d' %(name,i, sEnv.now))
        yield sEnv.timeout(stopInt)
    peakUsage.append((name,busMax,maxStop))
    busUse.append(thisBusUse)
    print("%s completed route at time %d, %d left on bus departed." % (name,sEnv.now,busLoad))
    
def bus9(sEnv,name,start,numPickup,doPerCent,numResidual):
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
        stop = gStops[i]
        print('%s driving to stop %d at time %d, with load %d' % (name,stop, sEnv.now,busLoad))
        yield sEnv.timeout(driveInt)
        if ( busLoad<busCapacity or numPickup[i]!=0 or doPerCent[i]>0 ):
            print("%s stopping at stop %d at time %d."%(name,stop,sEnv.now))
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
                print("     Bus was full! Some passenger turned away at stop %d, time %d. Bus full." % (i,sEnv.now))
            else:
                if busLoad>busMax: maxStop=i
                busMax = max(busMax,busLoad)
                print('     Picking up at time %d. Current load: %d' % (sEnv.now,busLoad ))
        else:
            print('%s Full, continuing from stop %d at time %d' %(name,i, sEnv.now))
        yield sEnv.timeout(stopInt)
    peakUsage.append((name,busMax,maxStop))
    busUse.append(thisBusUse)
    print("%s completed route at time %d, %d left on bus departed." % (name,sEnv.now,busLoad))

####################### Script ###############################################

#first import the data
path = "C:\\Users\\devon.zillmer\\OneDrive - West Point\\Documents\\cdas\\humphreysBus\\busData.csv"
countDF = pd.read_csv(path).fillna(0)
countDF['Stop2'] = countDF.apply(lambda row:trim(row),axis=1)
countDF['Stop'] = countDF.apply(lambda row:trim2(row),axis=1)
countDF['dtg'] = pd.to_datetime(countDF.Date + " " + countDF.Time)
stopList = np.sort(countDF.Stop.unique())
#data imported, we now save the average PU/DO data for a particular route
df2=countDF[countDF.Route=="Green"]
riders=df2.ID.unique()
recordPU = []
recordDO = []
record = []
residualPax = []
probDepart = []
for rider in riders:
    tempDF = df2[df2.ID==rider]
    recordPU.append(list(tempDF.Pickup))
    recordDO.append(list(tempDF.Dropoff))
    #print("Rider ",rider,': ',len(tempDF)," rows")    
    tempDF['Count'] = tempDF.Pickup-tempDF.Dropoff
    for i in range(len(tempDF)-1):
        tempDF.iloc[i+1,9]=tempDF.iloc[i,9]+[tempDF.iloc[i+1,9]]
    least = min(tempDF.Count)
    #print(least)
    if least<0: offset=abs(least)
    else: offset=0
    residualPax.append(offset)
    tempDF.Count = tempDF.Count+offset
    tempDF['probDepart'] = 0
    if offset>0: tempDF.iloc[0,10] = tempDF.iloc[0,4]/offset
    else: tempDF.iloc[0,10] = 0
    for i in range(len(tempDF)-1):
        if tempDF.iloc[i,9]>0:
            tempDF.iloc[i+1,10] = tempDF.iloc[i+1,4]/tempDF.iloc[i,9]
    probDepart.append(list(tempDF['probDepart']))
    record.append(list(tempDF.Count[0:31]))
    
# to save raw passenger total data
df3 = pd.DataFrame(record)
df3 = df3.transpose()
avgGreenBus=df3.mean(axis=1)
plt.plot(avgGreenBus)
plt.title("Plot Green Route DATA Average People on Bus, by stop")
plt.ylabel("Average count of Passengers")
plt.xlabel("Stop Element Number")
plt.show

# to save raw average pick-up data
df3 = pd.DataFrame(recordPU)
df3 = df3.transpose()[0:31] #trimming occasional dudes who gave extra data
avgGreenPU=df3.mean(axis=1)

# to save raw average drop-off data
df3 = pd.DataFrame(recordDO)
df3 = df3.transpose()[0:31] #trimming occasional dudes who gave extra data
avgGreenDO=df3.mean(axis=1)
greenResidual = np.mean(residualPax)

#this builds the average vector of probabilities of deparking at a given stop
df3 = pd.DataFrame(probDepart)
df3 = df3.transpose()
departProb=df3.mean(axis=1)
plt.plot(departProb)
plt.title("Plot Green Route DATA 'Alight Probability', by stop")
plt.ylabel("Probability of Debarking")
plt.xlabel("Stop Element Number")
plt.show


# plt.title("Plot Green Route DATA Average People on Bus, by stop")
# plt.ylabel("Average count of Passengers")
# plt.xlabel("Stop Element Number")
# plt.show

#here's a simulation that uses the crude Poisson dropoff Numbers
r.seed(1) # this sets a seed for repeatability
m = 1000 #number of busses
peakUsage = []
busUse = []

env = s.Environment() #create the SimPy environment
for j in range(m):
    busName = 'Bus %s'%(j+1)
    numPickup = [r.poisson(avgGreenPU[x],1)[0] for x in range(len(gStops))]
    numDropoff = [r.poisson(avgGreenDO[x],1)[0] for x in range(len(gStops))]
    env.process(bus8(env,busName,j*startInterval,numPickup,numDropoff,r.poisson(greenResidual,1)[0])) # create m buses, spaced apart by startInterval length
env.run()
peakUsage

df3 = pd.DataFrame(busUse)
df3 = df3.transpose()
avgGreenSim=df3.mean(axis=1)


#For comparison....
plt.plot(avgGreenBus)
plt.plot(avgGreenSim)
plt.title("Plot Green Route SIMULATON (via Poisson dropoff) Average People on Bus, by stop")
plt.ylabel("Average count of Passengers")
plt.xlabel("Stop Element Number")
plt.show




#here's a simulation that uses a percent Dropoff Technique
r.seed(1) # this sets a seed for repeatability
m = 1000 #number of busses
peakUsage = []
busUse = []

env = s.Environment() #create the SimPy environment
for j in range(m):
    busName = 'Bus %s'%(j+1)
    numPickup = [r.poisson(avgGreenPU[x],1)[0] for x in range(len(gStops))]
    env.process(bus9(env,busName,j*startInterval,numPickup,departProb,r.poisson(greenResidual,1)[0])) # create m buses, spaced apart by startInterval length
env.run()

df3 = pd.DataFrame(busUse)
df3 = df3.transpose()
avgGreenSim=df3.mean(axis=1)

#For comparison....
plt.plot(avgGreenBus)
plt.plot(avgGreenSim)
plt.title("Plot Green Route SIMULATON (via ROUND Dropoff) Average People on Bus, by stop")
plt.ylabel("Average count of Passengers")
plt.xlabel("Stop Element Number")
plt.show

avgDiff = np.mean(avgGreenBus-avgGreenSim)
print("The average difference between bus9 sim and reality was around %.2f off." %avgDiff)




























