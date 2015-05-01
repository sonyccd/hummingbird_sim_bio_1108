import logging
import sys
import time

__author__ = 'Bradford W. Bazemore'

import random
import matplotlib.pyplot as plt
import simpy
import scipy.stats as st
import numpy as np


'''
f0: sugar in the raw
f1: sugar
f2: Splenda
f3: Equal
'''

RANDOM_SEED = 42
FEEDER_SIZE = 500
DRINK_SPEED = 1
BIRD_INTER = [10, 50]
SIM_TIME = 1700
FEEDER_DATA = [[], [], [], []]
FEEDER_TIMES=[0,0,0,0]
FEEDER_TOTAL_TIMES=[]
FEEDER_FULL_DATA=[]
FEEDER_HITS = [0, 0, 0, 0]
ProbDist = (0.50, 0.30, 0.10, 0.10)


'''the bird simulation thing'''

def bird(env, id, feeder):
    # FEEDER_INDEX = [0, 1, 2, 3]
    waits = 0
    while True:
        #feeder_id = random.sample(FEEDER_INDEX, 1)[0]
        feeder_id = roll(ProbDist)
        with feeder[feeder_id][0].request() as req:
            wait = random.randint(1, 5)
            check = yield req | env.timeout(wait)
            start = env.now
            if req in check:
                waits = 0
                if feeder[feeder_id][1].level == 0:
                    #FEEDER_INDEX.remove(feeder_id)
                    continue
                else:
                    try:
                        food_need = random.randint(1, min(feeder[feeder_id][1].level, 4) + 1)
                        yield feeder[feeder_id][1].get(food_need)
                        FEEDER_HITS[feeder_id] += 1
                    except IndexError:
                        continue
                    yield env.timeout(food_need / DRINK_SPEED)
                    logging.debug('%s finished eating in %.1f seconds.', id, env.now - start)
            else:
                if waits == 5:
                    logging.debug( "EXIT")
                    return
                logging.debug( '%s waits %d',id, waits)
                waits += 1
        yield env.timeout(random.randint(*BIRD_INTER))


'''creates the birds at random time from time range'''


def bird_generator(env, feeder):
    for i in range(0, 50):
        yield env.timeout(random.randint(*BIRD_INTER))
        env.process(bird(env, i, feeder))


'''gathers stats for latter reivew'''


def stats(env, feeder):
    start = env.now
    old_level=0
    while True:
        if (env.now - start) > SIM_TIME:
            env.exit(env)
        else:
            yield env.timeout(100)
        logging.debug( '============================')
        count = 0
        for i in feeder:
            logging.debug( 'Feeder: %s  Level: %d' ,i[2], i[1].level)
            if i[1].level==old_level & FEEDER_TIMES[count]==0:
                FEEDER_TIMES.append(env.now-stat)
            FEEDER_DATA[count].append(i[1].level)
            count = count + 1
        logging.debug( '============================')


'''random number generator with bias'''


def roll(massDist):
    randRoll = random.random()
    sum = 0
    result = 1
    for mass in massDist:
        sum += mass
        if randRoll < sum:
            return result - 1
        result += 1

def reject_outliers(data, m=3):
    d = np.abs(data - np.median(data))
    mdev = np.median(d)
    s = d/mdev if mdev else 0.
    return data[s<m]

'''init the simulation env'''
for c in range(0,1):
    logging.basicConfig(stream=sys.stderr,)
    #random.seed(RANDOM_SEED)
    env = simpy.Environment()
    feeder = []
    for i in range(0, 4):
        feeder.append([simpy.Resource(env, 1), simpy.Container(env, FEEDER_SIZE, init=FEEDER_SIZE), i])
    env.process(bird_generator(env, feeder))
    stat = env.process(stats(env, feeder))
    env.run(until=stat)
    FEEDER_FULL_DATA.append(FEEDER_DATA)
    FEEDER_DATA=[[],[],[],[]]

print FEEDER_FULL_DATA[0][0]


#print st.f_oneway()


plt.figure(1)
plt.plot(FEEDER_DATA[0], label='SIR')
plt.plot(FEEDER_DATA[1], label='Sugar')
plt.plot(FEEDER_DATA[2], label='Splenda')
plt.plot(FEEDER_DATA[3], label='Equal')
plt.title("fluid consumed over time")
plt.ylabel('milliliters')
plt.xlabel('time(100sec)')
plt.legend()
plt.figure(2)
plt.bar(range(FEEDER_HITS.__len__()), FEEDER_HITS, .5)
plt.title("# of hits for each sweetener")
plt.xticks((0, 1, 2, 3), ('SIR', 'Sugar', 'Splend', 'Equal'))
plt.ylabel("#hits")
plt.xlabel("types of sweetener")
plt.show()