import sys
sys.stdin = open("gravity_input.txt", "r")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = list(map(int, input().split()))

    max_v = 0
    for i in range(N):
        # cnt = N - (i + 1)
        cnt = 0
        for j in range(i+1, N):
            # if arr[i] <= arr[j]:
            #     cnt -= 1
            if arr[i] > arr[j]:
                cnt += 1
        if max_v < cnt:
            max_v = cnt

    print(f'#{tc} {max_v}')


# # 강사님 풀이
#     ans = 0
#     for i in range(N):  # i 보다 작은 값 세기
#         cnt = 0
#         for j in range(i+1, N):
#             if arr[i] > arr[j]:
#                 cnt += 1
#         # cnt의 최대값
#         if ans < cnt:
#             ans = cnt
#     print(f'#{tc} {ans}')