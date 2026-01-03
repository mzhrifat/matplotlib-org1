"""
#Empty list
x=[]
#list with initial value
y=[1,2,3,4]

#List with mix data
z=[1,True,"Hello",3.14]

print(x)
print(y)
print(z)

#2
x=[4,3,24,1,34]
#Add element

x.append(100)
#sort list ascending
x.sort()
print(x)
"""

#3
my_array = [7,3,5,67,8]
minVal=my_array[0]

for i in my_array:
    if i < minVal:
        minVal=i

print('Lowest value:',minVal)