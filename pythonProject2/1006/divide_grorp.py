import sys
sys.stdin = open("divide_grorp_in.txt")

# def findgroup(member):
#     global ans
#     if boss[member] == member:
#         ans += 1
#         return member
#     ret = findboss(boss[member])
#     return ret
#
# def findboss(member):
#     if boss[member] == member:
#         return member
#     ret = findboss(boss[member])
#     return ret
#
# def union(a, b):
#     fa = findboss(a)
#     fb = findboss(b)
#     if fa == fb:
#         return
#     boss[fb] = fa
#
# T = int(input())
# for tc in range(1, T+1):
#     N, M = map(int, input().split())
#     arr = list(map(int, input().split()))
#
#     boss = [i for i in range(N+1)]
#     ans = 0
#     for i in range(0, M*2, 2):
#         union(arr[i], arr[i+1])
#
#     for j in range(len(boss)):
#         findgroup(j)
#
#     # print(boss)
#     print(f'#{tc} {ans-1}')     # boss 배열에서 0 빼야해서 -1


# # 강사님 풀이
# def find_set(x):
#     while parents[x] != x:
#         x = parents[x]
#     return x
#
# T = int(input())
# for tc in range(1, T+1):
#     N, M = map(int, input().split())
#     temp = list(map(int, input().split()))
#     parents = list(range(N+1))      # make-set
#     for i in range(M):
#         s, e = temp[i*2], temp[i*2+1]
#         # union
#         parents[find_set(e)] = find_set(s)
#     cnt = 0
#     for i in range(1, N+1):
#         if parents[i] == i:
#             cnt += 1
#     print(f'#{tc} {cnt}')

# 강사님 풀이 (DFS)
def dfs(v):
    visited[v] = 1
    for w in adj_lst[v]:
        if visited[w] == 0:
            dfs(w)

T = int(input())
for tc in range(1, T + 1):
    N, M = map(int, input().split())
    temp = list(map(int, input().split()))
    adj_lst = [[] for _ in range(N + 1)]  # 인접리스트
    visited = [0] * (N + 1)
    for i in range(M):
        s, e = temp[2 * i], temp[2 * i + 1]
        adj_lst[s].append(e)
        adj_lst[e].append(s)
    cnt = 0
    for i in range(1, N + 1):
        if visited[i] == 0:
            dfs(i)
            cnt += 1
    print(f'#{tc} {cnt}')