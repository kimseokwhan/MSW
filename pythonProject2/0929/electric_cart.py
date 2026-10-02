import sys
sys.stdin = open("electric_cart_input.txt")
# TSP (외판원 문제)

















































# # 강사님 풀이
# def perm(lev, cursum):
#     global ans
#     if ans < cursum: return         # 가지치기
#     if lev == N:
#         cursum += arr[path[N-1]][path[N]]       # cursum 0->1->2->3 까지만 포함됨
#         if ans > cursum: ans = cursum
#         return
#     for i in range(N):
#         if used[i]: continue
#         path[lev] = i
#         used[i] = 1
#         perm(lev + 1, cursum + arr[path[lev-1]][path[lev]])
#         used[i] = 0
#
# T = int(input())
# for tc in range(1, T+1):
#     N = int(input())
#     arr = [list(map(int, input().split())) for _ in range(N)]
#     path = [0] * N + [0]        # 0 1 2 3 0 으로 저장(출발, 도착 고정)
#     used = [0] * N
#     used[0] = 1     # 0번은 제외
#     ans = float('inf')
#     perm(1, 0)         # 0번은 제외
#     print(f'#{tc} {ans}')



# # 강사님 순열 연습
# def perm(lev):
#     if lev == 3:
#         print(*path)
#         return
#     for i in range(N):
#         if used[i]: continue
#         # path[lev] = arr[i]
#         path.append(arr[i])
#         used[i] = 1
#         perm(lev + 1)
#         used[i] = 0
#         path.pop()
#
# arr = [10, 20, 30]
# N = len(arr)
# used = [0] * N
# # path = [0] * N
# path = []
# perm(0)

# def perm(lev):
#     if lev == N:
#         print(*path)
#         return
#     for i in range(N):
#         if used[i]: continue
#         path[lev] = arr[i]
#         used[i] = 1
#         perm(lev + 1)
#         used[i] = 0
#
# arr = [0, 1, 2, 3]
# N = len(arr)
# path = [0] * N + [0]
# used = [0] * N
# used[0] = 1
# perm(1)