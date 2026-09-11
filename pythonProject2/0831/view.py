import sys
sys.stdin = open("view_input.txt", "r")

T = 10
# 여러개의 테스트 케이스가 주어지므로, 각각을 처리합니다.
for tc in range(1, T + 1):
    N = int(input())
    arr = list(map(int, input().split()))

    total = 0
    for i in range(2, N-2):
        max_v = 0
        for j in range(5):
            if j != 2:
                if max_v < arr[i-2+j]:
                    max_v = arr[i-2+j]
        if arr[i] > max_v:
            total += arr[i] - max_v


    print(f'#{tc} {total}')


# # 강사님 풀이
#     ans = 0
#     for i in range(2, N-2):
#         max_v = 0
#         # i-2, i-1, i+1, i+2 위치의 최대값
#         for j in range(5):
#             if j != 2:
#                 if max_v < arr[i-2+j]:
#                     max_v = arr[i-2+j]
#         # 좌우2개의 최대값보다 기본값이 더 큰 경우
#         if arr[i] > max_v:
#             ans += arr[i] - max_v
#
#     print(f'#{tc} {ans}')