import matplotlib.pyplot as plt
import numpy as np

# সরাসরি imread ব্যবহার
im = plt.imread("rounded_profile.png")

fig, ax = plt.subplots()

np.random.seed(19680801)
x = np.arange(30)
y = x + np.random.randn(30)

ax.bar(x, y, color='#6bbc6b')
ax.grid()

# figure-এ ইমেজ বসানো
fig.figimage(im, 25, 25, zorder=3, alpha=.7)

plt.show()
