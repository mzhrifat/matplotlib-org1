from collections import deque

def can_send_data(graph, u, v, d, n):
    visited = [False] * (n + 1)
    queue = deque([u])
    visited[u] = True

    while queue:
        node = queue.popleft()
        if node == v:
            return True
        for neighbor, capacity in graph[node]:
            if not visited[neighbor] and capacity >= d:
                visited[neighbor] = True
                queue.append(neighbor)
    return False

# Input
n, m, q = map(int, input().split())
graph = [[] for _ in range(n + 1)]

for _ in range(m):
    u, v, c = map(int, input().split())
    graph[u].append((v, c))
    graph[v].append((u, c))

for _ in range(q):
    u, v, d = map(int, input().split())
    result = can_send_data(graph, u, v, d, n)
    print("Yes" if result else "No")
