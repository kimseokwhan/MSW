import sys
sys.stdin = open("minimum_sum_array_input.txt")

def perm(lev, cursum):
    global sum_arr
    global min_v
    if min_v < cursum:
        return
    if lev == N:
        # print(f'#{tc} {cursum}')
        sum_arr.append(cursum)
    else:
        for i in range(lev, N):
            arr[lev], arr[i] = arr[i], arr[lev]
            perm(lev+1, cursum + arr[lev][path[lev]])
            arr[lev], arr[i] = arr[i], arr[lev]

# # 강사님 풀이
# def perm(lev, cursum):
#     global ans
#     if ans < cursum:
#         return
#     if lev == N:
#         if ans > cursum:
#             ans = cursum
#     else:
#         for i in range(lev, N):
#             path[i], path[lev] = path[lev], path[i]
#             perm(lev + 1, cursum + arr[lev][path[lev]])
#             path[i], path[lev] = path[lev], path[i]

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    path = [i for i in range(N)]
    sum_arr = []
    min_v = min(sum_arr)

    perm(0, 0)
    print(f'#{tc} {min_v}')

# # 강사님 풀이
#     path = list(range(N))
#     ans = float('inf')
#     perm(0, 0)
#     print(f'#{tc} {ans}')