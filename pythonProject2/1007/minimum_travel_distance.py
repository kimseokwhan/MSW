# 다익스트라 (Dijkstra)
import sys; sys.stdin = open("minimum_travel_distance_in.txt")

# 강사님 풀이
import heapq

def dijkstra(v):
    # 1. 시작점 셋팅
    pq = []
    D[v] = 0
    heapq.heappush(pq, (D[v], v))    # 가중치, 정점
    # 2. pq가 비어있지 않은 동안
    while pq:
        # 3. 가중치가 최소인 정점 (weight, v)
        weight, v = heapq.heappop(pq)
        # 4. 방문체크 + 하고싶은일 (V에 도착 헀냐?)
        if visited[v] == 1: continue
        visited[v] = 1
        if v == V:
            return D[v]
        # 5. 인접정점 가중치 갱신
        for w in range(V+1):
            if adj_mat[v][w] and visited[w] == 0:
                if D[w] > D[v] + adj_mat[v][w]:
                    D[w] = D[v] + adj_mat[v][w]
                    heapq.heappush(pq, (D[w], w))

T = int(input())
for tc in range(1, T+1):
    V, E = map(int, input().split())
    adj_mat = [[0] * (V+1) for _ in range(V+1)]     # 인접행렬
    visited = [0] * (V+1)                           # 방문체크
    D = [float('inf')] * (V+1)                      # 가중치
    for i in range(E):
        s, e, w = map(int, input().split())
        adj_mat[s][e] = w

    print(f'#{tc} {dijkstra(0)}')