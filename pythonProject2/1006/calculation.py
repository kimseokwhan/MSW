import sys
sys.stdin = open("calculation_in.txt")

# from collections import deque
#
# T = int(input())
# for tc in range(1, T+1):
#     N, M = map(int, input().split())
#
#     q = deque()
#     used = [0] * 1000001
#
#     q.append((N, 0))
#     used[N] = 1
#     ans = float('inf')
#
#     while q:
#         cur, cnt = q.popleft()
#         if cur == M:
#             ans = min(ans, cnt)
#             break
#
#         for next in [cur+1, cur-1, cur*2, cur-10]:
#             if 1 <= next <= 1000000 and used[next] == 0:
#                 used[next] = 1
#                 q.append((next, cnt + 1))
#
#     print(f'#{tc} {ans}')


# 강사님 풀이
def bfs(v):
    # 인큐 + 방문체크
    Q = [v]
    visited[v] = 1
    # 큐가 비어있지 않으면
    while Q:
        # v = 디큐
        v = Q.pop(0)
        # 할일
        if v == M:
            return visited[v] - 1
        # v에 인접정점(w)중 미방문 & 백만이하 자연수
        for w in [v+1, v-1, v*2, v-10]:
            if 0 < w <= 1_000_000:
                if visited[w] == 0:
                    # 인큐 + 방문체크
                    Q.append(w)
                    visited[w] = visited[v] + 1

T = int(input())
for tc in range(1, T+1):
    N, M = map(int, input().split())
    visited = [0] * (1_000_000 + 1)
    print(f'#{tc} {bfs(N)}')

# # 강사님 풀이 (덱 deque)
# from collections import deque
# def bfs(v):
#     # 인큐 + 방문체크
#     Q = deque([v])
#     visited[v] = 1
#     # 큐가 비어있지 않으면
#     while Q:
#         # v = 디큐
#         v = Q.popleft()
#         # 할일
#         if v == M:
#             return visited[v] - 1
#         # v에 인접정점(w)중 미방문 & 백만이하 자연수
#         for w in [v+1, v-1, v*2, v-10]:
#             if 0 < w <= 1_000_000:
#                 if visited[w] == 0:
#                     # 인큐 + 방문체크
#                     Q.append(w)
#                     visited[w] = visited[v] + 1
#
# T = int(input())
# for tc in range(1, T+1):
#     N, M = map(int, input().split())
#     visited = [0] * (1_000_000 + 1)
#     print(f'#{tc} {bfs(N)}')