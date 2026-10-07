import sys
sys.stdin = open("path_number_in.txt")




# 강사님 풀이
def dfs(v):
    global ans
    # 방문체크 + 할일
    visited[v] = 1
    if v == G:
        ans += 1
        return
    # v에 인접한 미방문 정점(w)에 대해서 반복 -> dfs(w)
    for w in adj_lst[v]:
        if visited[w] == 0:
            dfs(w)
            visited[w] = 0  # 다른 경로로 가기위해 풀어줘야 한다.

T = int(input())
for tc in range(1, T+1):
    V, E = map(int, input().split())
    temp = list(map(int, input().split()))
    adj_lst = [[] for _ in range(V+1)]
    visited = [0] * (V+1)
    for i in range(E):
        s, e = temp[i*2], temp[i*2+1]
        adj_lst[s].append(e)
    S, G = map(int, input().split())

    ans = 0
    dfs(S)
    print(f'#{tc} {ans}')