__author__ = 'bradford_bazemore'
import random
import matplotlib.pyplot as plt
import scipy.stats as st
ProbDist = (0.40, 0.30, 0.15, 0.15)
data=[]
# assume sum of bias is 1
def roll(massDist):
    randRoll = random.random() # in [0,1)
    sum = 0
    result = 1
    for mass in massDist:
        sum += mass
        if randRoll < sum:
            return result
        result+=1

for i in range(0,100):
    data.append(roll(ProbDist))
plt.hist(data)
plt.show()
print st.f_oneway([1,2,3,4,5],[2,3,4,5,6],[1,1,1,1,1])
