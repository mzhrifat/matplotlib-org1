def max_plants(N, C, w):
    dp0, dp1 = 0, 0
    water0, water1 = 0, w[0] if w[0] <= C else float('inf')

    for i in range(1, N):
        ndp0 = max(dp0, dp1)
        nwater0 = min(water0, water1)

        if water0 + w[i] <= C:
            ndp1 = dp0 + 1
            nwater1 = water0 + w[i]
        else:
            ndp1 = -1e9
            nwater1 = float('inf')

        dp0, dp1 = ndp0, ndp1
        water0, water1 = nwater0, nwater1

    return max(dp0, dp1)

# ইনপুট
N = 4
C = 10
W = [2, 3, 4, 5]

# ফাংশন কল
print(max_plants(N, C, W))
