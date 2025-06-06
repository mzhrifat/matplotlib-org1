import matplotlib.pyplot as plt
from IPython.core.pylabtools import figsize
"""
data={'apple':10,'orange':15,'lemon':5,'lime':20}
names=list(data.keys())
values=list(data.values())

fig,axs=plt.subplots(1,3,figsize=(9,3),sharey=True)
axs[0].bar(names,values)
axs[1].scatter(names,values)
axs[2].plot(names,values)
fig.suptitle('Categorial Plotting')
"""
cat=["bored","happy","bored","bored","happy","bored"]
dog=["happy","happy","happy","happy","bored","bored"]
activity=["combining","drinking","feeding","napping","playing","washing"]

fig,ax=plt.subplots()
ax.plot(activity,dog,label="dog")
ax.plot(activity,cat,label="cat")
plt.legend()
plt.show()