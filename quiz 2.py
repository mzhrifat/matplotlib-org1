def count_ways(n, cursed):
    def solve(r):
        if r == n:
            return 1
        total = 0
        for c in range(n):
            if (r, c) in cursed or c in cols or (r + c) in d1 or (r - c) in d2:
                continue
            cols.add(c)
            d1.add(r + c)
            d2.add(r - c)
            total += solve(r + 1)
            cols.remove(c)
            d1.remove(r + c)
            d2.remove(r - c)
        return total

    cols, d1, d2 = set(), set(), set()
    return solve(0)

# Input part
n, m = map(int, input().split())
cursed = set()
for _ in range(m):
    x, y = map(int, input().split())
    cursed.add((x, y))

print(count_ways(n, cursed))
