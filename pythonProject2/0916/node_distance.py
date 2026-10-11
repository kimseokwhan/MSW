import sys; sys.stdin = open("node_distance_input.txt")

def find_G(cur, cnt):
    global min_dis
    if min_dis <= cnt:   # 가지치기
        return
    if cur == G:    # Goal 도착 시 최소 거리 구하기
        min_dis = min(min_dis, cnt)
        return
    visited[cur] = 1
    for i in range(len(Ei[cur])):       # 이어진 노드들 방문
        if visited[Ei[cur][i]] == 0:
            find_G(Ei[cur][i], cnt + 1)
    visited[cur] = 0

T = int(input())
for tc in range(1, T+1):
    V, E = map(int, input().split())
    Ei = [[] for _ in range(V + 1)]     # 이어진 노드를 리스트로 관리
    for i in range(E):
        a, b = map(int, input().split())
        Ei[a].append(b)
        Ei[b].append(a)
    S, G = map(int, input().split())

    visited = [0] * (V + 1)     # 방문체크
    min_dis = float('inf')      # 최소 거리
    find_G(S, 0)
    if min_dis == float('inf'):     # Goal 못감
        min_dis = 0
    print(f'#{tc} {min_dis}')