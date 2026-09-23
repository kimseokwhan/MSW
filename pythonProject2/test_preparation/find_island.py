import sys; sys.stdin = open("find_island_input.txt")

def bfs(arr):
    pass


T = int(input())
for tc in range(1, T+1):
    N, M = map(int, input().split())
    arr = [list(map(str, input())) for _ in range(N)]

    ans = bfs(arr)
    print(f'#{tc} {ans}')