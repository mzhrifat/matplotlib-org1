import matplotlib.pyplot as plt
import matplotlib.cbook as cbook
import matplotlib.patches as patches

with cbook.get_sample_data('grace_hopper.jpg')as image_file:
    image=plt.imread(image_file)

fig,ax =plt.subplots()
im=ax.imshow(image)
patch=patches.Circle((260,200), radius=200, transform=ax.transData)
im.set clip path(path)
ax.axis('off')
plt.show()