import sys
sys.stdin = open("calculation_in.txt")

from collections import deque

# def calc(num):
#     global ans
#     if num <= 0 and used[num] == 1:
#         return
#     if num == M:
#         return

T = int(input())
for tc in range(1, T+1):
    N, M = map(int, input().split())

    q = deque()
    used = [0] * 1000001

    q.append((N, 0))
    used[N] = 1
    ans = float('inf')

    while q:
        cur, cnt = q.popleft()
        if cur == M:
            ans = min(ans, cnt)
            break

        for next in [cur+1, cur-1, cur*2, cur-10]:
            if 1 <= next <= 1000000 and used[next] == 0:
                used[next] = 1
                q.append((next, cnt + 1))

    print(f'#{tc} {ans}')