import sys; sys.stdin = open("오목판정_in.txt")

def omok(r, c, cnt, k):     # 오목 맞는지 판단
    global ans
    if cnt == 5:
        ans = 1
        return
    cnt += 1
    nr = r + dr[k]
    nc = c + dc[k]
    if 0 <= nr < N and 0 <= nc < N and arr[nr][nc] == 'o':
        omok(nr, nc, cnt, k)

# dr = [-1, -1, -1, 0, 0, 0, 1, 1, 1]
# dc = [-1, 0, 1, -1, 0, 1, -1, 0, 1]
dr = [0, 1, 1, 1]
dc = [1, -1, 0, 1]

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(str, input())) for _ in range(N)]

    ans = 0
    for i in range(N):          # 오목판 순회, 돌 찾기
        for j in range(N):
            if arr[i][j] == 'o':
                for k in range(4):      # 다음 돌 방향 찾기
                    nr = i + dr[k]
                    nc = j + dc[k]
                    if 0 <= nr < N and 0 <= nc < N and arr[nr][nc] == 'o':
                        omok(nr, nc, 2, k)

    if ans == 1:
        print(f"#{tc} YES")
    else:
        print(f"#{tc} NO")