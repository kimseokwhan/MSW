import sys
sys.stdin = open("graph_path_input.txt")

def dfs(S):
    global flag
    visited[S] = 1
    if S == G:
        flag = 1
        return
    for w in adj[S]:
        if visited[w] == 0:
            dfs(w)

# # 강사님 풀이
# def dfs(S):
#     # 1. 방문 체크
#     visited[S] = 1
#     # 2. v에 인접정점(w)가 미방문
#     for w in adj[S]:
#         if visited[w] == 0:
#             dfs(w)

T = int(input())
for tc in range(1, T+1):
    V, E = map(int, input().split())
    # adj = [list(map(int, input().split())) for _ in range(E)]     # 이렇게 받으면 인접리스트 ㄴㄴ
    adj = [[] for _ in range(V+1)]
    for i in range(E):
        s, e = map(int, input().split())
        adj[s].append(e)
    S, G = map(int, input().split())

    # print(V, E)
    # print(adj)
    # print(S, G)

    visited = [0] * (V+1)

    # 강사님 풀이(flag 사용(가지치기))
    flag = 0
    dfs(S)
    # print(f'#{tc} {visited[G]}')
    print(f'#{tc} {flag}')