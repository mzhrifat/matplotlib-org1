n = int(input())
flowers = list(map(int, input().split()))

mx = max(flowers)
mn = min(flowers)

if mx == mn:
    ways = n * (n - 1) // 2
    print(0, ways)
else:
    print(mx - mn, flowers.count(mx) * flowers.count(mn))
