import sys; sys.stdin = open("container_transport_input.txt")

# T = int(input())
# for tc in range(1, T+1):
#     N, M = map(int, input().split())
#     w = list(map(int, input().split()))
#     t = list(map(int, input().split()))
#
#     w.sort(reverse=True)
#     t.sort(reverse=True)
#     w_used = [0] * N
#     t_used = [0] * M
#
#     ans = 0
#
#     for i in range(N):
#         for j in range(M):
#             if w[i] <= t[j] and w_used[i] == 0 and t_used[j] == 0:
#                 ans += w[i]
#                 w_used[i] = 1
#                 t_used[j] = 1
#                 break
#
#     print(f'#{tc} {ans}')


# 강사님 풀이
T = int(input())
for tc in range(1, T+1):
    N, M = map(int, input().split())
    wi = list(map(int, input().split()))
    ti = list(map(int, input().split()))

    wi.sort(reverse=True)
    ti.sort(reverse=True)

    i = j = ans = 0
    while i < N and j < M:
        # 운반가능
        if wi[i] <= ti[j]:
            ans += wi[i]
            i += 1
            j += 1
        else:
            i += 1  # 컨터이너의 포인터만 증가

    print(f'#{tc} {ans}')