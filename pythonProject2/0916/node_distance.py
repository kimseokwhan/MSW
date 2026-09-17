import sys;sys.stdin = open("node_distance_input.txt")

def bfs(v):
    pass

T = int(input())
for tc in range(1, T+1):
    V, E = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(E)]
    S, G = map(int, input().split())

    print(V, E)
    print(arr)
    print(S, G)