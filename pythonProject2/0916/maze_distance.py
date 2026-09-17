import sys
sys.stdin = open("maze_distance_input.txt")

def find_s(arr, N):
    for i in range(N):
        for j in range(N):
            if arr[i][j] == 2:
                return i, j

def bfs(i, j, N):
    visited = [[0]*N for _ in range(N)]
    q = [(i, j)]
    visited[i][j] = 1
    while q:
        ti, tj = q.pop(0)
        if arr[ti][tj] == 3:
            return visited[ti][tj] - 2
        for di, dj in [[0,1], [1,0], [0,-1], [-1,0]]:
            ni, nj = ti + di, tj + dj
            if 0 <= ni < N and 0 <= nj < N and arr[ni][nj] != 1 and visited[ni][nj] == 0:
                q.append([ni, nj])
                visited[ni][nj] = visited[ti][tj] + 1
    return 0

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input())) for _ in range(N)]

    si, sj = find_s(arr, N)
    ans = bfs(si, sj, N)
    print(f'#{tc} {ans}')

####################################################################################################