import sys
sys.stdin = open("minimum_cost_input.txt")




# 강사님 풀이
def perm(lev, cursum):
    global ans
    if ans <= cursum: return
    if lev == N:
        ans = min(ans, cursum)
        return
    for i in range(N):
        if used[i]: continue
        used[i] = 1
        # path.append(arr[lev][i])
        # perm(lev + 1, cursum + path[lev])
        perm(lev + 1, cursum + arr[lev][i])
        # path.pop()
        used[i] = 0

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    used = [0] * N
    # path = []
    ans = float('inf')
    perm(0, 0)
    print(f'#{tc} {ans}')