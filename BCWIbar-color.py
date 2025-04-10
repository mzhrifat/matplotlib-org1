import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import bar_label, title

fig,ax=plt.subplots()

fruits=['apple','Dates','Cherry','malta']
counts=[40,100,30,55,]
bar_label=['red','blue','green','orange']
bar_colors=['tab:red','tab:blue','tab:green','tab:orange']

ax.bar(fruits,counts,label=bar_label,color=bar_colors)

ax.set_ylabel('Fruits supply')
ax.set_title('Fruit supply by kind and color')
ax.legend(title='Fruit color')

plt.show()