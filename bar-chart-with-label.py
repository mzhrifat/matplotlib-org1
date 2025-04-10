"""
import matplotlib.pyplot as plt
import numpy as np

animal_names = ['Lion', 'Gazelle', 'Cheetah']
mph_speed = [50, 60, 75]

fig, ax = plt.subplots()
bar_container = ax.bar(animal_names, mph_speed)
ax.set(ylabel='speed in MPH', title='Running speeds', ylim=(0, 80))
ax.bar_label(bar_container, fmt=lambda x: f'{x * 1.61:.1f} km/h')

plt.show()
"""

#bar chart with labels

import matplotlib.pyplot as plt
import numpy as np

species=('Adelie','Chinstrap','Gentoo')
sex_counts ={
    'Male':np.array([73,34,61]),
    'Female':np.array([72,34,58]),
}
width=0.6

fig,ax=plt.subplots()
bottom=np.zeros(3)

for sex,sex_count in sex_counts.items():
    p=ax.bar(species,sex_count,width,label=sex,bottom=bottom)
    bottom+=sex_count
    ax.bar_label(p,label_type='center')

ax.set_title('Number of penguins by sex')
ax.legend()
plt.show()