import sys
sys.stdin = open("repel_fly_input.txt", "r")

T = int(input())
# 여러개의 테스트 케이스가 주어지므로, 각각을 처리합니다.
for tc in range(1, T + 1):
    N, M = map(int, input().split())
    arr = [list(map(int, input().split())) for _ in range(N)]

    max_v = 0
    for i in range(N-M+1):
        for j in range(N-M+1):
            sum_v = 0
            for little_i in range(M):
                for little_j in range(M):
                    sum_v += arr[i+little_i][j+little_j]
            if max_v < sum_v:
                max_v = sum_v

    print(f'#{tc} {max_v}')

# # 강사님 풀이
#     max_v = 0
#     # 시작점을 순회
#     for r in range(N-M+1):
#         for c in range(N-M+1):
#             # 작은 직사각형(파리채) 순회
#             sum_v = 0
#             for i in range(M):
#                 for j in range(M):
#                     sum_v += arr[r+i][c+j]
#             if max_v < sum_v:
#                 max_v = sum_v
#     print(f'#{tc} {max_v}')