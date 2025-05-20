n = 5
k = 3
A = [1, 2, -3, 4, 5]


def max_treasure(n, k, A):
    max_sum = float('-inf')
    curr_sum = 0
    start = 0

    for end in range(n):
        curr_sum += A[end]
        if end - start + 1 > k:
            curr_sum -= A[start]
            start += 1
        if end - start + 1 == k:
            max_sum = max(max_sum, curr_sum)

    return max_sum


print(max_treasure(n, k, A))

