import sys
sys.stdin = open("pascal_input.txt")

arr = [[0]*10 for _ in range(10)]

for i in range(10):
    for j in range(10):
        if i==0 and i==j:
            arr[i][j] = 1
        else:
            arr[i][j] = arr[i-1][j] + arr[i-1][j-1]


# # 강사님 풀이
# SIZE = 100
# memo = [[0] * SIZE for _ in range(SIZE)]
# for i in range(SIZE):
#     for j in range(i+1):
#         if j == 0 or i == j:
#             memo[i][j] = 1
#         else:
#             memo[i][j] = memo[i-1][j-1] + memo[i-1][j]  # 점화식


T = int(input())
for tc in range(1, T+1):
    N = int(input())

    print(f'#{tc}')
    for i in range(N):
        for j in range(N):
            if arr[i][j] != 0:
                print(arr[i][j], end=' ')
        print()


# # 강사님 풀이
#     for i in range(N):
#         for j in range(i+1):
#             print(f'{memo[i][j]}', end=' ')
#         print()