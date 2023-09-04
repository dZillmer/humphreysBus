# Title: CDAS SymPy Intro
# Author: MAJ Devon Zillmer
# Date: 19 OCT 22

####################### Imports ##############################################
import simpy as s
import random as r
import numpy as np

####################### Functions ############################################
def bus(simpy_environment):
    '''Simple Simpy bus simulation'''
    driving_duration = 5 #time taken to drive between two stops in this neighbourhood
    stopping_duration = 10
    for i in range(15):
        print('Start driving to bus stop %d at time %d' % (i, simpy_environment.now ))
        yield simpy_environment.timeout(driving_duration)
        print('Stopping to pick up commuters at bus stop %d at time %d' % (i, simpy_environment.now ))
        yield simpy_environment.timeout(stopping_duration)
        
def bus_improved(simpy_environment):
        '''Improved Bus simulation'''
        drive_times = [r.randint(5, 15) for _ in range(15) ] #14 driving times
        for i in range(15):
            print('Driving to bus stop %d at time %d' % (i, simpy_environment.now))
            yield simpy_environment.timeout(drive_times[i])
            stop_time = r.randint(0,10) + abs(np.random.randn())
            if stop_time>0:
                print('Stopping at bus stop %d at time %d' % (i, simpy_environment.now))
            else:
                print('No one stopping at bus stop %d.')
            yield simpy_environment.timeout(stop_time)

# blue route has 38 stops before it "restarts it's route"
# red also has 38
# green route has 34 bus stops
# most stops are 1-2 minutes apart, because they're so close

def car(env):
    while True:
        print('Start parking at %d' % env.now)
        parking_duration = 5
        yield env.timeout(parking_duration)
        
        print('Start driving at %d' % env.now)
        trip_duration = 2
        yield env.timeout(trip_duration)

def car2(env, name, bcs, driving_time, charge_duration):
    # Simulate driving to the BCS
    yield env.timeout(driving_time)
    # Request one of its charging spots
    print('%s arriving at %d' % (name, env.now))
    with bcs.request() as req:
        yield req
        # Charge the battery
        print('%s starting to charge at %s' % (name, env.now))
        yield env.timeout(charge_duration)
        print('%s leaving the bcs at %s' % (name, env.now))
            

####################### Code #################################################

r.seed(11)
np.random.seed(1)
env = s.Environment() #create the SimPy environment
env.process(bus_improved(env) ) # create an instance of the Bus process
env.run()


# first example
env = s.Environment()
env.process(car(env))
env.run(until=15)

#second example
env = s.Environment()
bcs = s.Resource(env, capacity=2)
for i in range(4):
    env.process(car2(env, 'Car %d' % i, bcs, i*2, 5))
env.run()





np.random.seed(1)
n=36
# timeInts = [2 for _ in range(n)] #if deterministic
driveInts = [1+np.random.poisson(1) for _ in range(n)] #Poisson noise
passBoard = [1 for _ in range(n)] # deterministic passengers
# passBoard = [np.random.poisson(1) for _ in range(n)] #Poisson random passengers
passExit = [1 for _ in range(n)] #deterministic offramp
# passExit = [np.random.poisson(1) for _ in range(n)] #Poisson random offramp

def bus1(env, name):
    driveTimes = driveInts
    for i in range(n):
        print('%s to stop %d at time %d' % (name,i, env.now))
        yield env.timeout(driveTimes[i])
        if passBoard[i]==0 and passExit[i]==0:
            print('No one at bus stop %d, continuing to drive.' % i+1)
        else:
            print('Stopping at bus stop %d at time %d' % (i+1, env.now))
        yield env.timeout(0)

env=s.Environment()
for i in range(1):
    env.process(bus1(env,'Bus %d' %(i+1)))
env.run()

s.Resource()