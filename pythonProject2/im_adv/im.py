import sys; sys.stdin = open("im_in.txt")

T = int(input())
for tc in range(1, T+1):
    N, K = map(int, input().split())
    arr = list(map(int, input().split()))

    for i in range(K):
        max_top = -float('inf')
        min_top = float('inf')
        for j in range(N):
            if arr[j] > max_top:
                max_top = arr[j]
                max_top_idx = j
            if arr[j] < min_top:
                min_top = arr[j]
                min_top_idx = j
        arr[max_top_idx] -= 1
        arr[min_top_idx] += 1

    ans = max(arr) - min(arr)

    print(f'#{tc} {ans}')