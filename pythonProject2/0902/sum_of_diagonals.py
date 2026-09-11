import sys
sys.stdin = open("sum_of_diagonals_input.txt")

T = int(input())
for tc in range(1, T+1):
    N = int(input())
    arr = [list(map(int, input().split())) for _ in range(N)]

    total = 0
    for i in range(N):
        for j in range(N):
            if i == j:
                total += arr[i][j]
            if i + j == 4:
                total += arr[i][j]
    total -= arr[N//2][N//2]

    # for i in range(N):
    #     total += arr[i][i] + arr[i][N-1-i]
    # if N%2:
    #     total -= arr[N//2][N//2]

    print(f'#{tc} {total}')