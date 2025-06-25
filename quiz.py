t=int(input())
for _in range(t):
n,c,q=map(int,input().split())
s=input
for _in range(c):
l,r=map(int,input().split())
s+ = s[l-1 : r]

for _in range(q):
k=int(input())
print (s[k-1])