import matplotlib.pyplot as plt
import numpy as np

#data is a sequence of (start,duration) tuples

cpu_1=[(0,3),(3.5,1),(5,5)]
cpu_2=np.column_stack([np.linspace(0,9,10),np.full(10,0.5)])
cpu_3=np.column_stack([10*np.random.random(61),np.full(61,0.05)])
cpu_4=[(2,1.7),(7,1.2)]
disk=[(1,1.5)]
network= np.column_stack([10*np.random(10),np.full(10,0.005)])
