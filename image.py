#
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ছবি পড়া
image = plt.imread('rsz_img_2881.jpg')

fig, ax = plt.subplots()
im = ax.imshow(image)

# বৃত্তাকার ক্লিপ
patch = patches.Circle((60, 60), radius=200, transform=ax.transData)
im.set_clip_path(patch)

ax.axis('off')
plt.show()
#
