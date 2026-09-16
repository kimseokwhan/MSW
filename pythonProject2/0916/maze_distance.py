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


T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input())) for _ in range(N)]

    si, sj = find_s(arr, N)
    bfs(si, sj, N)