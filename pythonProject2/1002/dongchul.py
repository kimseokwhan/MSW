import sys
sys.stdin = open("dongchul_input.txt")




# 강사님 풀이
def perm(lev, curmax):
    global ans
    if ans >= curmax: return
    if lev == N:
        ans = max(ans, curmax)
        return
    for i in range(N):
        if used[i]: continue
        used[i] = True
        path.append(arr[lev][i] / 100)
        perm(lev + 1, curmax * path[lev])
        path.pop()
        used[i] = False

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]
    used = [False] * N
    path = []
    ans = 0
    perm(0, 1)
    print(f'#{tc} {ans*100:.6f}')