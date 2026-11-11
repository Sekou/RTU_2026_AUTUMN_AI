import numpy as np
import matplotlib.pyplot as plt

NBINS=20
objects = np.zeros(NBINS)
# objects[4], objects[9], objects[17]=1, 1, 1
objects[7], objects[14], objects[17]=1, 1, 1
belief = np.zeros(NBINS)+1/NBINS

def printArray(name, array):
    print(name)
    print([round(v ,3) for v in array])

def gaussian(x, mu, sig):
    return 1 / (np.sqrt(2 * np.pi) * sig) * np.exp(-np.power((x - mu) / sig, 2) / 2)

def getSingleMeasurementDistribution(x, nbins):
    res=np.zeros(nbins)
    for i in range(len(res)):
        res[i]=gaussian(i, x, 1)
    return res

def senseAllObjects(robot_x, nbins):
    ii=[i for i,v in enumerate(objects) if v==1]
    pSenseFull=sum(getSingleMeasurementDistribution(i, nbins) for i in ii)
    if objects[robot_x]>0:#UPD
        for x in range(nbins):
            belief[x]*=pSenseFull[x]
    print("before", belief)
    #забывание
    #for i in range(len(belief)): belief[i]*=0.9
    print("after", belief)

def shiftBeliefDistribution(speed, nbins):
    shifted = np.zeros(nbins)
    for x in range(len(shifted)):
        shifted[x] = belief[max(0, min(nbins - 1, x - speed))]
    for x in range(nbins):
        belief[x]=shifted[x] #UPD

def normalize():
    global belief
    s=np.sum(belief)
    belief=[v/s for v in belief]

robot_x=0 #начальная координата робота

for i in range(20):
    # SENSE
    senseAllObjects(robot_x, NBINS)
    normalize()
    printArray("Location probability (sensed): ", belief)
    plt.plot(belief)
    plt.savefig(f'img/{i}a.png')
    plt.clf()

    # ACT
    speed=1
    robot_x=min(len(objects)-1, robot_x+speed)

    # UPDATE
    shiftBeliefDistribution(speed, NBINS)
    normalize()
    printArray("Location probability (moved): ", belief)
    plt.plot(belief)
    plt.savefig(f'img/{i}b.png')
    plt.clf()