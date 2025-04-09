import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import xticks

#make data
x=[1,1,2,2]
y=[1,2,1,2]
z=[0,0,0,0]
dx=np.ones_like(x)*0.5
dy=np.ones_like(y)*0.5
dz=[2,3,1,4]

#plot
fig,ax=plt.subplots(subplot_kw={"projection":"3d"})
ax.bar3d(x,y,z,dx,dy,dz)

ax.set(xticklabels=[],
       yticklabels=[],
       zticklabels=[])

plt.show()



