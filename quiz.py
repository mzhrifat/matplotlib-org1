"""
t=int(input())
for _ in range(t):
n,c,q=map(int,input().split())
s=input
for _ in range(c):
l,r=map(int,input().split())
s+ = s[l-1 : r]

for _ in range(q):
k=int(input())

print (S[k-1])
"""
"""connecting a nation"""

def find (parent,x);
    if parent[x]!=x:
        parent[x]=find(parent,parent[x])
        return parent[x]
def union(parent,x,y):
    x_root=find(parent,x)
    y_root = find(parent,y)

if x_root!=y_root;
    parent[x_root]=y_root
n,m=map(int,input().split())
parent=[i for i in range(n+1)]

for _in range(m):
    u,v = map(inr,input().split())

