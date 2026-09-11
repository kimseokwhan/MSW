import sys
sys.stdin = open("maze_input.txt")

def maze(r, c):
    global flag
    if arr[r][c] == 3:
        flag = 1

    visited[r][c] = 1

    for i in range(4):
        nr = r + dr[i]
        nc = c + dc[i]
        if 0 <= nr < N and 0 <= nc < N:
            if visited[nr][nc] == 0:
                if arr[nr][nc] == 0 or arr[nr][nc] == 3:
                    maze(nr, nc)

def start_position(arr):
    for i in range(N):
        for j in range(N):
            if arr[i][j] == 2:
                return i, j

dr = [0, 1, 0, -1]
dc = [1, 0, -1, 0]


# # 강사님 풀이
# def start_pos(arr):
#     for i in range(N):
#         for j in range(N):
#             if arr[i][j] == 2:
#                 return i, j
#
# def dfs(r, c):
#     # 가지치기
#     global flag
#     if arr[r][c] == 3:
#         flag = 1
#         return
#     # 1. 방문체크
#     visited[r][c] = 1
#     # 2. 인접한 정점(w)이 미방문 -> dfs
#     for i in range(4):
#         nr = r + dr[i]
#         nc = c + dc[i]
#         if 0 <= nr < N and 0 <= nc < N \
#             and visited[nr][nc] == 0 \
#             and (arr[nr][nc] == 0 or arr[nr][nc] ==3):
#             dfs(nr, nc)


T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input())) for _ in range(N)]

    visited = [[0] * N for _ in range(N)]

    flag = 0
    r, c = start_position(arr)
    maze(r, c)
    print(f'#{tc} {flag}')


# # 강사님 풀이
#     # 출발점 좌표 찾기
#     r, c = start_pos(arr)
#     flag = 0
#     dfs(r, c)
#     print(f'#{tc} {flag}')