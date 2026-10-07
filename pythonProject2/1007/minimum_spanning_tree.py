# 최소 신장 트리 (Prim or Kruskal)
import sys; sys.stdin = open("minimum_spanning_tree_in.txt")

# 강사님 풀이
import heapq

def prim(v):
    # 1. 시작점 셋팅 (pq에 push, 가중치도 0)
    pq = []
    D[v] = 0
    total = 0
    heapq.heappush(pq, (D[v], v))  # 가중치, 정점
    # 2. PQ가 비어있지 않은 동안
    while pq:
        # 3. 가중치 최소값 찾기
        weight, v = heapq.heappop(pq)
        # 4. 방문처리 + 가중치합 계산하기
        if visited[v] == 1: continue
        visited[v] = 1
        total += weight
        # 5. 인접한 정점의 가중치 갱신
        for w, wt in adj_lst[v]:
            if visited[w] == 0 and wt < D[w]:
                D[w] = wt
                heapq.heappush(pq, (D[w], w))
    return total

INF = float('inf')
T = int(input())
for tc in range(1, T+1):
    V, E = map(int, input().split())
    adj_lst = [[] for _ in range(V+1)]  # 인접리스트
    visited = [0] * (V+1)               # 방문체크
    D = [INF] * (V+1)                   # 가중치
    for i in range(E):
        s, e, w = map(int, input().split())
        adj_lst[s].append((e, w))
        adj_lst[e].append((s, w))

    print(f'#{tc} {prim(0)}')